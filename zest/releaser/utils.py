# Small utility methods.

from argparse import ArgumentParser
from colorama import Fore
from packaging.version import InvalidVersion
from packaging.version import parse as parse_version

import logging
import os
import re
import shlex
import subprocess
import sys
import textwrap
import tokenize


logger = logging.getLogger(__name__)

WRONG_IN_VERSION = ["svn", "dev", "("]
AUTO_RESPONSE = False
VERBOSE = False

if sys.version_info.major == 3 and sys.version_info.minor < 10:
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points


def fs_to_text(fs_name):
    if not isinstance(fs_name, str):
        fs_name = fs_name.decode(sys.getfilesystemencoding(), "surrogateescape")
    return fs_name


class CommandException(Exception):
    """Exception for when a command fails."""


def loglevel():
    """Return DEBUG when -v is specified, INFO otherwise"""
    if VERBOSE:
        return logging.DEBUG
    return logging.INFO


def splitlines_with_trailing(content):
    """Return .splitlines() lines, but with a trailing newline if needed"""
    lines = content.splitlines()
    if content.endswith("\n"):
        lines.append("")
    return lines


def write_text_file(filename, contents, encoding=None):
    with open(filename, "w", encoding=encoding) as f:
        f.write(contents)


def read_text_file(filename, encoding=None):
    """Return lines and encoding of the file

    Unless specified manually, We have no way of knowing what text
    encoding this file may be in.
    The standard Python 'open' method uses the default system encoding
    to read text files in Python 3 or falls back to utf-8.

    1. If encoding is specified, we use that encoding.

    2. Lastly we try to detect the encoding using tokenize.
    """
    if encoding is not None:
        # The simple case.
        logger.debug(
            "Decoding file %s from encoding %s from argument.", filename, encoding
        )
        with open(filename, "rb", encoding=encoding) as filehandler:
            data = filehandler.read()
        return splitlines_with_trailing(data), encoding

    # tokenize first detects the encoding (looking for encoding hints
    # or an UTF-8 BOM) and opens the file using this encoding.
    # See https://docs.python.org/3/library/tokenize.html
    with tokenize.open(filename) as filehandler:
        data = filehandler.read()
        encoding = filehandler.encoding
        logger.debug("Detected encoding of %s with tokenize: %s", filename, encoding)
    return splitlines_with_trailing(data), encoding


def strip_version(version):
    """Strip the version of all whitespace."""
    return version.strip().replace(" ", "")


def cleanup_version(version):
    """Check if the version looks like a development version."""
    for w in WRONG_IN_VERSION:
        if version.find(w) != -1:
            logger.debug("Version indicates development: %s.", version)
            version = version[: version.find(w)].strip()
            logger.debug("Removing debug indicators: '%s'", version)
        version = version.rstrip(".")  # 1.0.dev0 -> 1.0. -> 1.0
    return version


def strip_last_number(value):
    """Remove last number from a value.

    This is mostly for markers like ``.dev0``, where this would
    return ``.dev``.
    """
    if not value:
        return value
    match = re.search(r"\d+$", value)
    if not match:
        return value
    return value[: -len(match.group())]


def suggest_version(
    current,
    feature=False,
    breaking=False,
    less_zeroes=False,
    levels=0,
    dev_marker=".dev0",
    final=False,
):
    """Suggest new version.

    Try to make sure that the suggestion for next version after
    1.1.19 is not 1.1.110, but 1.1.20.

    - feature: increase major version, 1.2.3 -> 1.3.
    - breaking: increase minor version, 1.2.3 -> 2 (well, 2.0)
    - final: remove a/b/rc, 6.0.0rc1 -> 6.0.0
    - less_zeroes: instead of 2.0.0, suggest 2.0.
      Only makes sense in combination with feature or breaking.
    - levels: number of levels to aim for.  3 would give: 1.2.3.
      levels=0 would mean: do not change the number of levels.
    """
    # How many options are enabled?
    if len(list(filter(None, [breaking, feature, final]))) > 1:
        print("ERROR: Only enable one option of breaking/feature/final.")
        sys.exit(1)
    dev = ""
    base_dev_marker = strip_last_number(dev_marker)
    if base_dev_marker in current:
        index = current.find(base_dev_marker)
        # Put the standard development marker back at the end.
        dev = dev_marker
        current = current[:index]
    # Split in first and last part, where last part is one integer and the
    # first part can contain more integers plus dots.
    current_split = current.split(".")
    original_levels = len(current_split)
    try:
        [int(x) for x in current_split]
    except ValueError:
        # probably a/b in the version.
        pass
    else:
        # With levels=3, we prefer major.minor.patch as version.  Add zeroes
        # where needed.  We don't subtract: if version is 1.2.3.4.5, we are not
        # going to suggest to drop a few numbers.
        if levels:
            while len(current_split) < levels:
                current_split.append("0")
    if breaking:
        target = 0
    elif feature:
        if len(current_split) > 1:
            target = 1
        else:
            # When the version is 1, a feature release is the same as a
            # breaking release.
            target = 0
    else:
        target = -1
    first = ".".join(current_split[:target])
    last = current_split[target]
    try:
        last = int(last) + 1
        suggestion = ".".join([char for char in (first, str(last)) if char])
    except ValueError:
        if target != -1:
            # Something like 1.2rc1 where we want a feature bump.  This gets
            # too tricky.
            return
        if final:
            parsed_version = parse_version(current)
            if not parsed_version.pre:
                logger.warning(
                    "Version is not a pre version, so we cannot "
                    "calculate a suggestion for the final version."
                )
                return
            suggestion = parsed_version.base_version
        else:
            # Fall back on simply updating the last character when it is
            # an integer.
            try:
                last = int(current[target]) + 1
                suggestion = current[:target] + str(last)
            except (ValueError, IndexError):
                logger.warning(
                    "Version does not end with a number, so we can't "
                    "calculate a suggestion for a next version."
                )
                return
    # Maybe add a few zeroes: turn 2 into 2.0.0 if 3 levels is the goal.
    goal = max(original_levels, levels)
    length = len(suggestion.split("."))
    if less_zeroes and goal > 2:
        # Adding zeroes is okay, but the user prefers not to overdo it.  If the
        # goal is 3 levels, and the current suggestion is 1.3, then that is
        # fine.  If the current suggestion is 2, then don't increase the zeroes
        # all the way to 2.0.0, but stop at 2.0.
        goal = 2
    missing = goal - length
    if missing > 0:
        suggestion += ".0" * missing
    return suggestion + dev


def base_option_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--no-input",
        action="store_true",
        dest="auto_response",
        default=False,
        help="Don't ask questions, just use the default values",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        default=False,
        help="Verbose mode",
    )
    return parser


def parse_options(parser=None):
    global AUTO_RESPONSE
    global VERBOSE
    if parser is None:
        parser = base_option_parser()
    options = parser.parse_args()
    AUTO_RESPONSE = options.auto_response
    VERBOSE = options.verbose
    return options


# Hack for testing, see get_input()
TESTMODE = False


class AnswerBook:
    def __init__(self):
        self.answers = []

    def set_answers(self, answers=None):
        if answers is None:
            answers = []
        self.answers = answers

    def get_next_answer(self):
        if self.answers:
            return self.answers.pop(0)
        # Accept the default.
        return ""


test_answer_book = AnswerBook()


def get_input(question):
    if not TESTMODE:
        # Normal operation.
        result = input(question)
        return result.strip()
    # Testing means no interactive input. Get it from answers_for_testing.
    print("Question: %s" % question)
    answer = test_answer_book.get_next_answer()
    if answer == "":
        print("Our reply: <ENTER>")
    else:
        print("Our reply: %s" % answer)
    return answer


def ask_version(question, default=None):
    if AUTO_RESPONSE:
        if default is None:
            msg = (
                "We cannot determine a default version, but "
                "we're running in --no-input mode. The original "
                "question: %s"
            )
            msg = msg % question
            raise RuntimeError(msg)
        logger.info(question)
        logger.info("Auto-responding '%s'.", default)
        return default
    if default:
        question += " [%s]: " % default
    else:
        question += ": "
    while True:
        input_value = get_input(question)
        if input_value:
            if input_value.lower() in ("y", "n"):
                # Please read the question.
                print("y/n not accepted as version.")
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
            msg = (
                "The question '%s' requires a manual answer, but "
                "we're running in --no-input mode."
            )
            msg = msg % question
            raise RuntimeError(msg)
        logger.info(question)
        logger.info("Auto-responding '%s'.", "yes" if default else "no")
        return default
    while True:
        yn = "y/n"
        if default is True:
            yn = "Y/n"
        if default is False:
            yn = "y/N"
        q = question + " (%s)? " % yn
        input_value = get_input(q)
        if input_value:
            answer = input_value
        else:
            answer = ""
        if not answer and default is not None:
            return default
        if exact and answer.lower() not in ("yes", "no"):
            print("Please explicitly answer yes/no in full " "(or accept the default)")
            continue
        if answer:
            answer = answer[0].lower()
            if answer == "y":
                return True
            if answer == "n":
                return False
        # We really want an answer.
        print("Please explicitly answer y/n")
        continue


def fix_rst_heading(heading, below):
    """If the 'below' line looks like a reST line, give it the correct length.

    This allows for different characters being used as header lines.
    """
    if len(below) == 0:
        return below
    first = below[0]
    if first not in "-=`~":
        return below
    if not len(below) == len([char for char in below if char == first]):
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
    pattern = re.compile(
        r"""
    (?P<version>.+)  # Version string
    \(               # Opening (
    (?P<date>.+)     # Date
    \)               # Closing )
    \W*$             # Possible whitespace at end of line.
    """,
        re.VERBOSE,
    )
    alt_pattern = re.compile(
        r"""
    ^                # Start of line
    (?P<version>.+)  # Version string
    \ [-~]\          # space dash/twiggle space
    (?P<date>.+)     # Date
    \W*$             # Possible whitespace at end of line.
    """,
        re.VERBOSE,
    )
    headings = []
    line_number = 0
    for line in history_lines:
        match = pattern.search(line)
        alt_match = alt_pattern.search(line)
        if match:
            result = {
                "line": line_number,
                "version": match.group("version").strip(),
                "date": match.group("date".strip()),
            }
            headings.append(result)
            logger.debug("Found heading: '%s'", result)
        if alt_match:
            result = {
                "line": line_number,
                "version": alt_match.group("version").strip(),
                "date": alt_match.group("date".strip()),
            }
            headings.append(result)
            logger.debug("Found alternative heading: '%s'", result)
        line_number += 1
    return headings


def show_interesting_lines(result):
    """Just print the first and last five lines of (pypi) output.

    But: when there are errors or warnings, print everything.
    And if there is a non-zero exit code, ask the user if she wants to continue.
    """
    if Fore.RED in result:
        # warnings/errors, print complete result.
        print(result)
        if ERROR_EXIT_CODE in result:
            if not ask(
                "There were errors or warnings. Are you sure you want to continue?",
                default=False,
            ):
                sys.exit(1)
        # User has seen everything and wants to continue, or there was no exit code.
        return

    # No errors or warnings.  Show first and last lines.
    lines = [line for line in result.split("\n")]
    if len(lines) < 11:
        for line in lines:
            print(line)
        return
    print("Showing first few lines...")
    for line in lines[:5]:
        print(line)
    print("...")
    print("Showing last few lines...")
    for line in lines[-5:]:
        print(line)


def setup_py(*rest_of_cmdline):
    """Return 'python setup.py' command."""
    for unsafe in ["upload", "register"]:
        if unsafe in rest_of_cmdline:
            logger.error("Must not use setup.py %s. Use twine instead", unsafe)
            sys.exit(1)
    return [sys.executable, "setup.py"] + list(rest_of_cmdline)


def is_data_documented(data, documentation=None):
    """check that the self.data dict is fully documented"""
    if documentation is None:
        documentation = {}
    if TESTMODE:
        # Hack for testing to prove entry point is being called.
        print("Checking data dict")
    undocumented = [
        key for key in data if key not in documentation and not key.startswith("_")
    ]
    if undocumented:
        print("Internal detail: key(s) %s are not documented" % undocumented)


def resolve_name(name):
    """Resolve a name like ``module.object`` to an object and return it.

    This functions supports packages and attributes without depth limitation:
    ``package.package.module.class.class.function.attr`` is valid input.
    However, looking up builtins is not directly supported: use
    ``builtins.name``.

    Raises ImportError if importing the module fails or if one requested
    attribute is not found.
    """
    if "." not in name:
        # shortcut
        __import__(name)
        return sys.modules[name]

    # FIXME clean up this code!
    parts = name.split(".")
    cursor = len(parts)
    module_name = parts[:cursor]
    ret = ""

    while cursor > 0:
        try:
            ret = __import__(".".join(module_name))
            break
        except ImportError:
            cursor -= 1
            module_name = parts[:cursor]

    if ret == "":
        raise ImportError(parts[0])

    for part in parts[1:]:
        try:
            ret = getattr(ret, part)
        except AttributeError:
            raise ImportError(part)

    return ret


def run_hooks(zest_releaser_config, which_releaser, when, data):
    """Run all release hooks for the given release step, including
    project-specific hooks from setup.cfg, and globally installed entry-points.

    which_releaser can be prereleaser, releaser, postreleaser.

    when can be before, middle, after.

    """
    hook_group = f"{which_releaser}.{when}"
    config = zest_releaser_config.config

    if config is not None and config.get(hook_group):
        # Multiple hooks may be specified
        # in setup.cfg or .pypirc each one is separated by whitespace
        # (including newlines)
        if zest_releaser_config.hooks_filename in ["setup.py", "setup.cfg", ".pypirc"]:
            hook_names = config.get(hook_group).split()
        # in pyproject.toml, a list is passed with the hooks
        elif zest_releaser_config.hooks_filename == "pyproject.toml":
            hook_names = config.get(hook_group)
        else:
            hook_names = []
        hooks = []

        # The following code is adapted from the 'packaging' package being
        # developed for Python's stdlib:

        # add project directory to sys.path, to allow hooks to be
        # distributed with the project
        # an optional package_dir option adds support for source layouts where
        # Python packages are not directly in the root of the source
        config_dir = os.path.dirname(zest_releaser_config.hooks_filename)
        sys.path.insert(0, os.path.dirname(zest_releaser_config.hooks_filename))

        package_dir = config.get("hook_package_dir")
        if package_dir:
            package_dir = os.path.join(config_dir, package_dir)
            sys.path.insert(0, package_dir)

        try:
            for hook_name in hook_names:
                # Resolve the hook or fail with ImportError.
                hooks.append(resolve_name(hook_name))

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
    group = f"zest.releaser.{which_releaser}.{when}"
    for entrypoint in entry_points(group=group):
        # Grab the function that is the actual plugin.
        plugin = entrypoint.load()
        # Feed the data dict to the plugin.
        plugin(data)


# Lines ending up in stderr that are only warnings, not errors.
# We only check the start of lines.  Should be lowercase.
KNOWN_WARNINGS = [
    # Not a real error.
    "warn",
    # A warning from distutils like this:
    # no previously-included directories found matching...
    # distutils is basically warning that a previous distutils run has
    # done its job properly while reading the package manifest.
    "no previously-included",
    # This is from bdist_wheel displaying a warning by setuptools that
    # it will not include the __init__.py of a namespace package.  See
    # issue 108.
    "skipping installation of",
]
# Make them lowercase just to be sure.
KNOWN_WARNINGS = [w.lower() for w in KNOWN_WARNINGS]
# If we see a non-zero exit code, we add this in this output:
ERROR_EXIT_CODE = "ERROR: exit code"


def format_command(command):
    """Return command list formatted as string.

    THIS IS INSECURE! DO NOT USE except for directly printing the result.
    Do NOT pass this to subprocess.popen/run.
    See also: https://docs.python.org/3/library/shlex.html#shlex.quote
    """
    args = [shlex.quote(arg) for arg in command]
    return " ".join(args)


def _execute_command(command, cwd=None, extra_environ=None, env=None):
    """Execute a command, returning stdout, plus maybe parts of stderr."""
    # Enforce the command to be a list or arguments.
    assert isinstance(command, (list, tuple))
    if extra_environ and env:
        raise ValueError("You cannot pass both 'extra_environ' and 'env'.")
    logger.debug("Running command: '%s'", format_command(command))
    if env is None:
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(sys.path)
        if extra_environ is not None:
            env.update(extra_environ)
    # By default we show errors, of course.
    show_stderr = True
    if command[0].startswith(sys.executable):
        # For several Python commands, we do not want to see the stderr:
        # if we include it for `python setup.py --version`, then the version
        # may contain all kinds of warnings.
        show_stderr = False
        # But we really DO want to see the stderr for some other Python commands,
        # otherwise for example a failed upload would not even show up in the output.
        for flag in ("upload", "register"):
            if flag in command:
                show_stderr = True
                break
    process_kwargs = {
        "stdin": subprocess.PIPE,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "cwd": cwd,
        "env": env,
        "text": True,
    }
    process = subprocess.run(command, **process_kwargs)
    if process.returncode or show_stderr or "Traceback" in process.stderr:
        # Some error occurred.  Or everything is fine, but the command
        # prints to stderr anyway.
        if process.returncode:
            return (
                Fore.RED
                + f"{ERROR_EXIT_CODE} {process.returncode}.\n"
                + process.stdout
                + get_errors(process.stderr)
            )
        return process.stdout + get_errors(process.stderr)
    # Only return the stdout. Stderr only contains possible
    # weird/confusing warnings that might trip up extraction of version
    # numbers and so.
    if process.stderr:
        logger.debug(
            "Stderr of running command '%s':\n%s",
            format_command(process.args),
            process.stderr,
        )
    return process.stdout


def get_errors(stderr_output):
    # Some error occurred.  Return the relevant output.
    # print(Fore.RED + stderr_output)
    stderr_output = stderr_output.strip()
    if not stderr_output:
        return ""
    # Make sure every error line is marked red.  The stderr
    # output also catches some warnings though.  It would be
    # really irritating if we start treating a line like this
    # as an error: warning: no previously-included files
    # matching '*.pyc' found anywhere in distribution.  Same
    # for empty lines.  So try to be smart about it.
    errors = []
    for line in stderr_output.split("\n"):
        line = line.strip()
        if not line:
            # Keep it in the errors, but do not mark it with a color.
            errors.append(line)
            continue
        for known in KNOWN_WARNINGS:
            if line.lower().startswith(known):
                # Not a real error, so mark it as a warning.
                errors.append(Fore.MAGENTA + line)
                break
        else:
            # Not found in known warnings, so mark it as an error.
            errors.append(Fore.RED + line)
    return "\n".join(errors)


def execute_command(
    command, allow_retry=False, fail_message="", cwd=None, extra_environ=None, env=None
):
    """Run the command and possibly retry it.

    When allow_retry is False, we simply call the base
    _execute_command and return the result.

    When allow_retry is True, a few things change.

    You can either pass extra_environ options that we then add to a copy of the
    current OS environment, plus we add the PYTHONPATH.
    Or you can pass your own env.
    You can only use one of these two options.

    We print interesting lines.  When all is right, this will be the
    first and last few lines, otherwise the full standard output plus
    error output.

    When we discover errors, we give three options:
    - Abort
    - Retry
    - Continue

    There is an error when there is a red color in the output.

    It might be a warning, but we cannot detect the distinction.
    """
    result = _execute_command(command, cwd=cwd, extra_environ=extra_environ, env=env)
    if not allow_retry:
        if ERROR_EXIT_CODE in result:
            print(result)
            if not ask(
                "There were errors or warnings. Are you sure you want to continue?",
                default=False,
            ):
                sys.exit(1)
        # Note: whoever calls us could print the result.  This would be double
        # in case there was an error code but the user continues.  So be it.
        return result

    # At this point, a retry is allowed.  We only do this for very few commands.
    if AUTO_RESPONSE:
        # Retry is not possible with auto response, so just return the result.
        if ERROR_EXIT_CODE in result:
            # This is a real error, and the user cannot react.  We quit.
            print(result)
            sys.exit(1)
        return result
    if Fore.RED not in result or ERROR_EXIT_CODE not in result:
        show_interesting_lines(result)
        return result
    # There are warnings or errors. Print the complete result.
    print(result)
    print(Fore.RED + "There were errors or warnings.")
    if fail_message:
        print(Fore.RED + fail_message)
    retry = retry_yes_no(command)
    if retry:
        logger.info("Retrying command: '%s'", format_command(command))
        return execute_command(command, allow_retry=True)
    # Accept the error, continue with the program.
    return result


def execute_commands(commands, allow_retry=False, fail_message=""):
    assert isinstance(commands, (list, tuple))
    if not isinstance(commands[0], (list, tuple)):
        commands = [commands]
    result = []
    for cmd in commands:
        assert isinstance(cmd, (list, tuple))
        result.append(
            execute_command(cmd, allow_retry=allow_retry, fail_message=fail_message)
        )
    return "\n".join(result)


def retry_yes_no(command):
    """Ask the user to maybe retry a command.

    This is used for the twine upload command and for the final 'git push'.

    """
    explanation = """
    You have these options for retrying (first character is enough):
    Yes:   Retry. Do this if it looks like a temporary Internet or PyPI outage.
           You can also first edit $HOME/.pypirc and then retry in
           case of a credentials problem.
    No:    Do not retry, but continue with the rest of the process.
    Quit:  Stop completely. Note that the postrelease step has not
           finished fully. You need to do the 'git push' and possibly the upload
           manually.
    ?:     Show this help."""
    explanation = textwrap.dedent(explanation)
    question = "Retry this command? [Yes/no/quit/?]"
    if AUTO_RESPONSE:
        msg = (
            "The question '%s' requires a manual answer, but "
            "we're running in --no-input mode."
        )
        msg = msg % question
        raise RuntimeError(msg)
    while True:
        input_value = get_input(question)
        if not input_value:
            # Default: yes, retry the command.
            input_value = "y"
        if input_value:
            input_value = input_value.lower()
            if input_value == "y" or input_value == "yes":
                logger.info("Retrying command: '%s'", format_command(command))
                return True
            if input_value == "n" or input_value == "no":
                # Accept the error, continue with the program.
                return False
            if input_value == "q" or input_value == "quit":
                raise CommandException("Command failed: '%s'" % format_command(command))
            # We could print the help/explanation only if the input is
            # '?', or maybe 'h', but if the user input has any other
            # content, it makes sense to explain the options anyway.
            print(explanation)


def get_last_tag(vcs, allow_missing=False):
    """Get last tag number, compared to current version.

    Note: when this cannot get a proper tag for some reason, it may exit
    the program completely.  When no tags are found and allow_missing is
    True, we return None.
    """
    version = vcs.version
    if not version:
        logger.critical("No version detected, so we can't do anything.")
        sys.exit(1)
    available_tags = vcs.available_tags()
    if not available_tags:
        if allow_missing:
            logger.debug("No tags found.")
            return
        logger.critical("No tags found, so we can't do anything.")
        sys.exit(1)

    # Mostly nicked from zest.stabilizer.

    # We seek a tag that's the same or less than the version as determined
    # by setuptools' version parsing. A direct match is obviously
    # right. The 'less' approach handles development eggs that have
    # already been switched back to development.
    # Note: if parsing the current version fails, there is nothing we can do:
    # there is no sane way of knowing which version is smaller than an unparsable
    # version, so we just break hard.
    parsed_version = parse_version(version)
    found = parsed_found = None
    for tag in available_tags:
        try:
            parsed_tag = parse_version(tag)
        except InvalidVersion:
            logger.debug("Could not parse version: %s", tag)
            continue
        if parsed_tag == parsed_version:
            found = tag
            logger.debug("Found exact match: %s", found)
            break
        if parsed_tag >= parsed_version:
            # too new tag, not interesting
            continue
        if found is not None and parsed_tag <= parsed_found:
            # we already have a better match
            continue
        logger.debug("Found possible lower match: %s", tag)
        found = tag
        parsed_found = parsed_tag
    return found


def sanity_check(vcs):
    """Do sanity check before making changes

    Check that we are not on a tag and/or do not have local changes.

    Returns True when all is fine.
    """
    if not vcs.is_clean_checkout():
        q = (
            "This is NOT a clean checkout. You are on a tag or you have "
            "local changes.\n"
            "Are you sure you want to continue?"
        )
        if not ask(q, default=False):
            return False
    return True


def check_recommended_files(data, vcs):
    """Do check for recommended files.

    Returns True when all is fine.
    """
    main_files = os.listdir(data["workingdir"])
    if "setup.py" not in main_files and "setup.cfg" not in main_files:
        # Not a python package.  We have no recommendations.
        return True
    if "MANIFEST.in" not in main_files and "MANIFEST" not in main_files:
        q = """This package is missing a MANIFEST.in file. This file is
recommended. See http://docs.python.org/distutils/sourcedist.html for
more info. Sample contents:

recursive-include main_directory *
recursive-include docs *
include *
global-exclude *.pyc

You may want to quit and fix this.
"""
        if not vcs.is_setuptools_helper_package_installed():
            q += "Installing %s may help too.\n" % vcs.setuptools_helper_package
        # We could ask, but simply printing it is nicer.  Well, okay,
        # let's avoid some broken eggs on PyPI, per
        # https://github.com/zestsoftware/zest.releaser/issues/10
        q += "Do you want to continue with the release?"
        if not ask(q, default=False):
            return False
        print(q)
    return True


def configure_logging():
    logging.addLevelName(
        logging.WARNING, Fore.MAGENTA + logging.getLevelName(logging.WARNING)
    )
    logging.addLevelName(logging.ERROR, Fore.RED + logging.getLevelName(logging.ERROR))
    logging.basicConfig(level=loglevel(), format="%(levelname)s: %(message)s")


def get_list_item(lines):
    """Get most used list item from text.

    Meaning: probably a dash, maybe a star.
    """
    unordered_list = []
    for line in lines:
        # Possibly there is leading white space, strip it.
        stripped = line.strip()
        # Look for lines starting with one character and a space.
        if len(stripped) < 3:
            continue
        if stripped[1] != " ":
            continue
        prefix = stripped[0]
        # Restore stripped whitespace.
        white = line.find(prefix)
        unordered_list.append("{}{}".format(" " * white, prefix))
    # Get sane default.
    best = "-"
    count = 0
    # Start counting.
    for key in set(unordered_list):
        new_count = unordered_list.count(key)
        if new_count > count:
            best = key
            count = new_count
    # Return the best one.
    return best


def history_format(config_value, history_file):
    """Decide what is the history/changelog format."""
    default = "rst"
    history_format = config_value
    if not history_format:
        history_file = history_file or ""
        ext = history_file.split(".")[-1].lower()
        history_format = "md" if ext in ["md", "markdown"] else default
    return history_format


def string_to_bool(value):
    """Reimplementation of configparser.ConfigParser.getboolean()"""
    if value.isalpha():
        value = value.lower()
    if value in ["1", "yes", "true", "on"]:
        return True
    elif value in ["0", "no", "false", "off"]:
        return False
    else:
        raise ValueError(f"Cannot convert string '{value}' to a bool")


def extract_zestreleaser_configparser(config, config_filename):
    if not config:
        return None

    try:
        result = dict(config["zest.releaser"].items())
    except KeyError:
        logger.debug(f"No [zest.releaser] section found in the {config_filename}")
        return None

    boolean_keys = [
        "release",
        "create-wheel",
        "no-input",
        "register",
        "push-changes",
        "less-zeroes",
        "tag-signing",
        "run-pre-commit",
    ]
    integer_keys = [
        "version-levels",
    ]
    for key, value in result.items():
        if key in boolean_keys:
            result[key] = string_to_bool(value)
        if key in integer_keys:
            result[key] = int(value)
    return result


def filename_from_test_dir(filename: str) -> str:
    # pkg_resources.resource_filename is deprecated and the replacement
    # importlib.resources.files() is too cumbersome and really wants to be used as a
    # context manager which isn't handy for the way we run our tests. So we use
    # something more bare-bones that doesn't work when packaged in a .whl, which is
    # fine for development.
    this_dir = os.path.dirname(__file__)
    test_dir = os.path.join(this_dir, "tests")
    return os.path.join(test_dir, filename)
