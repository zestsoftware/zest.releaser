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
import pypi

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
        package = vcs.name
        prefix = '%s-%s-' % (package, version)
        logger.info("Doing a checkout...")
        tagdir = vcs.prepare_checkout_dir(prefix)
        cmd = vcs.cmd_checkout_from_tag(version, tagdir)
        print getoutput(cmd)
        logger.info("Tag checkout placed in %s", tagdir)

        if 'setup.py' in os.listdir(tagdir):
            # See if creating an egg actually works.
            os.chdir(tagdir)
            logger.info("Making an egg of a fresh tag checkout.")
            print getoutput('%s setup.py sdist' % sys.executable)

            config = pypi.get_pypi_config()
            if not config:
                logger.warn("You must have a properly configured %s file in "
                            "your home dir to upload an egg.",
                            pypi.DIST_CONFIG_FILE)
            else:
                # First ask if we want to upload to pypi, which should
                # always work, also without collective.dist.
                use_pypi = pypi.package_in_pypi(package)
                if not use_pypi:
                    logger.info("This package is currently NOT registered on "
                                "PyPI. If you want to register, you need to "
                                "do this manually the first time.")
                else:
                    logger.info("This package is registered on PyPI.")
                    if pypi.has_old_pypi_config(config) and utils.ask(
                        "Register and upload to PyPI"):
                        result = getoutput('%s setup.py register sdist upload'
                                           % sys.executable)
                        utils.show_last_lines(result)

                # If collective.dist is installed, the user may have
                # defined other servers to upload to.
                # XXX Check what needs to be done with python 2.6, where
                # collective.dist is not needed anymore as it is built-in.
                for server in pypi.get_distutils_servers(config):
                    if server == 'pypi' and not use_pypi:
                        continue
                    if utils.ask("Register and upload to %s" % server):
                        result = getoutput(
                            '%s setup.py mregister sdist mupload -r %s'
                            % (sys.executable, server))
                        utils.show_last_lines(result)

        os.chdir(original_dir)
        if return_tagdir:
            # At the end, for the benefit of fullrelease.
            return tagdir
