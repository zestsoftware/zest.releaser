# GPL, (c) Reinout van Rees
from __future__ import unicode_literals

import logging
import os
import sys

from six.moves.urllib.error import HTTPError
from six.moves.urllib import request as urllib2

from zest.releaser import baserelease
from zest.releaser import pypi
from zest.releaser import utils
from zest.releaser.utils import execute_command

DATA = {
    # Documentation for self.data.  You get runtime warnings when something is
    # in self.data that is not in this list.  Embarrasment-driven
    # documentation!
    'workingdir': 'Original working directory',
    'reporoot': 'Root of the version control repository',
    'name': 'Name of the project being released',
    'tagdir': '''Directory where the tag checkout is placed (*if* a tag
    checkout has been made)''',
    'tagworkingdir': '''Working directory inside the tag checkout. This is
    the same, except when you make a release from within a sub directory.
    We then make sure you end up in the same relative directory after a
    checkout is done.''',
    'version': "Version we're releasing",
    'tag_already_exists': "Internal detail, don't touch this :-)",
}

logger = logging.getLogger(__name__)


def package_in_pypi(package):
    """Check whether the package is registered on pypi"""
    url = 'https://pypi.python.org/simple/%s' % package
    try:
        urllib2.urlopen(url)
        return True
    except HTTPError as e:
        logger.debug("Package not found on pypi: %s", e)
        return False


class Releaser(baserelease.Basereleaser):
    """Release the project by tagging it and optionally uploading to pypi."""

    def __init__(self, vcs=None):
        baserelease.Basereleaser.__init__(self, vcs=vcs)
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
                print(diff_command)
                print(execute_command(diff_command))
        else:
            self.data['tag_already_exists'] = False

    def _make_tag(self):
        if self.data['tag_already_exists']:
            return
        cmds = self.vcs.cmd_create_tag(self.data['version'])
        if not isinstance(cmds, list):
            cmds = [cmds]
        if len(cmds) == 1:
            print("Tag needed to proceed, you can use the following command:")
        for cmd in cmds:
            print(cmd)
            if utils.ask("Run this command"):
                print(execute_command(cmd))
            else:
                # all commands are needed in order to proceed normally
                print("Please create a tag for %s yourself and rerun." %
                      (self.data['version'],))
                sys.exit(1)
        if not self.vcs.tag_exists(self.data['version']):
            print("\nFailed to create tag %s!" % (self.data['version'],))
            sys.exit(1)

    def _upload_distributions(self, package):
        # See if creating an sdist (and maybe a wheel) actually works.
        # Also, this makes the sdist (and wheel) available for plugins.
        # And for twine, who will just upload the created files.
        logger.info(
            "Making a source distribution of a fresh tag checkout (in %s).",
            self.data['tagworkingdir'])
        result = utils.execute_command(utils.setup_py('sdist'))
        utils.show_interesting_lines(result)
        if self.pypiconfig.create_wheel():
            logger.info("Making a wheel of a fresh tag checkout (in %s).",
                        self.data['tagworkingdir'])
            result = utils.execute_command(utils.setup_py('bdist_wheel'))
        utils.show_interesting_lines(result)
        if not self.pypiconfig.is_pypi_configured():
            logger.warn("You must have a properly configured %s file in "
                        "your home dir to upload to a package index.",
                        pypi.DIST_CONFIG_FILE)
            return

        # Get list of all files to upload.
        files_in_dist = [
            os.path.join('dist', filename) for filename in os.listdir('dist')]

        # Is this package already registered on pypi?
        on_pypi = package_in_pypi(package)

        # Run extra entry point
        self._run_hooks('before_upload')

        # Get servers/repositories.
        if self.pypiconfig.is_old_pypi_config():
            servers = ['pypi']
        else:
            # The user may have defined other servers to upload to.
            servers = self.pypiconfig.distutils_servers()

        for server in servers:
            if server == 'pypi' and on_pypi:
                logger.info("This package is registered on PyPI.")
                # Already registered on PyPI.  Uploading is enough.
                do_register = False
                question = "Upload"
            else:
                # We must register first.
                do_register = True
                question = "Register and upload"
            default = True
            exact = False
            if server == 'pypi' and not on_pypi:
                logger.info("This package is NOT registered on PyPI.")
                # We are not yet on pypi.  To avoid an 'Oops...,
                # sorry!' when registering and uploading an internal
                # package we default to False here.
                default = False
                exact = True
            if utils.ask("%s to %s" % (question, server),
                         default=default, exact=exact):
                if do_register:
                    logger.info("Registering...")
                    utils.retry_twine('register', server, *files_in_dist)
                utils.retry_twine('upload', server, *files_in_dist)

    def _release(self):
        """Upload the release, when desired"""
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
            default_answer = self.pypiconfig.want_release()

        if not utils.ask("Check out the tag (for tweaks or pypi/distutils "
                         "server upload)", default=default_answer):
            return

        package = self.vcs.name
        version = self.data['version']
        logger.info("Doing a checkout...")
        self.vcs.checkout_from_tag(version)
        # ^^^ This changes directory to a temp folder.
        self.data['tagdir'] = os.path.realpath(os.getcwd())
        logger.info("Tag checkout placed in %s", self.data['tagdir'])
        if self.vcs.relative_path_in_repo:
            # We were in a sub directory of the repo when we started
            # the release, so we go to the same relative sub
            # directory.
            tagworkingdir = os.path.realpath(
                os.path.join(os.getcwd(), self.vcs.relative_path_in_repo))
            os.chdir(tagworkingdir)
            self.data['tagworkingdir'] = tagworkingdir
            logger.info("Changing to sub directory in tag checkout: %s",
                        self.data['tagworkingdir'])
        else:
            # The normal case.
            self.data['tagworkingdir'] = self.data['tagdir']

        # Possibly fix setup.cfg.
        if self.setup_cfg.has_bad_commands():
            logger.info("This is not advisable for a release.")
            if utils.ask("Fix %s (and commit to tag if possible)" %
                         self.setup_cfg.config_filename, default=True):
                # Fix the setup.cfg in the current working directory
                # so the current release works well.
                self.setup_cfg.fix_config()
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
                        self.setup_cfg.config_filename)
                    print(execute_command(command))
                else:
                    logger.debug("Not committing in non-svn repository as "
                                 "this is not needed or may be harmful.")

        # Run extra entry point
        self._run_hooks('after_checkout')

        if 'setup.py' in os.listdir(self.data['tagworkingdir']):
            self._upload_distributions(package)

        # Make sure we are in the expected directory again.
        os.chdir(self.vcs.workingdir)


def datacheck(data):
    """Entrypoint: ensure that the data dict is fully documented"""
    utils.is_data_documented(data, documentation=DATA)


def main():
    utils.parse_options()
    utils.configure_logging()
    releaser = Releaser()
    releaser.run()
    tagdir = releaser.data.get('tagdir')
    if tagdir:
        logger.info("Reminder: tag checkout is in %s", tagdir)
