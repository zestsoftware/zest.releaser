#! /usr/bin/env python2.4
# GPL, (c) Reinout van Rees
#
# Script to show the diff with the last relevant tag.
from commands import getoutput
from pkg_resources import parse_version
import logging
import os
import sys

import utils

logger = logging.getLogger('lasttagdiff')


def main():
    logging.basicConfig(level=utils.loglevel(),
                        format="%(levelname)s: %(message)s")
    version = utils.extract_version()
    if not version:
        logger.critical("No version detected, so we can't do anything.")
        sys.exit()
    available_tags = utils.available_tags()
    if not available_tags:
        logger.critical("No tags found, so we can't do anything.")
        sys.exit()

    # Mostly nicked from zest.stabilizer.

    # We seek a tag that's the same or less than the version as determined
    # by setuptools' version parsing. A direct match is obviously
    # right. The 'less' approach handles development eggs that have
    # already been switched back to development.
    available_tags.reverse()
    found = available_tags[0]
    parsed_version = parse_version(version)
    for tag in available_tags:
        parsed_tag = parse_version(tag)
        parsed_found = parse_version(found)
        if parsed_tag == parsed_version:
            found = tag
            logger.debug("Found exact match: %s", found)
            break
        if (parsed_tag >= parsed_found and
            parsed_tag < parsed_version):
            logger.debug("Found possible lower match: %s", tag)
            found = tag
    url = utils.svn_info()
    name, base = utils.extract_name_and_base(url)
    full_tag = base + 'tags/' + found
    logger.debug("Picked tag %r for %s (currently at %r).",
                 full_tag, name, version)

    # End of nicking from zest.stabilizer.

    logger.info("Showing differences of trunk with %s", full_tag)
    logger.info("Note: trunk on the server, so uncommitted changes won't "
                "show up.")
    diff_command = "svn diff %s %s" % (full_tag, url)
    print getoutput(diff_command)
    
