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
    if '.svn' in curdir_contents:
        return svn.Subversion()
    elif '.hg' in curdir_contents:
        return hg.Hg()
    elif '.bzr' in curdir_contents:
        return bzr.Bzr()
    elif '.git' in curdir_contents:
        return git.Git()
    else:
        # Try finding an svn checkout *not* in the root.
        last_try = utils.system("svn info")
        if 'Repository' in last_try:
            return svn.Subversion()
        # true means that we are in the work tree, false that we are in the
        # .git tree. If we are not in a git repository, the answer will looks
        # like 'Not a git repository' or even 'git: not found'
        last_try = utils.system("git  rev-parse --is-inside-work-tree")
        if last_try in ['true\n', 'false\n']:
            return git.Git()
        logger.critical('No version control system detected.')
        sys.exit(1)
