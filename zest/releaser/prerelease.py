"""Do the checks and tasks that have to happen before doing a release.
"""

import datetime
import logging
import sys

from zest.releaser import baserelease
from zest.releaser import utils
from zest.releaser.utils import system

logger = logging.getLogger('prerelease')

TODAY = datetime.datetime.today().strftime('%Y-%m-%d')
HISTORY_HEADER = '%(new_version)s (%(today)s)'
PRERELEASE_COMMIT_MSG = 'Preparing release %(new_version)s'

DATA = {
    # Documentation for self.data.  You get runtime warnings when something is
    # in self.data that is not in this list.  Embarrasment-driven
    # documentation!
    'workingdir': 'Original working directory',
    'name': 'Name of the project being released',
    'today': 'Date string used in history header',
    'new_version': 'New version (so 1.0 instead of 1.0dev)',
    'history_file': 'Filename of history/changelog file (when found)',
    'history_lines': 'List with all history file lines (when found)',
    'original_version': 'Version before prereleasing (e.g. 1.0dev)',
    'commit_msg': 'Message template used when committing',
    'history_header': 'Header template used for 1st history header',
    }


class Prereleaser(baserelease.Basereleaser):
    """Prepare release, ready for making a tag and an sdist.

    self.data holds data that can optionally be changed by plugins.

    """

    def __init__(self):
        baserelease.Basereleaser.__init__(self)
        # Prepare some defaults for potential overriding.
        self.data.update(dict(
            today=datetime.datetime.today().strftime('%Y-%m-%d'),
            history_header=HISTORY_HEADER,
            commit_msg=PRERELEASE_COMMIT_MSG,
            ))

    def prepare(self):
        """Prepare self.data by asking about new version etc."""
        if not utils.sanity_check(self.vcs):
            logger.critical("Sanity check failed.")
            sys.exit(1)
        self._grab_version()
        self._grab_history()

    def execute(self):
        """Make the changes and offer a commit"""
        self._write_version()
        self._write_history()
        self._diff_and_commit()

    def _grab_version(self):
        """Set the version to a non-development version."""
        original_version = self.vcs.version
        logger.debug("Extracted version: %s", original_version)
        if original_version is None:
            logger.critical('No version found.')
            sys.exit(1)
        suggestion = utils.cleanup_version(original_version)
        q = ("Enter version [%s]: " % suggestion)
        new_version = utils.get_input(q).strip()
        if not new_version:
            new_version = suggestion
        self.data['original_version'] = original_version
        self.data['new_version'] = new_version

    def _write_version(self):
        if self.data['new_version'] != self.data['original_version']:
            # self.vcs.version writes it to the file it got the version from.
            self.vcs.version = self.data['new_version']
            logger.info("Changed version from %r to %r",
                        self.data['original_version'],
                        self.data['new_version'])

    def _grab_history(self):
        """Calculate the needed history/changelog changes

        Every history heading looks like '1.0 b4 (1972-12-25)'. Extract them,
        check if the first one matches the version and whether it has a the
        current date.
        """
        history_file = self.vcs.history_file()
        if not history_file:
            logger.warn("No history file found")
            self.data['history_lines'] = None
            self.data['history_file'] = None
            return
        logger.debug("Checking %s", history_file)
        history_lines = open(history_file).read().split('\n')
        # ^^^ TODO: .readlines()?
        headings = utils.extract_headings_from_history(history_lines)
        if not len(headings):
            logger.error("No detectable version heading in the history "
                         "file %s", history_file)
            sys.exit()
        good_heading = self.data['history_header'] % self.data
        # ^^^ history_header is a string with %(abc)s replacements.
        line = headings[0]['line']
        previous = history_lines[line]
        history_lines[line] = good_heading
        logger.debug("Set heading from %r to %r.", previous, good_heading)
        history_lines[line + 1] = utils.fix_rst_heading(
            heading=good_heading,
            below=history_lines[line + 1])
        logger.debug("Set line below heading to %r",
                     history_lines[line + 1])
        self.data['history_lines'] = history_lines
        self.data['history_file'] = history_file
        # TODO: add line number where an extra changelog entry can be
        # inserted.

    def _write_history(self):
        """Write previously-calculated history lines back to the file"""
        if self.data['history_file'] is None:
            return
        contents = '\n'.join(self.data['history_lines'])
        history = self.data['history_file']
        open(history, 'w').write(contents)
        logger.info("History file %s updated.", history)

    def _diff_and_commit(self):
        diff_cmd = self.vcs.cmd_diff()
        diff = system(diff_cmd)
        if sys.version.startswith('2.6.2'):
            # python2.6.2 bug... http://bugs.python.org/issue5170 This is the
            # spot it can surface as we show a part of the changelog which can
            # contain every kind of character.  The rest is mostly ascii.
            print "Diff results:"
            print diff
        else:
            # Common case
            logger.info("The '%s':\n\n%s\n" % (diff_cmd, diff))
        if utils.ask("OK to commit this"):
            msg = self.data['commit_msg'] % self.data
            commit_cmd = self.vcs.cmd_commit(msg)
            commit = system(commit_cmd)
            logger.info(commit)


def datacheck(data):
    """Entrypoint: ensure that the data dict is fully documented"""
    utils.is_data_documented(data, documentation=DATA)


def main():
    logging.basicConfig(level=utils.loglevel(),
                        format="%(levelname)s: %(message)s")
    prereleaser = Prereleaser()
    prereleaser.run()
