from __future__ import unicode_literals

import ast
import logging
import io
import itertools
import os
import sys
import token
try:
    from tokenize import generate_tokens as tokenize
except ImportError:
    # Py3k
    from tokenize import tokenize

import six

from zest.releaser import pypi
from zest.releaser import utils


TXT_EXTENSIONS = ['rst', 'txt', 'markdown', 'md']
logger = logging.getLogger(__name__)


class BaseVersionControl(object):
    "Shared implementation between all version control systems"

    internal_filename = ''  # e.g. '.svn' or '.hg'
    setuptools_helper_package = ''

    def __init__(self):
        self.workingdir = os.getcwd()

    def _find_nodes(self, tree, type_):
        for node in ast.walk(tree):
            if isinstance(node, type_):
                yield node

    def _find_string_assignments(self, tree, name):
        """In an abstract syntax tree finds variable assignments to
        `name` that are strings.
        """

        for assignment_node in self._find_nodes(tree, ast.Assign):
            # in the code `spam = ham = eggs`, 'spam' and 'ham' are targets.
            for target in assignment_node.targets:
                if not isinstance(target, ast.Name):
                    # Should never happen
                    continue
                if target.id != name:
                    continue
                if isinstance(assignment_node.value, ast.Str):
                    yield assignment_node

    def _find_string_keywords(self, tree, name):
        """In and abstract syntax tree finds keyword assignments to
        `name` that are strings.
        """

        for keyword_node in self._find_nodes(tree, ast.keyword):
            if keyword_node.arg != name:
                continue
            if isinstance(keyword_node.value, ast.Str):
                yield keyword_node

    def _replace_string(self, code, start_line, start_col, new_value):
        """Takes a string containing Python code, integers indicating
        where a Python string appears in that code and a new value,
        then replaces that Python string in the source with the new
        string value and returns the new Python code.
        """

        if six.PY2:
            readline = io.BytesIO(code.encode('utf8')).readline
        else:
            readline = io.StringIO(code).readline

        toks = tokenize(readline)
        found = False
        for type_, _token, start, end, _line in toks:
            token_start_line, token_start_col = start
            token_end_line, token_end_col = end
            if type_ != token.STRING:
                continue
            if token_start_line < start_line:
                continue
            if token_start_col < start_col:
                continue

            found = True
            break

        if not found:
            raise ValueError('Could not find string assignment.')

        lines = code.split('\n')
        # -1 below because line numbers start at 1, but our list starts at 0
        return '\n'.join(
            lines[:token_start_line - 1] +
            [
                lines[token_start_line - 1][:token_start_col] +
                repr(new_value) +
                lines[token_end_line - 1][token_end_col:]
            ] +
            lines[token_end_line:]
            )

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
            f = open(version_file, 'r')
            version = f.read()
            return utils.strip_version(version)

    def get_python_file_version(self):
        setup_cfg = pypi.SetupConfig()
        if not setup_cfg.python_file_with_version():
            return
        code = utils.read_text_file(
            setup_cfg.python_file_with_version())
        tree = ast.parse(code, setup_cfg.python_file_with_version())
        for assignment in self._find_string_assignments(tree, '__version__'):
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
            if fullpath.lower() == 'debian/changelog':
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
                    logger.warn("Found file %s in version control but not on "
                                "file execute_command.", fullpath)
                    continue
                found.append(fullpath)
        if not found:
            return
        if len(found) > 1:
            found.sort(key=len)
            logger.warn("Found more than one file, picked the shortest one to "
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
                logger.warn("The specified history file %s doesn't exist",
                            location)
        filenames = []
        for base in ['CHANGES', 'HISTORY', 'CHANGELOG']:
            filenames.append(base)
            for extension in TXT_EXTENSIONS:
                filenames.append('.'.join([base, extension]))
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
            code = utils.read_text_file(filename)
            tree = ast.parse(code, filename)
            assignment = next(self._find_string_assignments(
                tree, '__version__'))
            contents = self._replace_string(
                code,
                assignment.value.lineno,
                assignment.value.col_offset,
                version)
            open(filename, 'w').write(contents)
            logger.info("Set __version__ in %s to %r", filename, version)
            return

        version_filenames = ['version']
        for extension in TXT_EXTENSIONS:
            version_filenames.append('.'.join(['version', extension]))
        versionfile = self.filefind(version_filenames)
        if versionfile:
            # We have a version.txt file but does it match the setup.py
            # version (if any)?
            setup_version = self.get_setup_py_version()
            if not setup_version or (setup_version ==
                                     self.get_version_txt_version()):
                open(versionfile, 'w').write(version + '\n')
                logger.info("Changed %s to %r", versionfile, version)
                return

        contents = utils.read_text_file('setup.py')
        tree = ast.parse(contents, 'setup.py')
        for assignment in itertools.chain(
                self._find_string_assignments(tree, 'version'),
                self._find_string_keywords(tree, 'version')
                ):

            logger.debug("Matching version line found: %r",
                         assignment.value.lineno)
            contents = self._replace_string(
                contents,
                assignment.value.lineno,
                assignment.value.col_offset,
                version)

        open('setup.py', 'w').write(contents)
        logger.info("Set setup.py's version to %r", version)
        return

        logger.error(
            "We could read a version from setup.py, but could not write it " +
            "back. See " +
            "http://zestreleaser.readthedocs.org/en/latest/versions.html " +
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

    def cmd_create_tag(self, version):
        "Create a tag from a version name."
        raise NotImplementedError()

    def checkout_from_tag(self, version):
        package = self.name
        prefix = '%s-%s-' % (package, version)
        tagdir = self.prepare_checkout_dir(prefix)
        os.chdir(tagdir)
        cmd = self.cmd_checkout_from_tag(version, tagdir)
        print(utils.execute_command(cmd))

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
        for dirpath, dirnames, filenames in os.walk('.'):
            dirnames  # noqa pylint
            for filename in filenames:
                files.append(os.path.join(dirpath, filename))
        return files
