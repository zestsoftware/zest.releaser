"""Do the checks and tasks that have to happen after doing a release.
"""

from packaging.version import parse as parse_version
from zest.releaser import baserelease
from zest.releaser import utils

import logging
import sys


logger = logging.getLogger(__name__)

HISTORY_HEADER = "%(clean_new_version)s (unreleased)"
COMMIT_MSG = "Bumped version for %(release)s release."

# Documentation for self.data.  You get runtime warnings when something is in
# self.data that is not in this list.  Embarrasment-driven documentation!
DATA = baserelease.DATA.copy()
DATA.update(
    {
        "breaking": "True if we handle a breaking (major) change",
        "clean_new_version": "Clean new version (say 1.1)",
        "feature": "True if we handle a feature (minor) change",
        "final": "True if we handle a final release",
        "release": "Type of release: breaking, feature, normal, final",
    }
)


class BumpVersion(baserelease.Basereleaser):
    """Add a changelog entry.

    self.data holds data that can optionally be changed by plugins.

    """

    def __init__(self, vcs=None, breaking=False, feature=False, final=False):
        baserelease.Basereleaser.__init__(self, vcs=vcs)
        # Prepare some defaults for potential overriding.
        if breaking:
            release = "breaking"
        elif feature:
            release = "feature"
        elif final:
            release = "final"
        else:
            release = "normal"
        self.data.update(
            dict(
                breaking=breaking,
                commit_msg=COMMIT_MSG,
                feature=feature,
                final=final,
                history_header=HISTORY_HEADER,
                release=release,
                update_history=True,
            )
        )

    def prepare(self):
        """Prepare self.data by asking about new dev version"""
        print("Checking version bump for {} release.".format(self.data["release"]))
        if not utils.sanity_check(self.vcs):
            logger.critical("Sanity check failed.")
            sys.exit(1)
        self._grab_version(initial=True)
        self._grab_history()
        # Grab and set new version.
        self._grab_version()

    def execute(self):
        """Make the changes and offer a commit"""
        if self.data["update_history"]:
            self._change_header()
        self._write_version()
        if self.data["update_history"]:
            self._write_history()
        self._diff_and_commit()

    def _grab_version(self, initial=False):
        """Grab the version.

        When initial is False, ask the user for a non-development
        version.  When initial is True, grab the current suggestion.

        """
        original_version = self.vcs.version
        logger.debug("Extracted version: %s", original_version)
        if not original_version:
            logger.critical("No version found.")
            sys.exit(1)
        suggestion = new_version = self.data.get("new_version")
        if not new_version:
            # Get a suggestion.
            breaking = self.data["breaking"]
            feature = self.data["feature"]
            final = self.data["final"]
            # Compare the suggestion for the last tag with the current version.
            # The wanted version bump may already have been done.
            last_tag_version = utils.get_last_tag(self.vcs, allow_missing=True)
            if last_tag_version is None:
                print("No tag found. No version bump needed.")
                sys.exit(0)
            else:
                print(f"Last tag: {last_tag_version}")
            print(f"Current version: {original_version}")
            params = dict(
                feature=feature,
                breaking=breaking,
                final=final,
                less_zeroes=self.zest_releaser_config.less_zeroes(),
                levels=self.zest_releaser_config.version_levels(),
                dev_marker=self.zest_releaser_config.development_marker(),
            )
            if final:
                minimum_version = utils.suggest_version(original_version, **params)
                if minimum_version is None:
                    print("No version bump needed.")
                    sys.exit(0)
            else:
                minimum_version = utils.suggest_version(last_tag_version, **params)
                if parse_version(minimum_version) <= parse_version(
                    utils.cleanup_version(original_version)
                ):
                    print("No version bump needed.")
                    sys.exit(0)
            # A bump is needed.  Get suggestion for next version.
            suggestion = utils.suggest_version(original_version, **params)
        if not initial:
            new_version = utils.ask_version("Enter version", default=suggestion)
        if not new_version:
            new_version = suggestion
        self.data["original_version"] = original_version
        self.data["new_version"] = new_version
        self.data["clean_new_version"] = utils.cleanup_version(new_version)


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
        help="Bump for feature release (increase minor version)",
    )
    parser.add_argument(
        "--breaking",
        action="store_true",
        dest="breaking",
        default=False,
        help="Bump for breaking release (increase major version)",
    )
    parser.add_argument(
        "--final",
        action="store_true",
        dest="final",
        default=False,
        help="Bump for final release (remove alpha/beta/rc from version)",
    )
    options = utils.parse_options(parser)
    # How many options are enabled?
    if len(list(filter(None, [options.breaking, options.feature, options.final]))) > 1:
        print("ERROR: Only enable one option of breaking/feature/final.")
        sys.exit(1)
    utils.configure_logging()
    bumpversion = BumpVersion(
        breaking=options.breaking,
        feature=options.feature,
        final=options.final,
    )
    bumpversion.run()
