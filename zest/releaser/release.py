# GPL, (c) Reinout van Rees
import commands
import logging
import os
import sys

from zest.releaser import choose
from zest.releaser import pypi
from zest.releaser import utils

logger = logging.getLogger('release')


def package_in_pypi(package):
    """Check whether the package is registered on pypi"""
    url = 'http://pypi.python.org/simple/%s' % package
    result = urllib.urlopen(url).read().strip()
    if package in result:
        # Some link with the package name is present. If the package doesn't
        # exist on pypi, the result would be the *string* 'Not Found'.
        return True
    else:
        logger.debug("Package not found on pypi: %r", result)
        return False


def main(return_tagdir=False):
    vcs = choose.version_control()

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
            print commands.getoutput(diff_command)
    else:
        print "To tag, you can use the following command:"
        cmd = vcs.cmd_create_tag(version)
        print cmd
        if utils.ask("Run this command"):
            print commands.getoutput(cmd)
        else:
            sys.exit()

    # Check out tag in temp dir
    if utils.ask("Check out the tag (for tweaks or pypi/distutils "
                 "server upload)"):
        package = vcs.name
        prefix = '%s-%s-' % (package, version)
        logger.info("Doing a checkout...")
        tagdir = vcs.prepare_checkout_dir(prefix)
        os.chdir(tagdir)
        cmd = vcs.cmd_checkout_from_tag(version, tagdir)
        print commands.getoutput(cmd)
        logger.info("Tag checkout placed in %s", tagdir)

        if 'setup.py' in os.listdir(tagdir):
            # See if creating an egg actually works.
            logger.info("Making an egg of a fresh tag checkout.")
            print commands.getoutput('%s setup.py sdist' % sys.executable)

            pypiconfig = pypi.Pypyconfig()
            if not pypiconfig.config:
                logger.warn("You must have a properly configured %s file in "
                            "your home dir to upload an egg.",
                            pypi.DIST_CONFIG_FILE)
                # TODO: when refactoring, zap the "else" and just put a
                # "return" here.
            else:
                # First ask if we want to upload to pypi, which should always
                # work, also without collective.dist.
                use_pypi = package_in_pypi(package)
                if not use_pypi:
                    logger.info("This package is currently NOT registered on "
                                "PyPI. If you want to register, you need to "
                                "do this manually the first time.")
                else:
                    logger.info("This package is registered on PyPI.")
                    if pypiconfig.has_old_pypi_config() and utils.ask(
                        "Register and upload to PyPI"):
                        result = commands.getoutput(
                            '%s setup.py register sdist upload'
                            % sys.executable)
                        utils.show_last_lines(result)

                # If collective.dist is installed (or we are using
                # python2.6 or higher), the user may have defined
                # other servers to upload to.
                for server in pypiconfig.distutils_servers():
                    if server == 'pypi' and not use_pypi:
                        continue
                    if utils.ask("Register and upload to %s" % server):
                        if sys.version_info[:2] >= (2, 6):
                            result = commands.getoutput(
                                '%s setup.py register sdist upload -r %s'
                                % (sys.executable, server))
                        else:
                            result = commands.getoutput(
                                '%s setup.py mregister sdist mupload -r %s'
                                % (sys.executable, server))
                        utils.show_last_lines(result)

        os.chdir(original_dir)
        if return_tagdir:
            # At the end, for the benefit of fullrelease.
            return tagdir
