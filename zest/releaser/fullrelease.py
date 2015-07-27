"""Do the prerelease, actual release and post release in one fell swoop!
"""
from __future__ import unicode_literals

import logging
import os

from zest.releaser import prerelease
from zest.releaser import release
from zest.releaser import postrelease
from zest.releaser import utils

logger = logging.getLogger(__name__)


def main():
    utils.parse_options()
    utils.configure_logging()
    logger.info('Starting prerelease.')
    original_dir = os.getcwd()
    # prerelease
    prereleaser = prerelease.Prereleaser()
    prereleaser.run()
    logger.info('Starting release.')
    # release
    releaser = release.Releaser(vcs=prereleaser.vcs)
    releaser.run()
    tagdir = releaser.data.get('tagdir')
    logger.info('Starting postrelease.')
    # postrelease
    postreleaser = postrelease.Postreleaser(vcs=releaser.vcs)
    postreleaser.run()
    os.chdir(original_dir)
    logger.info('Finished full release.')
    if tagdir:
        logger.info("Reminder: tag checkout is in %s", tagdir)
