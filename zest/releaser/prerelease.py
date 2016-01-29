"""Do the checks and tasks that have to happen before doing a release.
"""
from __future__ import unicode_literals

import datetime
import logging
import sys

from zest.releaser import baserelease
from zest.releaser import utils
from zest.releaser.postrelease import NOTHING_CHANGED_YET

logger = logging.getLogger(__name__)

TODAY = datetime.datetime.today().strftime('%Y-%m-%d')
HISTORY_HEADER = '%(new_version)s (%(today)s)'
PRERELEASE_COMMIT_MSG = 'Preparing release %(new_version)s'

DATA = {
    # Documentation for self.data.  You get runtime warnings when something is
    # in self.data that is not in this list.  Embarrasment-driven
    # documentation!
    'workingdir': 'Original working directory',
    'reporoot': 'Root of the version control repository',
    'name': 'Name of the project being released',
    'today': 'Date string used in history header',
    'new_version': 'New version (so 1.0 instead of 1.0dev)',
    'headings': 'Extracted headings from the history file',
    'history_file': 'Filename of history/changelog file (when found)',
    'history_last_release': (
        'Full text of all history entries of the current release'),
    'history_lines': 'List with all history file lines (when found)',
    'history_encoding': 'The detected encoding of the history file',
    'history_insert_line_here': (
        'Line number where an extra changelog entry can be inserted.'),
    'nothing_changed_yet': (
        'First line in new changelog section, '
        'warn when this is still in there before releasing'),
    'required_changelog_text': (
        'Text that must be present in the changelog. Can be a string or a '
        'list, for example ["New:", "Fixes:"]. For a list, only one of them '
        'needs to be present.'),
    'original_version': 'Version before prereleasing (e.g. 1.0.dev0)',
    'commit_msg': 'Message template used when committing',
    'history_header': 'Header template used for 1st history header',
}


class Prereleaser(baserelease.Basereleaser):
    """Prepare release, ready for making a tag and an sdist.

    self.data holds data that can optionally be changed by plugins.

    """

    def __init__(self, vcs=None):
        baserelease.Basereleaser.__init__(self, vcs=vcs)
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
