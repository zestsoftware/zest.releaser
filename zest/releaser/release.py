# GPL, (c) Reinout van Rees
import logging
import os
import urllib
import sys
import pkg_resources

from zest.releaser import baserelease
from zest.releaser import pypi
from zest.releaser import utils
from zest.releaser.utils import system

DATA = {
    # Documentation for self.data.  You get runtime warnings when something is
    # in self.data that is not in this list.  Embarrasment-driven
    # documentation!
    'workingdir': 'Original working directory',
    'name': 'Name of the project being released',
    'tagdir': '''Directory where the tag checkout is placed (*if* a tag
    checkout has been made)''',
    'version': "Version we're releasing",
    'tag_already_exists': "Internal detail, don't touch this :-)",
    }

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


class Releaser(baserelease.Basereleaser):
    """Release the project by tagging it and optionally uploading to pypi."""

    def __init__(self):
        baserelease.Basereleaser.__init__(self)
        # Prepare some defaults for potential overriding.
        self.data.update(dict(
            # Nothing yet
            ))

    def prepare(self):
        """Collect some data needed for releasing"""
        self._grab_version()
        self._check_if_tag_already_exists()

    def execute(self):
        """Do the actual releasing"""
        self._make_tag()
        self._release()

    def _grab_version(self):
        """Just grab the version"""
        version = self.vcs.version
        if not version:
            logger.critical("No version detected, so we can't do anything.")
            sys.exit()
        self.data['version'] = version

    def _check_if_tag_already_exists(self):
        """Check if tag already exists and show the difference if so"""
        version = self.data['version']
        if self.vcs.tag_exists(version):
            self.data['tag_already_exists'] = True
            q = ("There is already a tag %s, show "
                 "if there are differences?" % version)
            if utils.ask(q):
                diff_command = self.vcs.cmd_diff_last_commit_against_tag(
                    version)
                print diff_command
                print system(diff_command)
        else:
            self.data['tag_already_exists'] = False

    def _make_tag(self):
        if self.data['tag_already_exists']:
            return
        print "To tag, you can use the following command:"
        cmd = self.vcs.cmd_create_tag(self.data['version'])
        print cmd
        if utils.ask("Run this command"):
            print system(cmd)
        else:
            sys.exit()

    def _is_python24(self):
        return sys.hexversion < 0x02050000

    def _sdist_options(self):
        options = []
        if self._is_python24():
            # Due to a bug in python24, tar files might get corrupted.
            # We circumvent that by forcing zip files
            options.append('--formats=zip')
        return " ".join(options)

    def _release(self):
        """Upload the release, when desired"""
        if not utils.ask("Check out the tag (for tweaks or pypi/distutils "
                         "server upload)"):
            return
        package = self.vcs.name
        version = self.data['version']
        logger.info("Doing a checkout...")
        self.vcs.checkout_from_tag(version)
        tagdir = os.path.realpath(os.getcwd())
        logger.info("Tag checkout placed in %s", tagdir)
        sdist_options = self._sdist_options()

        if 'setup.py' in os.listdir(tagdir):
            # See if creating an egg actually works.
            logger.info("Making an egg of a fresh tag checkout.")
            print system(utils.setup_py('sdist ' + sdist_options))

            if utils.TESTMODE:
                pypirc_old = pkg_resources.resource_filename(
                    'zest.releaser.tests', 'pypirc_old.txt')
                pypiconfig = pypi.PypiConfig(pypirc_old)
            else:
                pypiconfig = pypi.PypiConfig()
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
                    if pypiconfig.is_old_pypi_config() and utils.ask(
                        "Register and upload to PyPI"):
                        result = system(
                            utils.setup_py('register sdist %s upload' %
                                           sdist_options))
                        utils.show_last_lines(result)

                # If collective.dist is installed (or we are using
                # python2.6 or higher), the user may have defined
                # other servers to upload to.
                for server in pypiconfig.distutils_servers():
                    if server == 'pypi' and not use_pypi:
                        continue
                    if utils.ask("Register and upload to %s" % server):
                        if pypi.new_distutils_available():
                            result = system(
                                utils.setup_py('register sdist %s upload -r %s'
                                               % (sdist_options, server)))
                        else:
                            result = system(
                                utils.setup_py('mregister sdist %s mupload '
                                               '-r %s'
                                               % (sdist_options, server)))
                        utils.show_last_lines(result)

        os.chdir(self.vcs.workingdir)


def datacheck(data):
    """Entrypoint: ensure that the data dict is fully documented"""
    utils.is_data_documented(data, documentation=DATA)


def main(return_tagdir=False):
    logging.basicConfig(level=utils.loglevel(),
                        format="%(levelname)s: %(message)s")
    releaser = Releaser()
    releaser.run()
    if return_tagdir:
        # At the end, for the benefit of fullrelease.
        return getattr(releaser, 'tagdir', None)
