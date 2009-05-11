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

from ConfigParser import ConfigParser
try:
    from collective.dist import mupload
    collective_dist = True
except ImportError:
    collective_dist = False

index_servers = []
DIST_CONFIG_FILE = '.pypirc'

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
    if utils.ask("Check out the tag (for tweaks or pypi/distutils "
                 "server upload)"):
        prefix = '%s-%s-' % (vcs.name, version)
        logger.info("Doing a checkout...")
        tagdir = vcs.prepare_checkout_dir(prefix)
        cmd = vcs.cmd_checkout_from_tag(version, tagdir)
        print getoutput(cmd)
        logger.info("Tag checkout placed in %s", tagdir)
        if 'setup.py' in os.listdir(tagdir):
            os.chdir(tagdir)
            logger.info("Making an egg of a fresh tag checkout.")
            print getoutput('%s setup.py sdist' % sys.executable)
            # First ask if we want to upload to pypi, which should
            # always work, also without collective.dist
            if utils.package_in_pypi(vcs.name):
                logger.info("We are on PYPI.")
                default = True
            else:
                logger.info("We are currently NOT registered with PyPI.")
                default = False
            if utils.ask("Register and upload to PyPI", default=default):
                result = getoutput('%s setup.py register sdist upload' %
                                   sys.executable)
                utils.show_last_lines(result)

            # If collective.dist is installed, the user may have
            # defined other servers to upload to.
            # XXX Check what needs to be done with python 2.6, where
            # collective.dist is not needed anymore as it is built-in.
            rc = os.path.join(os.path.expanduser('~'), DIST_CONFIG_FILE)
            if collective_dist and os.path.exists(rc):
                config = ConfigParser()
                config.read(rc)
                raw_index_servers = config.get('distutils', 'index-servers')
                # We have already asked about uploading to pypi.
                index_servers = [
                    server.strip() for server in raw_index_servers.split('\n')
                    if server.strip() not in ('', 'pypi')]
                for server in index_servers:
                    if utils.ask("Register and upload to %s" % server):
                        result = getoutput(
                            '%s setup.py mregister sdist mupload -r %s'
                            % (sys.executable, server))
                        utils.show_last_lines(result)

        os.chdir(original_dir)
        if return_tagdir:
            # At the end, for the benefit of fullrelease.
            return tagdir
