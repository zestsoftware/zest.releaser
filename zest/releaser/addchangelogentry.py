"""Add a changelog entry.
"""
from __future__ import unicode_literals

import logging
import sys

from zest.releaser import baserelease
from zest.releaser import utils

logger = logging.getLogger(__name__)

COMMIT_MSG = ''

# Documentation for self.data.  You get runtime warnings when something is in
# self.data that is not in this list.  Embarrasment-driven documentation!
DATA = baserelease.DATA.copy()
DATA.update({
    'commit_msg': (
        'Message template used when committing. '
        'Default: same as the message passed on the command line.'),
    'message': 'The message we want to add',
})


class AddChangelogEntry(baserelease.Basereleaser):
    """Add a changelog entry.

    self.data holds data that can optionally be changed by plugins.

    """

    def __init__(self, vcs=None, message='', commit_msg=None):
        baserelease.Basereleaser.__init__(self, vcs=vcs)
        # Prepare some defaults for potential overriding.
        self.data.update(dict(
            commit_msg=commit_msg,
            message=message.strip(),
        ))

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
    parser.add_argument(
        "--commit_msg",
        help="Message template used when committing.",
        default=COMMIT_MSG)
    options = utils.parse_options(parser)
    utils.configure_logging()
    addchangelogentry = AddChangelogEntry(
        message=utils.fs_to_text(options.message),
        commit_msg=utils.fs_to_text(options.commit_msg),
    )
    addchangelogentry.run()
