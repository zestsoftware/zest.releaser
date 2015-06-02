# Small utility methods.

from argparse import ArgumentParser
import logging
import os
import re
import shlex
import subprocess
import sys
import textwrap

from colorama import Fore
import pkg_resources
from pkg_resources import parse_version
import six
from six.moves import input
from six.moves import shlex_quote


logger = logging.getLogger(__name__)

WRONG_IN_VERSION = [u'svn', u'dev', u'(']
# For zc.buildout's system() method:
MUST_CLOSE_FDS = not sys.platform.startswith('win')

AUTO_RESPONSE = False
VERBOSE = False
INPUT_ENCODING = 'UTF-8'
if getattr(sys.stdin, 'encoding', None):
    INPUT_ENCODING = sys.stdin.encoding
OUTPUT_ENCODING = INPUT_ENCODING
if getattr(sys.stdout, 'encoding', None):
    OUTPUT_ENCODING = sys.stdout.encoding
ENCODING_HINTS = (b'# coding=', b'# -*- coding: ', b'# vim: set fileencoding=')


def cmd_to_text(cmd):
    return u' '.join(map(shlex_quote, cmd))


def fs_to_text(fs_name):
    if not isinstance(fs_name, six.text_type):
        fs_name = fs_name.decode(sys.getfilesystemencoding(),
                                 'surrogateescape')
    return fs_name


class CommandException(Exception):
    """Exception for when a command fails."""


def loglevel():
    """Return DEBUG when -v is specified, INFO otherwise"""
    if VERBOSE:
        return logging.DEBUG
    return logging.INFO


def read_text_file(filename, encoding=None):
    # Unless specified manually, We have no way of knowing what text
    # encoding this file may be in.
    # The 'open' method uses the default system encoding to read text
    # files in Python 3 or falls back to utf-8.
    with open(filename, 'rb') as fh:
        data = fh.read()

    if encoding is not None:
        return data.decode(encoding)

    # Look for hints, PEP263-style
    if data[:3] == b'\xef\xbb\xbf':
        return data.decode('UTF-8')

    data_len = len(data)
    for canary in ENCODING_HINTS:
        if canary in data:
            pos = data.index(canary)
            if pos > 1 and data[pos - 1] not in (b' ', b'\n', b'\r'):
                continue
            pos += len(canary)
            coding = b''
            while pos < data_len and data[pos] not in (b' ', b'\n'):
                coding += data[pos]
                pos += 1
            encoding = coding.decode('ascii').strip()
            try:
                return data.decode(encoding)
            except (LookupError, UnicodeError):
                # Try the next one
                pass

    return data.decode('UTF-8')


def strip_version(version):
    """Strip the version of all whitespace."""
    return version.strip().replace(' ', '')


def cleanup_version(version):
    """Check if the version looks like a development version."""
    for w in WRONG_IN_VERSION:
        if version.find(w) != -1:
            logger.debug(
                u"Version indicates development: {0}.".format(version))
            version = version[:version.find(w)].strip()
            logger.debug(u"Removing debug indicators: {0}".format(version))
        version = version.rstrip('.')  # 1.0.dev0 -> 1.0. -> 1.0
    return version


def parse_options():
    global AUTO_RESPONSE
    global VERBOSE
    parser = ArgumentParser()
    parser.add_argument(
        "--no-input",
        action="store_true",
        dest="auto_response",
        default=False,
        help="Don't ask questions, just use the default values")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        dest="verbose",
        default=False,
        help="Verbose mode")
    options = parser.parse_args()
    AUTO_RESPONSE = options.auto_response
    VERBOSE = options.verbose


# Hack for testing, see get_input()
TESTMODE = False


class AnswerBook(object):

    def __init__(self):
        self.answers = []

    def set_answers(self, answers=None):
        if answers is None:
            answers = []
        self.answers = answers

    def get_next_answer(self):
        return self.answers.pop(0)

test_answer_book = AnswerBook()


def get_input(question):
    if not TESTMODE:
        # Normal operation.
        result = input(question)
        if not isinstance(result, six.text_type):
            result = result.decode(INPUT_ENCODING)
        return result.strip()
    # Testing means no interactive input. Get it from answers_for_testing.
    print(u"Question: {0}".format(question.strip()))
    answer = test_answer_book.get_next_answer()
    if answer == u'':
        print(u"Our reply: <ENTER>")
    else:
        print(u"Our reply: {0}".format(answer))
    return answer


def ask_version(question, default=None):
    if AUTO_RESPONSE:
        if default is None:
            msg = (u"We cannot determine a default version, but "
                   u"we're running in --no-input mode. The original "
                   u"question: {0}")
            msg = msg.format(question)
            raise RuntimeError(msg)
        logger.debug(
            u"Auto-responding '{0}' to the question below.".format(default))
        logger.debug(question)
        return default
    if default:
        question += u" [{0}]: ".format(default)
    else:
        question += u": "
    while True:
        input_value = get_input(question)
        if input_value:
            if input_value.lower() in (u'y', u'n'):
                # Please read the question.
                print(u"y/n not accepted as version.")
                continue
            return input_value
        if default:
            return default


def ask(question, default=True, exact=False):
    """Ask the question in y/n form and return True/False.

    If you don't want a default 'yes', set default to None (or to False if you
    want a default 'no').

    With exact=True, we want to get a literal 'yes' or 'no', at least
    when it does not match the default.

    """
    if AUTO_RESPONSE:
        if default is None:
            msg = (u"The question '{0}' requires a manual answer, but "
                   u"we're running in --no-input mode.")
            msg = msg.format(question)
            raise RuntimeError(msg)
        logger.debug(u"Auto-responding '{0}' to the question below.".format(
            default and u"yes" or u"no"))
        logger.debug(question)
        return default
    while True:
        yn = u'y/n'
        if default is True:
            yn = u'Y/n'
        if default is False:
            yn = u'y/N'
        q = question + u" ({0})? ".format(yn)
        input_value = get_input(q)
        if input_value:
            answer = input_value
        else:
            answer = u''
        if not answer and default is not None:
            return default
        if exact and answer.lower() not in (u'yes', u'no'):
            print(u"Please explicitly answer yes/no in full "
                  u"(or accept the default)")
            continue
        if answer:
            answer = answer[0].lower()
            if answer == u'y':
                return True
            if answer == u'n':
                return False
        # We really want an answer.
        print(u'Please explicitly answer y/n')
        continue


def fix_rst_heading(heading, below):
    """If the 'below' line looks like a reST line, give it the correct length.

    This allows for different characters being used as header lines.
    """
    if len(below) == 0:
        return below
    first = below[0]
    if first not in u'-=`~':
        return below
    if not len(below) == len([char for char in below
                              if char == first]):
        # The line is not uniformly the same character
        return below
    below = first * len(heading)
    return below


def extract_headings_from_history(history_lines):
    """Return list of dicts with version-like headers.

    We check for patterns like '2.10 (unreleased)', so with either
    'unreleased' or a date between parenthesis as that's the format we're
    using. Just fix up your first heading and you should be set.

    As an alternative, we support an alternative format used by some
    zope/plone paster templates: '2.10 - unreleased' or '2.10 ~ unreleased'

    Note that new headers that zest.releaser sets are in our preferred
    form (so 'version (date)').
    """
    pattern = re.compile(r"""
    (?P<version>.+)  # Version string
    \(               # Opening (
    (?P<date>.+)     # Date
    \)               # Closing )
    \W*$             # Possible whitespace at end of line.
    """, re.VERBOSE)
    alt_pattern = re.compile(r"""
    ^                # Start of line
    (?P<version>.+)  # Version string
    \ [-~]\          # space dash/twiggle space
    (?P<date>.+)     # Date
    \W*$             # Possible whitespace at end of line.
    """, re.VERBOSE)
    headings = []
    line_number = 0
    for line in history_lines:
        match = pattern.search(line)
        alt_match = alt_pattern.search(line)
        if match:
            result = {'line': line_number,
                      'version': match.group('version').strip(),
                      'date': match.group('date'.strip())}
            headings.append(result)
            logger.debug(u"Found heading: {0!r}".format(result))
        if alt_match:
            result = {'line': line_number,
                      'version': alt_match.group('version').strip(),
                      'date': alt_match.group('date'.strip())}
            headings.append(result)
            logger.debug(u"Found alternative heading: {0!r}".format(result))
        line_number += 1
    return headings


def show_interesting_lines(result):
    """Just print the first and last five lines of (pypi) output.

    But: when there are errors or warnings, print everything and ask
    the user if she wants to continue.
    """
    if Fore.RED in result:
        # warnings/errors, print complete result.
        print(result)
        if not ask(
                u"There were errors or warnings. Are you sure "
                u"you want to continue?", default=False):
            sys.exit(1)
        # User has seen everything and wants to continue.
        return

    # No errors or warnings.  Show first and last lines.
    lines = [line for line in result.split(u'\n')]
    if len(lines) < 11:
        for line in lines:
            print(line)
        return
    print(u'Showing first few lines...')
    for line in lines[:5]:
        print(line)
    print(u'...')
    print(u'Showing last few lines...')
    for line in lines[-5:]:
        print(line)


def setup_py(rest_of_cmdline):
    """Return 'python setup.py' command (with hack for testing)"""
    executable = [sys.executable]
    if isinstance(rest_of_cmdline, six.string_types):
        # BBB
        rest_of_cmdline = shlex.split(rest_of_cmdline)
    if TESTMODE:
        # Hack for testing
        for unsafe in [u'upload', u'register']:
            if unsafe in rest_of_cmdline:
                executable = [u'echo', u'MOCK']

    return executable + [u'setup.py'] + rest_of_cmdline


def twine_command(rest_of_cmdline):
    """Return 'twine' command (with hack for testing)"""
    executable = [u'twine']
    if isinstance(rest_of_cmdline, six.string_types):
        # BBB
        rest_of_cmdline = shlex.split(rest_of_cmdline)
    if TESTMODE:
        # Hack for testing
        executable = [u'echo', u'MOCK', u'twine']

    return executable + rest_of_cmdline


def has_twine():
    """Is the twine command available?

    If twine is available, we prefer it for uploading.  We could try
    to import it, but it might be importable and still not available
    on the system path.

    So check if the twine command gives an error.

    Note that --version prints to stderr, so it fails.  --help prints
    to stdout as it should.
    """
    result = execute_command(twine_command(['--help']))
    return Fore.RED not in result


def is_data_documented(data, documentation=None):
    """check that the self.data dict is fully documented"""
    if documentation is None:
        documentation = {}
    if TESTMODE:
        # Hack for testing to prove entry point is being called.
        print(u"Checking data dict")
    undocumented = [key for key in data
                    if key not in documentation]
    if undocumented:
        print(u'Internal detail: key(s) {0} are not documented'.format(
            undocumented))


def resolve_name(name):
    """Resolve a name like ``module.object`` to an object and return it.

    This functions supports packages and attributes without depth limitation:
    ``package.package.module.class.class.function.attr`` is valid input.
    However, looking up builtins is not directly supported: use
    ``builtins.name``.

    Raises ImportError if importing the module fails or if one requested
    attribute is not found.
    """
    if '.' not in name:
        # shortcut
        __import__(name)
        return sys.modules[name]

    # FIXME clean up this code!
    parts = name.split('.')
    cursor = len(parts)
    module_name = parts[:cursor]
    ret = ''

    while cursor > 0:
        try:
            ret = __import__('.'.join(module_name))
            break
        except ImportError:
            cursor -= 1
            module_name = parts[:cursor]

    if ret == '':
        raise ImportError(parts[0])

    for part in parts[1:]:
        try:
            ret = getattr(ret, part)
        except AttributeError:
            raise ImportError(part)

    return ret


def run_hooks(setup_cfg, which_releaser, when, data):
    """Run all release hooks for the given release step, including
    project-specific hooks from setup.cfg, and globally installed entry-points.

    which_releaser can be prereleaser, releaser, postreleaser.

    when can be before, middle, after.

    """
    hook_group = '%s.%s' % (which_releaser, when)
    config = setup_cfg.config

    if config is not None and config.has_option('zest.releaser', hook_group):
        # Multiple hooks may be specified, each one separated by whitespace
        # (including newlines)
        hook_names = config.get('zest.releaser', hook_group).split()
        hooks = []

        # The following code is adapted from the 'packaging' package being
        # developed for Python's stdlib:

        # add project directory to sys.path, to allow hooks to be
        # distributed with the project
        # an optional package_dir option adds support for source layouts where
        # Python packages are not directly in the root of the source
        config_dir = os.path.dirname(setup_cfg.config_filename)
        sys.path.insert(0, os.path.dirname(setup_cfg.config_filename))

        if config.has_option('zest.releaser', 'hook_package_dir'):
            package_dir = config.get('zest.releaser', 'hook_package_dir')
            package_dir = os.path.join(config_dir, package_dir)
            sys.path.insert(0, package_dir)
        else:
            package_dir = None

        try:
            for hook_name in hook_names:
                try:
                    hooks.append(resolve_name(hook_name))
                except ImportError as e:
                    logger.warning(
                        'cannot find {0} hook: {1}; skipping...'.format(
                            hook_name, e.args[0]
                        ))
            for hook in hooks:
                hook(data)
        finally:
            sys.path.pop(0)
            if package_dir is not None:
                sys.path.pop(0)

    run_entry_points(which_releaser, when, data)


def run_entry_points(which_releaser, when, data):
    """Run the requested entry points.

    which_releaser can be prereleaser, releaser, postreleaser.

    when can be before, middle, after.

    """
    group = 'zest.releaser.%s.%s' % (which_releaser, when)
    for entrypoint in pkg_resources.iter_entry_points(group=group):
        # Grab the function that is the actual plugin.
        plugin = entrypoint.load()
        # Feed the data dict to the plugin.
        plugin(data)


def _execute_command(command, input_value=u''):
    """commands.getoutput() replacement that also works on windows"""
    if isinstance(command, six.string_types):
        # BBB
        command = shlex.split(command)

    logger.debug(u"Running command: {0}".format(cmd_to_text(command)))
    if command[0] == sys.executable:
        env = dict(os.environ, PYTHONPATH=os.pathsep.join(sys.path))
        if u'upload' in command or u'register' in command:
            # We really do want to see the stderr here, otherwise a
            # failed upload does not even show up in the output.
            show_stderr = True
        else:
            show_stderr = False
    else:
        env = None
        show_stderr = True
    p = subprocess.Popen(command,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         close_fds=MUST_CLOSE_FDS,
                         env=env)
    i, o, e = (p.stdin, p.stdout, p.stderr)
    if input_value:
        i.write(input_value.encode(INPUT_ENCODING))
    i.close()
    stdout_output = o.read()
    stderr_output = e.read()
    # We assume that the output from commands we're running is text.
    if not isinstance(stdout_output, six.text_type):
        stdout_output = stdout_output.decode(OUTPUT_ENCODING)
    if not isinstance(stderr_output, six.text_type):
        stderr_output = stderr_output.decode(OUTPUT_ENCODING)
    # TODO.  Note that the returncode is always None, also after
    # running p.kill().  The shell=True may be tripping us up.  For
    # some ideas, see http://stackoverflow.com/questions/4789837
    if p.returncode or show_stderr or u'Traceback' in stderr_output:
        # Some error occured
        # print(Fore.RED + stderr_output)
        stderr_output = stderr_output.strip()
        if stderr_output:
            # Make sure every error line is marked red.  The stderr
            # output also catches some warnings though.  It would be
            # really irritating if we start treating a line like this
            # as an error: warning: no previously-included files
            # matching '*.pyc' found anywhere in distribution.  Same
            # for empty lines.  So try to be smart about it.

            # errors = [(Fore.RED + line) for line in
            # stderr_output.split('\n')]
            errors = []
            for line in stderr_output.split(u'\n'):
                line = line.strip()
                if not line:
                    errors.append(line)
                elif line.lower().startswith(u'warn'):
                    # Not a real error.
                    errors.append(Fore.MAGENTA + line)
                elif line.lower().startswith(u"no previously-included"):
                    # Specifically a warning from distutils like this:
                    # no previously-included directories found matching...
                    # distutils is basically warning that a previous
                    # distutils run has done its job properly while
                    # reading the package manifest.
                    errors.append(Fore.MAGENTA + line)
                else:
                    errors.append(Fore.RED + line)
            errors = u'\n'.join(errors)
        else:
            errors = u''
        result = stdout_output + errors
    else:
        # Only return the stdout. Stderr only contains possible
        # weird/confusing warnings that might trip up extraction of version
        # numbers and so.
        result = stdout_output
        if stderr_output:
            logger.debug(u"Stderr of running command '{0}':\n{1}".format(
                cmd_to_text(command), stderr_output))
    o.close()
    e.close()
    return result


def execute_command(command, allow_retry=False, fail_message=u""):
    """Run the command and possibly retry it.

    When allow_retry is False, we simply call the base
    _execute_command and return the result.

    When allow_retry is True, a few things change.

    We print interesting lines.  When all is right, this will be the
    first and last few lines, otherwise the full standard output plus
    error output.

    When we discover errors, we give three options:
    - Abort
    - Retry
    - Continue

    There is an error is there is a red color in the output.

    It might be a warning, but we cannot detect the distinction.
    """
    if isinstance(command, six.string_types):
        # BBB
        command = shlex.split(command)

    result = _execute_command(command)
    if not allow_retry:
        return result
    if Fore.RED not in result:
        show_interesting_lines(result)
        return result
    # There are warnings or errors. Print the complete result.
    print(result)
    print(Fore.RED + u"There were errors or warnings.")
    if fail_message:
        print(Fore.RED + fail_message)
    explanation = u"""
    You have these options for retrying (first character is enough):
    Yes:   Retry. Do this if it looks like a temporary Internet or PyPI outage.
           You can also first edit $HOME/.pypirc and then retry in
           case of a credentials problem.
    No:    Do not retry, but continue with the rest of the process.
    Quit:  Stop completely. Note that the postrelease step has not
           been run yet, you need to do that manually.
    ?:     Show this help."""
    explanation = textwrap.dedent(explanation)
    question = u"Retry this command? [Yes/no/quit/?]"
    if AUTO_RESPONSE:
        msg = (u"The question '{0}' requires a manual answer, but "
               u"we're running in --no-input mode.")
        msg = msg.format(question)
        raise RuntimeError(msg)
    while True:
        input_value = get_input(question)
        if not input_value:
            # Default: yes, retry the command.
            input_value = u'y'
        if input_value:
            input_value = input_value.lower()
            if input_value == u'y' or input_value == u'yes':
                logger.info(u"Retrying command: {0!r}".format(
                    cmd_to_text(command)))
                return execute_command(command, allow_retry=True)
            if input_value == u'n' or input_value == u'no':
                # Accept the error, continue with the program.
                return result
            if input_value == u'q' or input_value == u'quit':
                raise CommandException(u"Command failed: {0!r}".format(
                    cmd_to_text(command)))
            # We could print the help/explanation only if the input is
            # '?', or maybe 'h', but if the user input has any other
            # content, it makes sense to explain the options anyway.
            print(explanation)


def get_last_tag(vcs):
    """Get last tag number, compared to current version.

    Note: when this cannot get a proper tag for some reason, it may
    exit the program completely.
    """
    version = vcs.version
    if not version:
        logger.critical(u"No version detected, so we can't do anything.")
        sys.exit(1)
    available_tags = vcs.available_tags()
    if not available_tags:
        logger.critical(u"No tags found, so we can't do anything.")
        sys.exit(1)

    # Mostly nicked from zest.stabilizer.

    # We seek a tag that's the same or less than the version as determined
    # by setuptools' version parsing. A direct match is obviously
    # right. The 'less' approach handles development eggs that have
    # already been switched back to development.
    available_tags.reverse()
    found = available_tags[0]
    parsed_version = parse_version(version)
    for tag in available_tags:
        parsed_tag = parse_version(tag)
        parsed_found = parse_version(found)
        if parsed_tag == parsed_version:
            found = tag
            logger.debug(u"Found exact match: %s", found)
            break
        if (parsed_tag >= parsed_found and
                parsed_tag < parsed_version):
            logger.debug(u"Found possible lower match: %s", tag)
            found = tag
    return found


def sanity_check(vcs):
    """Do sanity check before making changes

    Check that we are not on a tag and/or do not have local changes.

    Returns True when all is fine.
    """
    if not vcs.is_clean_checkout():
        q = (u"This is NOT a clean checkout. You are on a tag or you have "
             u"local changes.\n"
             u"Are you sure you want to continue?")
        if not ask(q, default=False):
            return False
    return True


def check_recommended_files(data, vcs):
    """Do check for recommended files.

    Returns True when all is fine.
    """
    main_files = os.listdir(data['workingdir'])
    if u'setup.py' not in main_files and u'setup.cfg' not in main_files:
        # Not a python package.  We have no recommendations.
        return True
    if u'MANIFEST.in' not in main_files and u'MANIFEST' not in main_files:
        q = u"""This package is missing a MANIFEST.in file. This file is
recommended. See http://docs.python.org/distutils/sourcedist.html for
more info. Sample contents:

recursive-include main_directory *
recursive-include docs *
include *
global-exclude *.pyc

You may want to quit and fix this.
"""
        if not vcs.is_setuptools_helper_package_installed():
            q += u"Installing {0} may help too.\n".format(
                vcs.setuptools_helper_package
                )
        # We could ask, but simply printing it is nicer.  Well, okay,
        # let's avoid some broken eggs on PyPI, per
        # https://github.com/zestsoftware/zest.releaser/issues/10
        q += u"Do you want to continue with the release?"
        if not ask(q, default=False):
            return False
        print(q)
    return True


def configure_logging():
    logging.addLevelName(
        logging.WARNING,
        Fore.MAGENTA + logging.getLevelName(logging.WARNING)
        )
    logging.addLevelName(
        logging.ERROR,
        Fore.RED + logging.getLevelName(logging.ERROR)
        )
    logging.basicConfig(level=loglevel(),
                        format=u"%(levelname)s: %(message)s")
