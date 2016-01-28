"""Do the checks and tasks that have to happen after doing a release.
"""
from __future__ import unicode_literals

import datetime
import logging
import sys

from zest.releaser import baserelease
from zest.releaser import utils
from zest.releaser.utils import read_text_file
from zest.releaser.utils import write_text_file


logger = logging.getLogger(__name__)

TODAY = datetime.datetime.today().strftime('%Y-%m-%d')
NOTHING_CHANGED_YET = '- Nothing changed yet.'
COMMIT_MSG = 'Back to development: %(new_version)s'
DEV_VERSION_TEMPLATE = '%(new_version)s.dev0'

DATA = {
    # Documentation for self.data.  You get runtime warnings when something is
    # in self.data that is not in this list.  Embarrasment-driven
    # documentation!
    'workingdir': 'Original working directory',
    'reporoot': 'Root of the version control repository',
    'name': 'Name of the project being released',
    'nothing_changed_yet': 'First line in new changelog section',
    'history_header': 'Header template used for 1st history header',
}


class AddChangelogEntry(baserelease.Basereleaser):
    """Add a changelog entry.

    self.data holds data that can optionally be changed by plugins.

    """

    def __init__(self, vcs=None, message=''):
        baserelease.Basereleaser.__init__(self, vcs=vcs)
        # Prepare some defaults for potential overriding.
        self.data.update(dict(
            nothing_changed_yet=NOTHING_CHANGED_YET,
            commit_msg=COMMIT_MSG,
            dev_version_template=DEV_VERSION_TEMPLATE))
        # The message we want to add.
        self.message = message

    def prepare(self):
        """Prepare self.data by asking about new dev version"""
        if not utils.sanity_check(self.vcs):
            logger.critical("Sanity check failed.")
            sys.exit(1)
        self._grab_version()
        self._update_history(self.message)

    def execute(self):
        """Make the changes and offer a commit"""
        self._update_history()
        self._diff_and_commit()
        self._push()

    def _update_history(self, message=''):
        """Update the history file"""
        version = self.data['new_version']
        history = self.vcs.history_file()
        if not history:
            logger.warn("No history file found")
            return
        history_lines, history_encoding = read_text_file(history)
        history_lines = history_lines.split('\n')
        headings = utils.extract_headings_from_history(history_lines)
        if not len(headings):
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
                  self.data['nothing_changed_yet'],
                  '',
                  '']
        history_lines[inject_location:inject_location] = inject
        contents = '\n'.join(history_lines)
        write_text_file(history, contents, history_encoding)
        logger.info("Injected new section into the history: %r", header)


def datacheck(data):
    """Entrypoint: ensure that the data dict is fully documented"""
    utils.is_data_documented(data, documentation=DATA)


def main():
    parser = utils.base_option_parser()
    parser.add_argument(
        "message",
        help="Text of changelog entry")
    options = utils.parse_options(parser)
    utils.configure_logging()
    addchangelogentry = AddChangelogEntry()
    addchangelogentry.run()
