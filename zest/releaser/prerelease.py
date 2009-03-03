"""Do the checks and tasks that have to happen before doing a release.
"""
import datetime
import logging
import sys

import utils

logger = logging.getLogger('prerelease')
TODAY = datetime.datetime.today().strftime('%Y-%m-%d')


def check_version():
    """Set the version to a non-development version."""
    original_version = utils.extract_version()
    version = original_version
    logger.debug("Extracted version: %s", version)
    if version is None:
        logger.critical('No version found.')
        sys.exit(1)
    suggestion = utils.cleanup_version(version)
    print ("Enter version [%s]:" % suggestion)
    version = raw_input().strip()
    if not version:
        version = suggestion
    if version != original_version:
        utils.update_version(version)
        logger.info("Changed version from %r to %r" % (original_version,
                                                       version))
    return version


def check_history(second=False):
    """Check if the history has been updated.

    Every history heading looks like '1.0 b4 (1972-12-25)'. Extract them,
    check if the first one matches the version and whether it has a the
    current date.

    Some packages have docs/HISTORY.txt and package/name/HISTORY.txt.
    When second is True, we check the history of the second match.
    """
    history = utils.history_file(second=second)
    if not history:
        logger.warn("No history file found")
        return
    logger.debug("Checking %s", history)

    history_lines = open(history).read().split('\n')
    headings = utils.extract_headings_from_history(history_lines)
    if not len(headings):
        if not second:
            # Try finding a second history file.
            check_history(second=True)
            return
        logger.error("No detectable version heading in the history file.")
        sys.exit()

    first = headings[0]
    detected_version = utils.extract_version()
    version_ok = (first['version'] == detected_version)
    if not version_ok:
        logger.debug("First history heading's version (%r) doesn't match "
                      "the detected version (%r).",
                      first['version'], detected_version)
    date_ok = (first['date'] == TODAY)
    if not date_ok:
        logger.debug("First history heading's date (%r) doesn't match "
                     "today's date (%r).",
                     first['date'], TODAY)
    if not (date_ok and version_ok):
        good_heading = '%s (%s)' % (detected_version, TODAY)
        line = headings[0]['line']
        previous = history_lines[line]
        history_lines[line] = good_heading
        logger.debug("Set heading to %r.", good_heading)
        history_lines[line+1] = utils.fix_rst_heading(
            heading=good_heading,
            below=history_lines[line+1])
        logger.debug("Set line below heading to %r",
                     history_lines[line+1])
        contents = '\n'.join(history_lines)
        open(history, 'w').write(contents)
        logger.info("History file %s updated, first heading set to %r "
                    "from %r", history, good_heading, previous)


def main():
    logging.basicConfig(level=utils.loglevel(),
                        format="%(levelname)s: %(message)s")
    # XXX Check for uncommitted files.
    version = check_version()
    check_history()
    # XXX Check long-description
    utils.show_diff_offer_commit('Preparing release %s' % version)
