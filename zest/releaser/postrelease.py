"""Do the checks and tasks that have to happen after doing a release.
"""
from __future__ import unicode_literals

import logging
import sys

from zest.releaser import baserelease
from zest.releaser import utils

logger = logging.getLogger(__name__)

HISTORY_HEADER = '%(new_version)s (unreleased)'
COMMIT_MSG = 'Back to development: %(new_version)s'
DEV_VERSION_TEMPLATE = '%(new_version)s%(development_marker)s'

# Documentation for self.data.  You get runtime warnings when something is in
# self.data that is not in this list.  Embarrasment-driven documentation!
DATA = baserelease.DATA.copy()
DATA.update({
    'dev_version': 'New version with development marker (so 1.1.dev0)',
    'dev_version_template': 'Template for development version number',
    'development_marker': 'String to be appended to version after postrelease',
    'new_version': 'New version, without development marker (so 1.1)',
})


class Postreleaser(baserelease.Basereleaser):
    """Post-release tasks like resetting version number.

    self.data holds data that can optionally be changed by plugins.

    """

    def __init__(self, vcs=None):
        baserelease.Basereleaser.__init__(self, vcs=vcs)
        # Prepare some defaults for potential overriding.
        self.data.update(dict(
            commit_msg=COMMIT_MSG,
            dev_version_template=DEV_VERSION_TEMPLATE,
            development_marker=self.pypiconfig.development_marker(),
            history_header=HISTORY_HEADER,
        ))

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
        suggestion = utils.suggest_version(
            current,
            less_zeroes=self.pypiconfig.less_zeroes(),
            levels=self.pypiconfig.version_levels(),
            dev_marker=self.pypiconfig.development_marker(),
        )
        print("Current version is %s" % current)
        q = ("Enter new development version "
             "('%(development_marker)s' will be appended)" % self.data)
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
