# GPL, (c) Reinout van Rees
import logging
import os
import urllib2
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
    try:
        urllib2.urlopen(url)
        return True
    except urllib2.HTTPError, e:
        logger.debug("Package not found on pypi: %s", e)
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
        cmds = self.vcs.cmd_create_tag(self.data['version'])
        if not isinstance(cmds, list):
            cmds = [cmds]
        if len(cmds) == 1:
            print "Tag needed to proceed, you can use the following command:"
        for cmd in cmds:
            print cmd
            if utils.ask("Run this command"):
                print system(cmd)
            else:
                # all commands are needed in order to proceed normally
                print "Please create a tag for %s yourself and rerun." % \
                        (self.data['version'],)
                sys.exit()
        if not self.vcs.tag_exists(self.data['version']):
            print "\nFailed to create tag %s!" % (self.data['version'],)
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

    def _upload_distributions(self, package, sdist_options, pypiconfig):
        # See if creating an egg actually works.
        logger.info("Making an egg of a fresh tag checkout.")
        print system(utils.setup_py('sdist ' + sdist_options))

        # First ask if we want to upload to pypi, which should always
        # work, also without collective.dist.
        use_pypi = package_in_pypi(package)
        if use_pypi:
            logger.info("This package is registered on PyPI.")
        else:
            logger.warn("This package is NOT registered on PyPI.")
        if pypiconfig.is_old_pypi_config():
            pypi_command = 'register sdist %s upload' % sdist_options
            shell_command = utils.setup_py(pypi_command)
            if use_pypi:
                default = True
                exact = False
            else:
                # We are not yet on pypi.  To avoid an 'Oops...,
                # sorry!' when registering and uploading an internal
                # package we default to False here.
                default = False
                exact = True
            if utils.ask("Register and upload to PyPI", default=default,
                         exact=exact):
                logger.info("Running: %s", shell_command)
                result = system(shell_command)
                utils.show_first_and_last_lines(result)

        # If collective.dist is installed (or we are using
        # python2.6 or higher), the user may have defined
        # other servers to upload to.
        for server in pypiconfig.distutils_servers():
            if pypi.new_distutils_available():
                commands = ('register', '-r', server, 'sdist',
                            sdist_options, 'upload', '-r', server)
            else:
                ## This would be logical, given the lines above:
                #commands = ('mregister', '-r', server, 'sdist',
                #            sdist_options, 'mupload', '-r', server)
                ## But according to the collective.dist documentation
                ## it should be this (with just one '-r'):
                commands = ('mregister', 'sdist',
                            sdist_options, 'mupload', '-r', server)
            shell_command = utils.setup_py(' '.join(commands))
            default = True
            exact = False
            if server == 'pypi' and not use_pypi:
                # We are not yet on pypi.  To avoid an 'Oops...,
                # sorry!' when registering and uploading an internal
                # package we default to False here.
                default = False
                exact = True
            if utils.ask("Register and upload to %s" % server,
                         default=default, exact=exact):
                logger.info("Running: %s", shell_command)
                result = system(shell_command)
                utils.show_first_and_last_lines(result)

    def _release(self):
        """Upload the release, when desired"""
        if utils.TESTMODE:
            pypirc_old = pkg_resources.resource_filename(
                'zest.releaser.tests', 'pypirc_old.txt')
            pypiconfig = pypi.PypiConfig(pypirc_old)
        else:
            pypiconfig = pypi.PypiConfig()

        # Does the user normally want a real release?  We are
        # interested in getting a sane default answer here, so you can
        # override it in the exceptional case but just hit Enter in
        # the usual case.
        main_files = os.listdir(self.data['workingdir'])
        if 'setup.py' not in main_files and 'setup.cfg' not in main_files:
            # Neither setup.py nor setup.cfg, so this is no python
            # package, so at least a pypi release is not useful.
            # Expected case: this is a buildout directory.
            default_answer = False
        else:
            default_answer = pypiconfig.want_release()

        if not utils.ask("Check out the tag (for tweaks or pypi/distutils "
                         "server upload)", default=default_answer):
            return

        package = self.vcs.name
        version = self.data['version']
        logger.info("Doing a checkout...")
        self.vcs.checkout_from_tag(version)
        self.data['tagdir'] = os.path.realpath(os.getcwd())
        logger.info("Tag checkout placed in %s", self.data['tagdir'])

        # Possibly fix setup.cfg.
        setup_config = pypi.SetupConfig()
        if setup_config.has_bad_commands():
            logger.info("This is not advisable for a release.")
            if utils.ask("Fix %s (and commit to tag if possible)" %
                         setup_config.config_filename, default=True):
                # Fix the setup.cfg in the current working directory
                # so the current release works well.
                setup_config.fix_config()
                # Now we may want to commit this.  Note that this is
                # only really useful for subversion, as for example in
                # git you are in a detached HEAD state, which is a
                # place where a commit will be lost.
                #
                # Ah, in the case of bazaar doing a commit is actually
                # harmful, as the commit ends up on the tip, instead
                # of only being done on a tag or branch.
                #
                # So the summary is:
                #
                # - svn: NEEDED, not harmful
                # - git: not needed, not harmful
                # - hg: not needed, not harmful
                # - bzr: not needed, HARMFUL
                #
                # So for clarity and safety we should only do this for
                # subversion.
                if self.vcs.internal_filename == '.svn':
                    command = self.vcs.cmd_commit(
                        "Fixed %s on tag for release" %
                        setup_config.config_filename)
                    print system(command)
                else:
                    logger.debug("Not committing in non-svn repository as "
                                 "this is not needed or may be harmful.")

        sdist_options = self._sdist_options()
        # Run extra entry point
        self._run_entry_points('after_checkout')

        if 'setup.py' in os.listdir(self.data['tagdir']):
            if not pypiconfig.config:
                logger.warn("You must have a properly configured %s file in "
                            "your home dir to upload an egg.",
                            pypi.DIST_CONFIG_FILE)
            else:
                self._upload_distributions(package, sdist_options, pypiconfig)

        # Make sure we are in the expected directory again.
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
        return releaser.data.get('tagdir')
    else:
        tagdir = releaser.data.get('tagdir')
        if tagdir:
            logger.info("Reminder: tag checkout is in %s", tagdir)
