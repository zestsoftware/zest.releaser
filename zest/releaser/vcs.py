import ast
import logging
import os
import re
import sys

import six
from zest.releaser import pypi
from zest.releaser import utils
from zest.releaser.utils import execute_command
from zest.releaser.utils import read_text_file


VERSION_PATTERN = re.compile(r"""
version\W*=\W*   # 'version =  ' with possible whitespace
\d               # Some digit, start of version.
""", re.VERBOSE)

TXT_EXTENSIONS = [u'rst', u'txt', u'markdown', u'md']

logger = logging.getLogger(__name__)


class BaseVersionControl(object):
    "Shared implementation between all version control systems"

    internal_filename = ''  # e.g. '.svn' or '.hg'
    setuptools_helper_package = ''

    def __init__(self):
        self.workingdir = os.getcwd()

    def is_setuptools_helper_package_installed(self):
        try:
            __import__(self.setuptools_helper_package)
        except ImportError:
            return False
        return True

    def _find_assignment(self, tree, varname):
        assignment = None
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == varname:
                        # Found the assignment
                        assignment = node
                        break
            elif isinstance(node, ast.keyword):
                if node.arg == varname:
                    assignment = node
                    break
            else:
                continue
            if assignment is not None:
                break

        if assignment is None or not isinstance(assignment.value, ast.Str):
            return None

        return assignment

    def get_setup_py_version(self):
        if os.path.exists(u'setup.py'):
            # First run egg_info, as that may get rid of some warnings
            # that otherwise end up in the extracted version, like
            # UserWarnings.
            execute_command(utils.setup_py([u'egg_info']))
            version = execute_command(
                utils.setup_py([u'--version'])).split(u'\n')[0]
            if u'Traceback' in version:
                # Likely cause is for example forgetting to 'import
                # os' when using 'os' in setup.py.
                logger.critical(u'The setup.py of this package has an error:')
                print(version)
                logger.critical(u'No version found.')
                sys.exit(1)
            return utils.strip_version(version)

    def get_setup_py_name(self):
        if os.path.exists(u'setup.py'):
            # First run egg_info, as that may get rid of some warnings
            # that otherwise end up in the extracted name, like
            # UserWarnings.
            execute_command(utils.setup_py([u'egg_info']))
            return execute_command(utils.setup_py([u'--name'])).strip()

    def get_version_txt_version(self):
        filenames = [u'version']
        for extension in TXT_EXTENSIONS:
            filenames.append(os.path.extsep.join([u'version', extension]))
        version_file = self.filefind(filenames)
        if version_file:
            version = read_text_file(version_file)
            return utils.strip_version(version)

    def get_python_file_version(self):
        setup_cfg = pypi.SetupConfig()
        if not setup_cfg.python_file_with_version():
            return
        content = read_text_file(setup_cfg.python_file_with_version())
        tree = ast.parse(content, setup_cfg.python_file_with_version())
        assignment = self._find_assignment(tree, u'__version__')
        if assignment is not None:
            return utils.strip_version(assignment.value.s)

        return None

    def filefind(self, names):
        """Return first found file matching name (case-insensitive).

        Some packages have docs/HISTORY.txt and
        package/name/HISTORY.txt.  We make sure we only return the one
        in the docs directory if no other can be found.

        'names' can be a string or a list of strings; if you have both
        a CHANGES.txt and a docs/HISTORY.txt, you want the top level
        CHANGES.txt to be found first.
        """
        if isinstance(names, six.string_types):
            names = [names]
        names = [name.lower() for name in names]
        files = self.list_files()
        found = []
        for fullpath in files:
            if fullpath.lower() == u'debian/changelog':
                logger.debug((
                    u"Ignoring {0}, unreadable (for us) debian "
                    u"changelog"
                    ).format(fullpath))
                continue
            filename = os.path.basename(fullpath)
            if filename.lower() in names:
                logger.debug(u"Found {0}".format(fullpath))
                if not os.path.exists(fullpath):
                    # Strange.  It at least happens in the tests when
                    # we deliberately remove a CHANGES.txt file.
                    logger.warn((
                        u"Found file {0} in version control but not on "
                        u"file execute_command.").format(fullpath))
                    continue
                found.append(fullpath)
        if not found:
            return
        if len(found) > 1:
            found.sort(key=len)
            logger.warn((
                u"Found more than one file, picked the shortest one to "
                u"change: {0}").format(u', '.join(found)))
        return found[0]

    def history_file(self, location=None):
        """Return history file location.
        """
        if location:
            # Hardcoded location passed from the config file.
            if os.path.exists(location):
                return location
            else:
                logger.warn(
                    u"The specified history file {0} doesn't exist".format(
                        location
                    ))
        filenames = []
        for base in [u'CHANGES', u'HISTORY', u'CHANGELOG']:
            filenames.append(base)
            for extension in TXT_EXTENSIONS:
                filenames.append(u'.'.join([base, extension]))
        history = self.filefind(filenames)
        if history:
            return history

    def tag_exists(self, version):
        """Check if a tag has already been created with the name of the
        version.
        """
        for tag in self.available_tags():
            if tag == version:
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

    def _update_version(self, version):
        """Find out where to change the version and change it.

        There are three places where the version can be defined. The first one
        is an explicitly defined Python file with a ``__version__``
        attribute. The second one is some version.txt that gets read by
        setup.py. The third is directly in setup.py.
        """

        if self.get_python_file_version():
            setup_cfg = pypi.SetupConfig()
            filename = setup_cfg.python_file_with_version()
            content = read_text_file(filename)
            tree = ast.parse(content, filename)
            assignment = self._find_assignment(tree, u'__version__')
            if assignment is not None:
                # This assumes that the version string does not span more than
                # one line
                position = (
                    assignment.value.lineno - 1,
                    assignment.value.col_offset,
                    assignment.value.col_offset + len(repr(assignment.value.s))
                    )
                lines = content.splitlines()
                lines[position[0]] = (
                    lines[position[0]][:position[1]] +
                    repr(version) +
                    lines[position[0]][position[2]:]
                    )
                contents = u'\n'.join(lines)
                open(filename, 'w').write(contents)
                logger.info(u"Set __version__ in {0} to {1!r}".format(
                    filename, version))
                return
        else:
            filename = 'setup.py'

        version_filenames = [u'version']
        for extension in TXT_EXTENSIONS:
            version_filenames.append(
                os.path.extsep.join([u'version', extension])
                )
        versionfile = self.filefind(version_filenames)
        if versionfile:
            # We have a version.txt file but does it match the setup.py
            # version (if any)?
            setup_version = self.get_setup_py_version()
            if not setup_version or (setup_version ==
                                     self.get_version_txt_version()):
                open(versionfile, 'w').write(version + u'\n')
                logger.info(
                    u"Changed {0} to {1!r}".format(versionfile, version)
                    )
                return

        content = read_text_file(filename)
        tree = ast.parse(content, filename)
        assignment = self._find_assignment(tree, u'version')
        if assignment:
            # This assumes that the version string does not span more than
            # one line
            position = (
                assignment.value.lineno - 1,
                assignment.value.col_offset,
                assignment.value.col_offset + len(repr(assignment.value.s))
                )
            lines = content.splitlines()
            logger.debug(u"Matching version line found: {0!r}".format(
                lines[position[0]]))
            lines[position[0]] = (
                lines[position[0]][:position[1]] +
                repr(version) +
                lines[position[0]][position[2]:]
                )
            contents = u'\n'.join(lines)
            open('setup.py', 'w').write(contents)
            logger.info("Set setup.py's version to {0}".format(version))
            return

        logger.error(
            u"We could read a version from setup.py, but could not write it "
            u"back. See "
            u"http://zestreleaser.readthedocs.org/en/latest/versions.html "
            u"for hints.")
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

    def cmd_create_tag(self, version):
        "Create a tag from a version name."
        raise NotImplementedError()

    def checkout_from_tag(self, version):
        package = self.name
        prefix = u'{0}-{1}-'.format(package, version)
        tagdir = self.prepare_checkout_dir(prefix)
        os.chdir(tagdir)
        cmds = self.cmd_checkout_from_tag(version, tagdir)
        for cmd in cmds:
            print(execute_command(cmd))

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
        for dirpath, dirnames, filenames in os.walk(u'.'):
            dirnames  # noqa pylint
            for filename in filenames:
                files.append(os.path.join(dirpath, filename))
        return files
