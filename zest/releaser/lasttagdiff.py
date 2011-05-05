#! /usr/bin/env python2.4
# GPL, (c) Reinout van Rees
#
# Script to show the diff with the last relevant tag.
import logging
import sys

import zest.releaser.choose
from zest.releaser.utils import system
from zest.releaser import utils

logger = logging.getLogger('lasttagdiff')


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
    logger.info("Showing differences from the last commit against tag %s",
                full_tag)
    diff_command = vcs.cmd_diff_last_commit_against_tag(found)
    print diff_command
    print system(diff_command)
