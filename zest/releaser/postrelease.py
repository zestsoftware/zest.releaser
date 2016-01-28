"""Do the checks and tasks that have to happen after doing a release.
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
    'new_version': 'New development version (so 1.1)',
    'dev_version': 'New development version with dev marker (so 1.1.dev0)',
    'commit_msg': 'Message template used when committing',
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
}


class Postreleaser(baserelease.Basereleaser):
    """Post-release tasks like resetting version number.

    self.data holds data that can optionally be changed by plugins.

    """

    def __init__(self, vcs=None):
        baserelease.Basereleaser.__init__(self, vcs=vcs)
        # Prepare some defaults for potential overriding.
        self.data.update(dict(
            nothing_changed_yet=NOTHING_CHANGED_YET,
            commit_msg=COMMIT_MSG,
            history_header=HISTORY_HEADER,
            dev_version_template=DEV_VERSION_TEMPLATE))

    def prepare(self):
        """Prepare self.data by asking about new dev version"""
        if not utils.sanity_check(self.vcs):
            logger.critical("Sanity check failed.")
            sys.exit(1)
        self._ask_for_new_dev_version()
        self._grab_history()

    def execute(self):
        """Make the changes and offer a commit"""
        self._write_version()
        self._change_header(add=True)
        self._write_history()
        self._diff_and_commit()
        self._push()

    def _ask_for_new_dev_version(self):
        """Ask for and store a new dev version string."""
        current = self.vcs.version
        # Clean it up to a non-development version.
        current = utils.cleanup_version(current)
        suggestion = utils.suggest_version(current)
        print("Current version is %s" % current)
        q = "Enter new development version ('.dev0' will be appended)"
        version = utils.ask_version(q, default=suggestion)
        if not version:
            version = suggestion
        if not version:
            logger.error("No version entered.")
            sys.exit(1)

        self.data['new_version'] = version
        dev_version = self.data['dev_version_template'] % self.data
        self.data['dev_version'] = dev_version
        logger.info("New version string is %s",
                    dev_version)

    def _write_version(self):
        """Update the version in vcs"""
        self.vcs.version = self.data['dev_version']


def datacheck(data):
    """Entrypoint: ensure that the data dict is fully documented"""
    utils.is_data_documented(data, documentation=DATA)


def main():
    utils.parse_options()
    utils.configure_logging()
    postreleaser = Postreleaser()
    postreleaser.run()
