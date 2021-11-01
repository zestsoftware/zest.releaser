import logging
import os
import re
import sys

from zest.releaser import pypi
from zest.releaser import utils

VERSION_PATTERN = re.compile(r"""
^                # Start of line
\s*              # Indentation
version\s*=\s*   # 'version =  ' with possible whitespace
['"]?            # String literal begins
\d               # Some digit, start of version.
""", re.VERBOSE)
UPPERCASE_VERSION_PATTERN = re.compile(r"""
^                # Start of line
VERSION\s*=\s*   # 'VERSION =  ' with possible whitespace
['"]             # String literal begins
\d               # Some digit, start of version.
""", re.VERBOSE)

UNDERSCORED_VERSION_PATTERN = re.compile(r"""
^                    # Start of line
__version__\s*=\s*   # '__version__ =  ' with possible whitespace
['"]                 # String literal begins
\d                   # Some digit, start of version.
""", re.VERBOSE)

TXT_EXTENSIONS = ['rst', 'txt', 'markdown', 'md']

logger = logging.getLogger(__name__)


class BaseVersionControl:
    "Shared implementation between all version control systems"

    internal_filename = ''  # e.g. '.svn' or '.hg'
    setuptools_helper_package = ''

    def __init__(self, reporoot=None):
        self.workingdir = os.getcwd()
        if reporoot is None:
            self.reporoot = self.workingdir
            self.relative_path_in_repo = ''
        else:
            self.reporoot = reporoot
            # Determine relative path from root of repo.
            self.relative_path_in_repo = os.path.relpath(
                self.workingdir, reporoot)
        self.setup_cfg = pypi.SetupConfig()
        pypi_cfg = pypi.PypiConfig()
        self.fallback_encoding = pypi_cfg.encoding()

    def __repr__(self):
        return '<{} at {} {}>'.format(
            self.__class__.__name__, self.reporoot, self.relative_path_in_repo)

    def is_setuptools_helper_package_installed(self):
        try:
            __import__(self.setuptools_helper_package)
        except ImportError:
            return False
        return True

    def get_setup_py_version(self):
        if os.path.exists('setup.py'):
            # First run egg_info, as that may get rid of some warnings
            # that otherwise end up in the extracted version, like
            # UserWarnings.
            utils.execute_command(utils.setup_py('egg_info'))
            version = utils.execute_command(
                utils.setup_py('--version')).splitlines()[0]
            if 'Traceback' in version:
                # Likely cause is for example forgetting to 'import
                # os' when using 'os' in setup.py.
                logger.critical('The setup.py of this package has an error:')
                print(version)
                logger.critical('No version found.')
                sys.exit(1)
            return utils.strip_version(version)

    def get_setup_py_name(self):
        if os.path.exists('setup.py'):
            # First run egg_info, as that may get rid of some warnings
            # that otherwise end up in the extracted name, like
            # UserWarnings.
            utils.execute_command(utils.setup_py('egg_info'))
            return utils.execute_command(utils.setup_py('--name')).strip()

    def get_version_txt_version(self):
        filenames = ['version']
        for extension in TXT_EXTENSIONS:
            filenames.append('.'.join(['version', extension]))
        version_file = self.filefind(filenames)
        if version_file:
            with open(version_file) as f:
                version = f.read()
            return utils.strip_version(version)

    def get_python_file_version(self):
        python_version_file = self.setup_cfg.python_file_with_version()
        if not python_version_file:
            return
        lines, encoding = utils.read_text_file(
            python_version_file,
            fallback_encoding=self.fallback_encoding,
        )
        encoding  # noqa, unused variable
        for line in lines:
            match = UNDERSCORED_VERSION_PATTERN.search(line)
            if match:
                logger.debug("Matching __version__ line found: '%s'", line)
                line = line.lstrip('__version__').strip()
                line = line.lstrip('=').strip()
                line = line.replace('"', '').replace("'", "")
                return utils.strip_version(line)

    def filefind(self, names):
        """Return first found file matching name (case-insensitive).

        Some packages have docs/HISTORY.txt and
        package/name/HISTORY.txt.  We make sure we only return the one
        in the docs directory if no other can be found.

        'names' can be a string or a list of strings; if you have both
        a CHANGES.txt and a docs/HISTORY.txt, you want the top level
        CHANGES.txt to be found first.
        """
        if isinstance(names, str):
            names = [names]
        names = [name.lower() for name in names]
        files = self.list_files()
        found = []
        for fullpath in files:
            if fullpath.lower().endswith('debian/changelog'):
                logger.debug(
                    "Ignoring %s, unreadable (for us) debian changelog",
                    fullpath)
                continue
            filename = os.path.basename(fullpath)
            if filename.lower() in names:
                logger.debug("Found %s", fullpath)
                if not os.path.exists(fullpath):
                    # Strange.  It at least happens in the tests when
                    # we deliberately remove a CHANGES.txt file.
                    logger.warning(
                        "Found file %s in version control but not on "
                        "file execute_command.", fullpath)
                    continue
                found.append(fullpath)
        if not found:
            return
        if len(found) > 1:
            found.sort(key=len)
            logger.warning(
                "Found more than one file, picked the shortest one to "
                "change: %s", ', '.join(found))
        return found[0]

    def history_file(self, location=None):
        """Return history file location.
        """
        if location:
            # Hardcoded location passed from the config file.
            if os.path.exists(location):
                return location
            else:
                logger.warning("The specified history file %s doesn't exist",
                               location)
        filenames = []
        for base in ['CHANGES', 'HISTORY', 'CHANGELOG']:
            filenames.append(base)
            for extension in TXT_EXTENSIONS:
                filenames.append('.'.join([base, extension]))
        history = self.filefind(filenames)
        if history:
            return history

    def tag_exists(self, tag_name):
        """Check if a tag has already been created with the name of the
        version.
        """
        for tag in self.available_tags():
            if tag == tag_name:
                return True
        return False

    def _extract_version(self):
        """Extract the version from setup.py or version.txt.

        If there is a setup.py and it gives back a version that differs
        from version.txt then this version.txt is not the one we should
        use.  This can happen in packages like ZopeSkel that have one or
        more version.txt files that have nothing to do with the version of
        the package itself.

        So when in doubt: use setup.py.

        But if there's an explicitly configured Python file that has to be
        searched for a ``__version__`` attribute, use that one.
        """
        return (self.get_python_file_version() or
                self.get_setup_py_version() or
                self.get_version_txt_version())

    def _update_python_file_version(self, version):
        filename = self.setup_cfg.python_file_with_version()
        lines, encoding = utils.read_text_file(
            filename,
            fallback_encoding=self.fallback_encoding,
        )
        good_version = "__version__ = '%s'" % version
        for index, line in enumerate(lines):
            if UNDERSCORED_VERSION_PATTERN.search(line):
                lines[index] = (
                    good_version.replace("'", '"')
                    if '"' in line
                    else good_version
                )

        contents = '\n'.join(lines)
        utils.write_text_file(filename, contents, encoding)
        logger.info("Set __version__ in %s to '%s'", filename, version)

    def _update_version(self, version):
        """Find out where to change the version and change it.

        There are three places where the version can be defined. The first one
        is an explicitly defined Python file with a ``__version__``
        attribute. The second one is some version.txt that gets read by
        setup.py. The third is directly in setup.py.
        """
        if self.get_python_file_version():
            self._update_python_file_version(version)
            return

        version_filenames = ['version']
        version_filenames.extend([
            '.'.join(['version', extension]) for extension in TXT_EXTENSIONS])
        versionfile = self.filefind(version_filenames)
        if versionfile:
            # We have a version.txt file but does it match the setup.py
            # version (if any)?
            setup_version = self.get_setup_py_version()
            if not setup_version or (setup_version ==
                                     self.get_version_txt_version()):
                with open(versionfile, 'w') as f:
                    f.write(version + '\n')
                logger.info("Changed %s to '%s'", versionfile, version)
                return

        good_version = "version = '%s'" % version
        line_number = 0
        setup_lines, encoding = utils.read_text_file(
            'setup.py',
            fallback_encoding=self.fallback_encoding,
        )
        for line_number, line in enumerate(setup_lines):
            if VERSION_PATTERN.search(line):
                logger.debug("Matching version line found: '%s'", line)
                if line.startswith(' '):
                    # oh, probably '    version = 1.0,' line.
                    indentation = line.split('version')[0]
                    # Note: no spaces around the '='.
                    good_version = indentation + "version='%s'," % version
                if '"' in line:
                    good_version = good_version.replace("'", '"')
                setup_lines[line_number] = good_version
                utils.write_text_file(
                    'setup.py', '\n'.join(setup_lines), encoding)
                logger.info("Set setup.py's version to '%s'", version)
                return
            if UPPERCASE_VERSION_PATTERN.search(line):
                # This one only occurs in the first column, so no need to
                # handle indentation.
                logger.debug("Matching version line found: '%s'", line)
                good_version = good_version.upper()
                if '"' in line:
                    good_version = good_version.replace("'", '"')
                setup_lines[line_number] = good_version
                utils.write_text_file(
                    'setup.py', '\n'.join(setup_lines), encoding)
                logger.info("Set setup.py's version to '%s'", version)
                return

        good_version = "version = %s" % version
        if os.path.exists('setup.cfg'):
            setup_cfg_lines, encoding = utils.read_text_file(
                'setup.cfg',
                fallback_encoding=self.fallback_encoding,
            )
            for line_number, line in enumerate(setup_cfg_lines):
                if VERSION_PATTERN.search(line):
                    logger.debug("Matching version line found: '%s'", line)
                    if line.startswith(' '):
                        indentation = line.split('version')[0]

                        good_version = indentation + good_version
                    setup_cfg_lines[line_number] = good_version
                    utils.write_text_file(
                        'setup.cfg', '\n'.join(setup_cfg_lines), encoding)
                    logger.info("Set setup.cfg's version to '%s'", version)
                    return

        logger.error(
            "We could read a version from setup.py, but could not write it "
            "back. See "
            "https://zestreleaser.readthedocs.io/en/latest/versions.html "
            "for hints.")
        raise RuntimeError("Cannot set version")

    version = property(_extract_version, _update_version)

    #
    # Methods that need to be supplied by child classes
    #

    @property
    def name(self):
        "Name of the project under version control"
        raise NotImplementedError()

    def available_tags(self):
        """Return available tags."""
        raise NotImplementedError()

    def prepare_checkout_dir(self, prefix):
        """Return a temporary checkout location. Create this directory first
        if necessary."""
        raise NotImplementedError()

    def tag_url(self, version):
        "URL to tag of version."
        raise NotImplementedError()

    def cmd_diff(self):
        "diff command"
        raise NotImplementedError()

    def cmd_commit(self, message):
        "commit command: should specify a verbose option if possible"
        raise NotImplementedError()

    def cmd_diff_last_commit_against_tag(self, version):
        """Return diffs between a tagged version and the last commit of
        the working copy.
        """
        raise NotImplementedError()

    def cmd_log_since_tag(self, version):
        """Return log since a tagged version till the last commit of
        the working copy.
        """
        raise NotImplementedError()

    def cmd_create_tag(self, version, message, sign=False):
        "Create a tag from a version name."
        raise NotImplementedError()

    def checkout_from_tag(self, version):
        package = self.name
        prefix = f'{package}-{version}-'
        tagdir = self.prepare_checkout_dir(prefix)
        os.chdir(tagdir)
        cmd = self.cmd_checkout_from_tag(version, tagdir)
        print(utils.execute_commands(cmd))

    def is_clean_checkout(self):
        "Is this a clean checkout?"
        raise NotImplementedError()

    def push_commands(self):
        """Return commands to push changes to the server.

        Needed if a commit isn't enough.

        """
        return []

    def list_files(self):
        """List files in version control.

        We could raise a NotImplementedError, but a basic method that
        works is handy for the vcs.txt tests.
        """
        files = []
        for dirpath, dirnames, filenames in os.walk(os.curdir):
            dirnames  # noqa pylint
            for filename in filenames:
                files.append(os.path.join(dirpath, filename))
        return files
