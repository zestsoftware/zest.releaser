#! /usr/bin/env python2.4
# GPL, (c) Reinout van Rees
#
# Script to show the log from the last relevant tag till now.
import logging
import sys

import zest.releaser.choose
from zest.releaser.utils import system
from zest.releaser import utils

logger = logging.getLogger('lasttaglog')


def main():
    logging.basicConfig(level=utils.loglevel(),
                        format="%(levelname)s: %(message)s")
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
    print log_command
    print system(log_command)
