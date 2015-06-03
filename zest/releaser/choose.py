import logging
import os
import sys
from zest.releaser import git
from zest.releaser import hg
from zest.releaser import bzr
from zest.releaser import svn
from zest.releaser import utils

logger = logging.getLogger(__name__)


def version_control():
    """Return an object that provides the version control interface based
    on the detected version control system."""
    curdir_contents = os.listdir('.')
    if u'.svn' in curdir_contents:
        return svn.Subversion()
    elif u'.hg' in curdir_contents:
        return hg.Hg()
    elif u'.bzr' in curdir_contents:
        return bzr.Bzr()
    elif u'.git' in curdir_contents:
        return git.Git()
    else:
        # Try finding an svn checkout *not* in the root.
        last_try = utils.execute_command([u"svn", u"info"])
        if u'Repository' in last_try:
            return svn.Subversion()
        logger.critical(u'No version control system detected.')
        sys.exit(1)
