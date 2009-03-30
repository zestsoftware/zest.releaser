import logging
import os
import sys
from zest.releaser import hg
from zest.releaser import svn

logger = logging.getLogger('chooser')


def version_control():
    """Return an object that provides the version control interface based
    on the detected version control system."""
    for dirpath, dirnames, filenames in os.walk('.'):
        if '.svn' in dirnames:
            return svn.Subversion()
        elif '.hg' in dirnames:
            return hg.Hg()
    else:
        logger.critical('No version control system detected.')
        sys.exit(1)
