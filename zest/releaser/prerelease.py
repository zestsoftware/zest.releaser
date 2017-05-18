"""Do the checks and tasks that have to happen before doing a release.
"""
from __future__ import unicode_literals

import datetime
import logging
import sys

from zest.releaser import baserelease
from zest.releaser import utils

logger = logging.getLogger(__name__)

HISTORY_HEADER = '%(new_version)s (%(today)s)'
PRERELEASE_COMMIT_MSG = 'Preparing release %(new_version)s'

# Documentation for self.data.  You get runtime warnings when something is in
# self.data that is not in this list.  Embarrasment-driven documentation!
DATA = baserelease.DATA.copy()
DATA.update({
    'today': 'Date string used in history header',
})


class Prereleaser(baserelease.Basereleaser):
    """Prepare release, ready for making a tag and an sdist.

    self.data holds data that can optionally be changed by plugins.

    """

    def __init__(self, vcs=None):
        baserelease.Basereleaser.__init__(self, vcs=vcs)
        # Prepare some defaults for potential overriding.
        date_format = self.pypiconfig.date_format()
        self.data.update(dict(
            commit_msg=PRERELEASE_COMMIT_MSG,
            history_header=HISTORY_HEADER,
            today=datetime.datetime.today().strftime(date_format),
        ))

    def prepare(self):
        """Prepare self.data by asking about new version etc."""
        if not utils.sanity_check(self.vcs):
            logger.critical("Sanity check failed.")
            sys.exit(1)
        if not utils.check_recommended_files(self.data, self.vcs):
            logger.debug("Recommended files check failed.")
            sys.exit(1)
        # Grab current version.
        self._grab_version(initial=True)
        # Grab current history.
        self._grab_history()
        # Print changelog for this release.
        print("Changelog entries for version {0}:\n".format(
            self.data['new_version']))
        print(self.data.get('history_last_release'))
        # Grab and set new version.
        self._grab_version()
        # Look for unwanted 'Nothing changed yet' in latest header.
        self._check_nothing_changed()
        # Look for required text under the latest header.
        self._check_required()

    def execute(self):
        """Make the changes and offer a commit"""
        self._change_header()
        self._write_version()
        self._write_history()
        self._diff_and_commit()

    def _grab_version(self, initial=False):
        """Grab the version.

        When initial is False, ask the user for a non-development
        version.  When initial is True, grab the current suggestion.

        """
        original_version = self.vcs.version
        logger.debug("Extracted version: %s", original_version)
        if original_version is None:
            logger.critical('No version found.')
            sys.exit(1)
        suggestion = utils.cleanup_version(original_version)
        new_version = None
        if not initial:
            new_version = utils.ask_version(
                "Enter version", default=suggestion)
        if not new_version:
            new_version = suggestion
        self.data['original_version'] = original_version
        self.data['new_version'] = new_version


def datacheck(data):
    """Entrypoint: ensure that the data dict is fully documented"""
    utils.is_data_documented(data, documentation=DATA)


def main():
    utils.parse_options()
    utils.configure_logging()
    prereleaser = Prereleaser()
    prereleaser.run()
