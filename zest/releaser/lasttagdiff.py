# GPL, (c) Reinout van Rees
#
# Script to show the diff with the last relevant tag.
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
    logger.debug(u"Picked tag {0!r} for {1} (currently at {2!r}).".format(
                 full_tag, name, vcs.version))
    logger.info(
        u"Showing differences from the last commit against tag {0}".format(
            full_tag
        ))
    diff_command = vcs.cmd_diff_last_commit_against_tag(found)
    print(diff_command)
    print(execute_command(diff_command))
