"""Do the checks and tasks that have to happen before doing a release.
"""

import datetime
import logging
import sys

from zest.releaser import baserelease
from zest.releaser import utils
from zest.releaser.utils import execute_command
from zest.releaser.utils import read_text_file
from zest.releaser.postrelease import NOTHING_CHANGED_YET

logger = logging.getLogger(__name__)

TODAY = datetime.datetime.today().strftime('%Y-%m-%d')
HISTORY_HEADER = u'{new_version:s} ({today:s})'
PRERELEASE_COMMIT_MSG = 'Preparing release {new_version:s}'

DATA = {
    # Documentation for self.data.  You get runtime warnings when something is
    # in self.data that is not in this list.  Embarrasment-driven
    # documentation!
    'workingdir': u'Original working directory',
    'name': u'Name of the project being released',
    'today': u'Date string used in history header',
    'new_version': u'New version (so 1.0 instead of 1.0dev)',
    'history_file': u'Filename of history/changelog file (when found)',
    'history_lines': u'List with all history file lines (when found)',
    'nothing_changed_yet': (
        u'First line in new changelog section, '
        u'warn when this is still in there before releasing'),
    'original_version': u'Version before prereleasing (e.g. 1.0dev)',
    'commit_msg': u'Message template used when committing',
    'history_header': u'Header template used for 1st history header',
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
            nothing_changed_yet=NOTHING_CHANGED_YET,
        ))

    def prepare(self):
        """Prepare self.data by asking about new version etc."""
        if not utils.sanity_check(self.vcs):
            logger.critical(u"Sanity check failed.")
            sys.exit(1)
        if not utils.check_recommended_files(self.data, self.vcs):
            logger.debug(u"Recommended files check failed.")
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
        logger.debug(u"Extracted version: {0}".format(original_version))
        if original_version is None:
            logger.critical('No version found.')
            sys.exit(1)
        suggestion = utils.cleanup_version(original_version)
        new_version = utils.ask_version("Enter version", default=suggestion)
        if not new_version:
            new_version = suggestion
        self.data['original_version'] = original_version
        self.data['new_version'] = new_version

    def _write_version(self):
        if self.data['new_version'] != self.data['original_version']:
            # self.vcs.version writes it to the file it got the version from.
            self.vcs.version = self.data['new_version']
            logger.info(u"Changed version from {0!r} to {1!r}".format(
                        self.data['original_version'],
                        self.data['new_version']))

    def _grab_history(self):
        """Calculate the needed history/changelog changes

        Every history heading looks like '1.0 b4 (1972-12-25)'. Extract them,
        check if the first one matches the version and whether it has a the
        current date.
        """
        default_location = None
        config = self.setup_cfg.config
        if config and config.has_option('zest.releaser', 'history_file'):
            default_location = config.get('zest.releaser', 'history_file')
        history_file = self.vcs.history_file(location=default_location)
        if not history_file:
            logger.warn(u"No history file found")
            self.data['history_lines'] = None
            self.data['history_file'] = None
            return
        logger.debug(u"Checking {0}".format(history_file))
        history_lines = read_text_file(history_file).split('\n')
        headings = utils.extract_headings_from_history(history_lines)
        if not len(headings):
            logger.error(u"No detectable version heading in the history "
                         u"file {0}".format(history_file))
            sys.exit(1)
        good_heading = self.data['history_header'].format(**self.data)
        # ^^^ history_header is a string with %(abc)s replacements.
        line = headings[0]['line']
        previous = history_lines[line]
        history_lines[line] = good_heading
        logger.debug(u"Set heading from {0!r} to {1!r}.".format(
            previous, good_heading))
        history_lines[line + 1] = utils.fix_rst_heading(
            heading=good_heading,
            below=history_lines[line + 1])
        logger.debug(u"Set line below heading to {0!r}".format(
                     history_lines[line + 1]))
        self.data['history_lines'] = history_lines
        self.data['history_file'] = history_file
        # TODO: add line number where an extra changelog entry can be
        # inserted.

        # Look for 'Nothing changed yet' under the latest header.  Not
        # nice if this text ends up in the changelog.  Did nothing happen?
        start = headings[0]['line']
        if len(headings) > 1:
            end = headings[1]['line']
        else:
            end = -1
        for line in history_lines[start:end]:
            if self.data['nothing_changed_yet'] in line:
                if not utils.ask((
                        u"WARNING: Changelog contains {0!r}. Are you sure you "
                        u"want to release?"
                        ).format(self.data['nothing_changed_yet']),
                        default=False):

                    logger.info(u"You can use the 'lasttaglog' command to "
                                u"see the commits since the last tag.")
                    sys.exit(0)
                break

    def _write_history(self):
        """Write previously-calculated history lines back to the file"""
        if self.data['history_file'] is None:
            return
        contents = u'\n'.join(self.data['history_lines'])
        history = self.data['history_file']
        open(history, 'w').write(contents)
        logger.info(u"History file {0} updated.".format(history))

    def _diff_and_commit(self):
        diff_cmd = self.vcs.cmd_diff()
        diff = execute_command(diff_cmd)
        if sys.version.startswith('2.6.2'):
            # python2.6.2 bug... http://bugs.python.org/issue5170 This is the
            # spot it can surface as we show a part of the changelog which can
            # contain every kind of character.  The rest is mostly ascii.
            print(u"Diff results:")
            print(diff)
        else:
            # Common case
            logger.info(u"The '{0}':\n\n{1}\n".format(diff_cmd, diff))
        if utils.ask(u"OK to commit this"):
            msg = self.data['commit_msg'].format(**self.data)
            msg = self.update_commit_message(msg)
            commit_cmd = self.vcs.cmd_commit(msg)
            commit = execute_command(commit_cmd)
            logger.info(commit)


def datacheck(data):
    """Entrypoint: ensure that the data dict is fully documented"""
    utils.is_data_documented(data, documentation=DATA)


def main():
    utils.parse_options()
    utils.configure_logging()
    prereleaser = Prereleaser()
    prereleaser.run()
