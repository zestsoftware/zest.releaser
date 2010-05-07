import logging
import os
import sys
from zest.releaser import git
from zest.releaser import hg
from zest.releaser import bzr
from zest.releaser import svn

logger = logging.getLogger('chooser')


def version_control():
    """Return an object that provides the version control interface based
    on the detected version control system."""
    curdir_contents = os.listdir('.')
    if '.svn' in curdir_contents:
        return svn.Subversion()
    elif '.hg' in curdir_contents:
        return hg.Hg()
    elif '.bzr' in curdir_contents:
        return bzr.Bzr()
    elif '.git' in curdir_contents:
        return git.Git()
    else:
        logger.critical('No version control system detected.')
        sys.exit(1)
