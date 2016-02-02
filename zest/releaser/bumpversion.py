"""Do the checks and tasks that have to happen after doing a release.
"""
from __future__ import unicode_literals

import logging
import sys

from zest.releaser import baserelease
from zest.releaser import utils

logger = logging.getLogger(__name__)

HISTORY_HEADER = '%(clean_new_version)s (unreleased)'
COMMIT_MSG = 'Bumped version for %(release)s release.'

DATA = {
    # Documentation for self.data.  You get runtime warnings when something is
    # in self.data that is not in this list.  Embarrasment-driven
    # documentation!
    'workingdir': 'Original working directory',
    'reporoot': 'Root of the version control repository',
    'name': 'Name of the project being released',
    'clean_new_version': 'Clean new version (say 1.1)',
    'new_version': 'New version (say 1.1.dev0)',
    'commit_msg': 'Message template used when committing.',
    'headings': 'Extracted headings from the history file',
    'history_file': 'Filename of history/changelog file (when found)',
    'history_last_release': (
        'Full text of all history entries of the current release'),
    'history_header': 'Header template used for 1st history header',
    'history_lines': 'List with all history file lines (when found)',
    'history_encoding': 'The detected encoding of the history file',
    'history_insert_line_here': (
        'Line number where an extra changelog entry can be inserted.'),
    'original_version': 'Version before bump (e.g. 1.0.dev0)',
    'breaking': 'True if we handle a breaking (major) change',
    'feature': 'True if we handle a feature (minor) change',
    'release': 'Type of release: breaking, feature, normal',
}


class BumpVersion(baserelease.Basereleaser):
    """Add a changelog entry.

    self.data holds data that can optionally be changed by plugins.

    """

    def __init__(self, vcs=None, breaking=False, feature=False):
        baserelease.Basereleaser.__init__(self, vcs=vcs)
        # Prepare some defaults for potential overriding.
        if breaking:
            release = 'breaking'
        elif feature:
            release = 'feature'
        else:
            release = 'normal'
        self.data.update(dict(
            history_header=HISTORY_HEADER,
            breaking=breaking,
            feature=feature,
            release=release,
            commit_msg=COMMIT_MSG))

    def prepare(self):
        """Prepare self.data by asking about new dev version"""
        print('Checking version bump for {} release.'.format(
            self.data['release']))
        if not utils.sanity_check(self.vcs):
            logger.critical("Sanity check failed.")
            sys.exit(1)
        self._grab_version(initial=True)
        self._grab_history()
        # Grab and set new version.
        self._grab_version()

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
        suggestion = new_version = self.data.get('new_version')
        if not new_version:
            # Get a suggestion.
            breaking = self.data['breaking']
            feature = self.data['feature']
            # Compare the suggestion for the last tag with the current version.
            # The wanted version bump may already have been done.
            last_tag_version = utils.get_last_tag(self.vcs, allow_missing=True)
            if last_tag_version is None:
                print("No tag found. No version bump needed.")
                sys.exit(0)
            else:
                print("Last tag: {}".format(last_tag_version))
            print("Current version: {}".format(original_version))
            minimum_version = utils.suggest_version(
                last_tag_version, feature=feature, breaking=breaking)
            if minimum_version <= original_version:
                print("No version bump needed.")
                sys.exit(0)
            # A bump is needed.  Get suggestion for next version.
            suggestion = utils.suggest_version(
                original_version, feature=feature, breaking=breaking)
        if not initial:
            new_version = utils.ask_version(
                "Enter version", default=suggestion)
        if not new_version:
            new_version = suggestion
        self.data['original_version'] = original_version
        self.data['new_version'] = new_version
        self.data['clean_new_version'] = utils.cleanup_version(new_version)


def datacheck(data):
    """Entrypoint: ensure that the data dict is fully documented"""
    utils.is_data_documented(data, documentation=DATA)


def main():
    parser = utils.base_option_parser()
    parser.add_argument(
        "--feature",
        action="store_true",
        dest="feature",
        default=False,
        help="Bump for feature release (increase minor version)")
    parser.add_argument(
        "--breaking",
        action="store_true",
        dest="breaking",
        default=False,
        help="Bump for breaking release (increase major version)")
    options = utils.parse_options(parser)
    if options.breaking and options.feature:
        print('Cannot have both breaking and feature options.')
        sys.exit(1)
    utils.configure_logging()
    bumpversion = BumpVersion(
        breaking=options.breaking, feature=options.feature)
    bumpversion.run()
