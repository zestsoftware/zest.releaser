# GPL, (c) Reinout van Rees
#
# Script to show the log from the last relevant tag till now.
from __future__ import unicode_literals

import logging
import sys

import zest.releaser.choose
from zest.releaser.utils import execute_command
from zest.releaser import utils

logger = logging.getLogger(__name__)


def main():
    utils.configure_logging()
    vcs = zest.releaser.choose.version_control()
    if len(sys.argv) > 1:
        found = sys.argv[-1]
    else:
        found = utils.get_last_tag(vcs)
    name = vcs.name
    full_tag = vcs.tag_url(found)
    logger.debug("Picked tag %r for %s (currently at %r).",
                 full_tag, name, vcs.version)
    logger.info("Showing log since tag %s and the last commit.",
                full_tag)
    log_command = vcs.cmd_log_since_tag(found)
    print(log_command)
    print(execute_command(log_command))
