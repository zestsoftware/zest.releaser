# Small utility methods.
from optparse import OptionParser
from pkg_resources import parse_version
import logging
import os
import re
import subprocess
import sys

import pkg_resources

logger = logging.getLogger(__name__)

WRONG_IN_VERSION = ['svn', 'dev', '(']
# For zc.buildout's system() method:
MUST_CLOSE_FDS = not sys.platform.startswith('win')

AUTO_RESPONSE = False
VERBOSE = False


def loglevel():
    """Return DEBUG when -v is specified, INFO otherwise"""
    if VERBOSE:
        return logging.DEBUG
    return logging.INFO


def strip_version(version):
    """Strip the version of all whitespace."""
    return version.strip().replace(' ', '')


def cleanup_version(version):
    """Check if the version looks like a development version."""
    for w in WRONG_IN_VERSION:
        if version.find(w) != -1:
            logger.debug("Version indicates development: %s.", version)
            version = version[:version.find(w)].strip()
            logger.debug("Removing debug indicators: %r", version)
        version = version.rstrip('.')  # 1.0.dev0 -> 1.0. -> 1.0
    return version


def parse_options():
    global AUTO_RESPONSE
    global VERBOSE
    parser = OptionParser()
    parser.add_option("--no-input",
                      action="store_true",
                      dest="auto_response",
                      default=False,
                      help="Don't ask questions, just use the default values")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="Verbose mode")
    (options, args) = parser.parse_args()
    AUTO_RESPONSE = options.auto_response
    VERBOSE = options.verbose


# Hack for testing, see get_input()
TESTMODE = False
answers_for_testing = []

def get_input(question):
    if not TESTMODE:
        # Normal operation.
        return raw_input(question)
    # Testing means no interactive input. Get it from answers_for_testing.
    print "Question:", question
    answer = answers_for_testing.pop(0)
    if answer == '':
        print "Our reply: <ENTER>"
    else:
        print "Our reply:", answer
    return answer


def ask_version(question, default=None):
    if AUTO_RESPONSE:
        if default is None:
            msg = ("We cannot determine a default version, but "
                   "we're running in --no-input mode. The original "
                   "question: %s")
            msg = msg % question
            raise RuntimeError(msg)
        logger.debug("Auto-responding '%s' to the question below.", default)
        logger.debug(question)
        return default
    if default:
        question += " [%s]: " % default
    else:
        question += ": "
    while True:
        input = get_input(question)
        if input:
            return input
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
            msg = ("The question '%s' requires a manual answer, but " +
                   "we're running in --no-input mode.")
            msg = msg % question
            raise RuntimeError(msg)
        logger.debug("Auto-responding '%s' to the question below." % (
                default and "yes" or "no"))
        logger.debug(question)
        return default
    while True:
        yn = 'y/n'
        if default is True:
            yn = 'Y/n'
        if default is False:
            yn = 'y/N'
        q = question + " (%s)? " % yn
        input = get_input(q)
        if input:
            answer = input
        else:
            answer = ''
        if not answer and default is not None:
            return default
        if exact and answer.lower() not in ('yes', 'no'):
            print ("Please explicitly answer yes/no in full "
                   "(or accept the default)")
            continue
        if answer:
            answer = answer[0].lower()
            if answer == 'y':
                return True
            if answer == 'n':
                return False
        # We really want an answer.
        print 'Please explicitly answer y/n'
        continue


def fix_rst_heading(heading, below):
    """If the 'below' line looks like a reST line, give it the correct length.

    This allows for different characters being used as header lines.
    """
    if len(below) == 0:
        return below
    first = below[0]
    if first not in '-=`~':
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
            logger.debug("Found heading: %r", result)
        if alt_match:
            result = {'line': line_number,
                      'version': alt_match.group('version').strip(),
                      'date': alt_match.group('date'.strip())}
            headings.append(result)
            logger.debug("Found alternative heading: %r", result)
        line_number += 1
    return headings


def show_first_and_last_lines(result):
    """Just print the first and last five lines of (pypi) output"""
    lines = [line for line in result.split('\n')]
    if len(lines) < 11:
        for line in lines:
            print line
        return
    print 'Showing first few lines...'
    for line in lines[:5]:
        print line
    print '...'
    print 'Showing last few lines...'
    for line in lines[-5:]:
        print line


def show_last_lines(result):
    """Just print the last five lines of (pypi) output"""
    lines = [line for line in result.split('\n')]
    print 'Showing last few lines...'
    for line in lines[-5:]:
        print line


def setup_py(rest_of_cmdline):
    """Return 'python setup.py' command (with hack for testing)"""
    executable = sys.executable
    if TESTMODE:
        # Hack for testing
        for unsafe in ['upload', 'register', 'mregister']:
            if unsafe in rest_of_cmdline:
                executable = 'echo MOCK'

    return '%s setup.py %s' % (executable, rest_of_cmdline)


def is_data_documented(data, documentation={}):
    """check that the self.data dict is fully documented"""
    if TESTMODE:
        # Hack for testing to prove entry point is being called.
        print "Checking data dict"
    undocumented = [key for key in data
                    if key not in documentation]
    if undocumented:
        print 'Internal detail: key(s) %s are not documented' % undocumented


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
                except ImportError, e:
                    logger.warning('cannot find %s hook: %s; skipping...',
                                   hook_name, e.args[0])
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


def prepare_documentation_entrypoint(data):
    """Place the generated entrypoint doc in the source structure."""
    if data['name'] != 'zest.releaser':
        # We're available everywhere, but we're only intended for
        # zest.releaser internal usage.
        return
    target = os.path.join(data['workingdir'], 'doc', 'source',
                          'entrypoints.rst')
    marker = '.. ### AUTOGENERATED FROM HERE ###'
    result = []
    for line in open(target).readlines():
        line = line.rstrip()
        if line == marker:
            break
        result.append(line)
    result.append(marker)
    result.append('')

    # Preventing circular imports
    from zest.releaser import prerelease
    from zest.releaser import release
    from zest.releaser import postrelease

    for name, datadict in (
            ('prerelease', prerelease.DATA),
            ('release', release.DATA),
            ('postrelease', postrelease.DATA)):
        heading = '%s data dict items' % name.capitalize()
        result.append(heading)
        result.append('-' * len(heading))
        result.append('')
        for key in sorted(datadict.keys()):
            result.append(key)
            result.append('    ' + datadict[key])
            result.append('')

    open(target, 'wb').write('\n'.join(result))
    print "Wrote entry point documentation to", target


def system(command, input=''):
    """commands.getoutput() replacement that also works on windows"""
    #print "CMD: %r" % command
    p = subprocess.Popen(command,
                         shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         close_fds=MUST_CLOSE_FDS)
    i, o, e = (p.stdin, p.stdout, p.stderr)
    if input:
        i.write(input)
    i.close()
    result = o.read() + e.read()
    o.close()
    e.close()
    return result


def get_last_tag(vcs):
    """Get last tag number, compared to current version.

    Note: when this cannot get a proper tag for some reason, it may
    exit the program completely.
    """
    version = vcs.version
    if not version:
        logger.critical("No version detected, so we can't do anything.")
        sys.exit()
    available_tags = vcs.available_tags()
    if not available_tags:
        logger.critical("No tags found, so we can't do anything.")
        sys.exit()

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
            logger.debug("Found exact match: %s", found)
            break
        if (parsed_tag >= parsed_found and
                parsed_tag < parsed_version):
            logger.debug("Found possible lower match: %s", tag)
            found = tag
    return found


def sanity_check(vcs):
    """Do sanity check before making changes

    Check that we are not on a tag and/or do not have local changes.

    Returns True when all is fine.
    """
    if not vcs.is_clean_checkout():
        q = ("This is NOT a clean checkout. You are on a tag or you have "
             "local changes.\n"
             "Are you sure you want to continue?")
        if not ask(q, default=False):
            return False
    return True


def check_recommended_files(data, vcs):
    """Do check for recommended files.

    Returns True when all is fine.
    """
    main_files = os.listdir(data['workingdir'])
    if not 'setup.py' in main_files and not 'setup.cfg' in main_files:
        # Not a python package.  We have no recommendations.
        return True
    if not 'MANIFEST.in' in main_files and not 'MANIFEST' in main_files:
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
            q += "Installing %s may help too.\n" % \
                vcs.setuptools_helper_package
        # We could ask, but simply printing it is nicer.  Well, okay,
        # let's avoid some broken eggs on PyPI, per
        # https://github.com/zestsoftware/zest.releaser/issues/10
        q += "Do you want to continue with the release?"
        if not ask(q, default=False):
            return False
        print q
    return True
