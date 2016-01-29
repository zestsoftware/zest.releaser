"""Add a changelog entry.
"""
from __future__ import unicode_literals

import datetime
import logging
import sys

from zest.releaser import baserelease
from zest.releaser import utils

logger = logging.getLogger(__name__)

TODAY = datetime.datetime.today().strftime('%Y-%m-%d')
HISTORY_HEADER = '%(new_version)s (unreleased)'
NOTHING_CHANGED_YET = '- Nothing changed yet.'
COMMIT_MSG = ''
DEV_VERSION_TEMPLATE = '%(new_version)s.dev0'

DATA = {
    # Documentation for self.data.  You get runtime warnings when something is
    # in self.data that is not in this list.  Embarrasment-driven
    # documentation!
    'workingdir': 'Original working directory',
    'reporoot': 'Root of the version control repository',
    'name': 'Name of the project being released',
    'nothing_changed_yet': 'First line in new changelog section',
    'new_version': 'New development version (so 1.1)',
    'dev_version': 'New development version with dev marker (so 1.1.dev0)',
    'commit_msg': (
        'Message template used when committing. '
        'Default: same as the message passed on the command line.'),
    'headings': 'Extracted headings from the history file',
    'history_file': 'Filename of history/changelog file (when found)',
    'history_last_release': (
        'Full text of all history entries of the current release'),
    'history_header': 'Header template used for 1st history header',
    'history_lines': 'List with all history file lines (when found)',
    'history_encoding': 'The detected encoding of the history file',
    'history_insert_line_here': (
        'Line number where an extra changelog entry can be inserted.'),
    'dev_version_template': 'Template for dev version number',
    'message': 'The message we want to add',
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
            history_header=HISTORY_HEADER,
            message=message.strip(),
            dev_version_template=DEV_VERSION_TEMPLATE))

    def prepare(self):
        """Prepare self.data by asking about new dev version"""
        if not utils.sanity_check(self.vcs):
            logger.critical("Sanity check failed.")
            sys.exit(1)
        self._grab_history()
        self._get_message()

    def execute(self):
        """Make the changes and offer a commit"""
        self._insert_changelog_entry(self.data['message'])
        self._write_history()
        self._diff_and_commit()

    def _get_message(self):
        """Get changelog message and commit message."""
        message = self.data['message']
        while not message:
            q = "What is the changelog message? "
            message = utils.get_input(q)
        self.data['message'] = message
        if not self.data['commit_msg']:
            self.data['commit_msg'] = message


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
    addchangelogentry = AddChangelogEntry(
        message=utils.fs_to_text(options.message))
    addchangelogentry.run()
