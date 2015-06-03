"""Do the prerelease, actual release and post release in one fell swoop!
"""
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
    logger.info(u'Starting prerelease.')
    original_dir = os.getcwd()
    prerelease.main()
    os.chdir(original_dir)
    logger.info(u'Starting release.')
    tagdir = release.main(return_tagdir=True)
    os.chdir(original_dir)
    logger.info(u'Starting postrelease.')
    postrelease.main()
    os.chdir(original_dir)
    logger.info(u'Finished full release.')
    if tagdir:
        logger.info(u"Reminder: tag checkout is in {0}".format(tagdir))
