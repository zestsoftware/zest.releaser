"""Do the checks and tasks that have to happen before doing a release.
"""
import datetime
import logging
import sys
from commands import getoutput

from zest.releaser import utils
from zest.releaser import choose

logger = logging.getLogger('postrelease')

TODAY = datetime.datetime.today().strftime('%Y-%m-%d')


def ask_for_new_dev_version(vcs):
    """Ask for and return a new dev version string."""
    current = vcs.version
    first = current[:-1]
    last = current[-1]
    try:
        last = int(last) + 1
        suggestion = '%s%d' % (first, last)
    except ValueError:
        logger.warn("Version does not end with a number, so we can't "
                    "calculate a  suggestion for a next version.")
        suggestion = None
    print "Current version is %r" % current
    if suggestion:
        suggestion_string = ' [%s]' % suggestion
    else:
        suggestion_string = ''
    print ("Enter new development version ('dev' will be appended)"
           "%s:" % suggestion_string)
    version = raw_input().strip()
    if not version:
        version = suggestion
    if not version:
        logger.error("No version entered.")
        sys.exit()
    version = "%sdev" % version
    logger.info("New version string is %r", version)
    return version


def update_history(vcs, version, second=False):
    """Update the history file.

    Some packages have docs/HISTORY.txt and package/name/HISTORY.txt.
    When second is True, we update the history of the second match.
    """
    version = utils.cleanup_version(version)
    history = vcs.history_file(second=second)
    if not history:
        logger.warn("No history file found")
        return
    history_lines = open(history).read().split('\n')
    headings = utils.extract_headings_from_history(history_lines)
    if not len(headings):
        if not second:
            # Try finding a second history file.
            update_history(version, second=True)
            return
        logger.warn("No detectable existing version headings in the "
                    "history file.")
        inject_location = 0
        underline_char = '-'
    else:
        first = headings[0]
        inject_location = first['line']
        underline_line = first['line'] + 1
        try:
            underline_char = history_lines[underline_line][0]
        except IndexError:
            logger.debug("No character on line below header.")
            underline_char = '-'

    header = '%s (unreleased)' % version
    inject = [header,
              underline_char * len(header),
              '',
              '- Nothing changed yet.',
              '',
              '']
    history_lines[inject_location:inject_location] = inject
    contents = '\n'.join(history_lines)
    open(history, 'w').write(contents)
    logger.info("Injected new section into the history: %r", header)


def main():
    logging.basicConfig(level=utils.loglevel(),
                        format="%(levelname)s: %(message)s")
    vcs = choose.version_control()
    version = ask_for_new_dev_version(vcs)
    vcs.version = version
    update_history(vcs, version)

    # show diff, offer commit
    diff_cmd = vcs.cmd_diff()
    diff = getoutput(diff_cmd)
    logger.info("The '%s':\n\n%s\n" % (diff_cmd, diff))
    if utils.ask("OK to commit this"):
        commit_cmd = vcs.cmd_commit('Back to development: %s' % version)
        commit = getoutput(commit_cmd)
        logger.info(commit)
