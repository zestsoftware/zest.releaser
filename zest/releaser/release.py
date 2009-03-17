#! /usr/bin/env python2.4
# GPL, (c) Reinout van Rees
#
# Script to tag releases.
import logging
from commands import getoutput
import os
import sys
from tempfile import mkdtemp

import utils

logger = logging.getLogger('release')


def main(return_tagdir=False):
    original_dir = os.getcwd()
    logging.basicConfig(level=utils.loglevel(),
                        format="%(levelname)s: %(message)s")
    url = utils.svn_info()
    name, base = utils.extract_name_and_base(url)
    version = utils.extract_version()
    tags = utils.available_tags()
    if not version:
        logger.critical("No version detected, so we can't do anything.")
        sys.exit()

    tag_url = base + 'tags/' + version
    if version in tags:
        q = ("There is already a tag %s, show "
             "if there are differences?" % version)
        if utils.ask(q):
            diff_command = "svn diff %s %s" % (tag_url, url)
            print diff_command
            print getoutput(diff_command)
    else:
        print "To tag, you can use the following command:"
        cmd = 'svn cp %s %s -m "Tagging %s"' % (url, tag_url,
                                                version)
        print cmd
        if utils.ask("Run this command"):
            print getoutput(cmd)
        else:
            sys.exit()

    # Check out tag in temp dir
    if utils.ask("Check out the tag (for tweaks or pypi upload)"):
        prefix = '%s-%s-' % (name, version)
        tagdir = mkdtemp(prefix=prefix)
        logger.info("Doing a checkout...")
        print getoutput('svn co %s %s' % (tag_url, tagdir))
        logger.info("Tag checkout placed in %s", tagdir)

        if utils.package_in_pypi(name):
            if utils.ask("We're on PYPI: make an egg of a fresh tag checkout"):
                os.chdir(tagdir)
                logger.info("Making egg...")
                print getoutput('%s setup.py sdist' % sys.executable)

                if utils.ask("Register and upload to pypi"):
                    result = getoutput(
                        '%s setup.py register sdist upload' % sys.executable)
                    lines = [line for line in result.split('\n')]
                    print 'Showing last few lines...'
                    for line in lines[-5:]:
                        print line
        else:
            logger.info("We're not registered with the cheeseshop.")
        os.chdir(original_dir)
        if return_tagdir:
            # At the end, for the benefit of fullrelease.
            return tagdir
