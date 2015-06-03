# GPL, (c) Reinout van Rees
#
# Script to show the log from the last relevant tag till now.
import logging
import sys

import zest.releaser.choose
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
    logger.info(u"Showing log since tag {0} and the last commit.".format(
                full_tag))
    log_command = vcs.cmd_log_since_tag(found)
    print(utils.cmd_to_text(log_command))
    print(utils.execute_command(log_command))
