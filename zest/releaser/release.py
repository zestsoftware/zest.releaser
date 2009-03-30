#! /usr/bin/env python2.4
# GPL, (c) Reinout van Rees
#
# Script to tag releases.
import logging
from commands import getoutput
import os
import sys
import zest.releaser.choose
import utils

logger = logging.getLogger('release')


def main(return_tagdir=False):
    vcs = zest.releaser.choose.version_control()

    original_dir = os.getcwd()
    logging.basicConfig(level=utils.loglevel(),
                        format="%(levelname)s: %(message)s")

    version = vcs.version
    if not version:
        logger.critical("No version detected, so we can't do anything.")
        sys.exit()

    # check if a tag already exists
    if vcs.tag_exists(version):
        q = ("There is already a tag %s, show "
             "if there are differences?" % version)
        if utils.ask(q):
            diff_command = vcs.cmd_diff_last_commit_against_tag(version)
            print diff_command
            print getoutput(diff_command)
    else:
        print "To tag, you can use the following command:"
        cmd = vcs.cmd_create_tag(version)
        print cmd
        if utils.ask("Run this command"):
            print getoutput(cmd)
        else:
            sys.exit()

    # Check out tag in temp dir
    if utils.ask("Check out the tag (for tweaks or pypi upload)"):
        prefix = '%s-%s-' % (vcs.name, version)
        logger.info("Doing a checkout...")
        tagdir = vcs.prepare_checkout_dir(prefix)
        cmd = vcs.cmd_checkout_from_tag(version, tagdir)
        print getoutput(cmd)
        logger.info("Tag checkout placed in %s", tagdir)

        if utils.package_in_pypi(vcs.name):
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
            logger.info("We're not registered with PyPI.")
        os.chdir(original_dir)
        if return_tagdir:
            # At the end, for the benefit of fullrelease.
            return tagdir
