# GPL, (c) Reinout van Rees
import logging
import os
import urllib2
import sys

from zest.releaser import baserelease
from zest.releaser import pypi
from zest.releaser import utils
from zest.releaser.utils import execute_command

DATA = {
    # Documentation for self.data.  You get runtime warnings when something is
    # in self.data that is not in this list.  Embarrasment-driven
    # documentation!
    'workingdir': u'Original working directory',
    'name': u'Name of the project being released',
    'tagdir': u'''Directory where the tag checkout is placed (*if* a tag
    checkout has been made)''',
    'version': u"Version we're releasing",
    'tag_already_exists': u"Internal detail, don't touch this :-)",
}

logger = logging.getLogger(__name__)


def package_in_pypi(package):
    """Check whether the package is registered on pypi"""
    url = u'https://pypi.python.org/simple/{0!s}'.format(package)
    try:
        urllib2.urlopen(url)
        return True
    except urllib2.HTTPError, e:
        logger.debug(u"Package not found on pypi: {0!s}".format(e))
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
            logger.critical(u"No version detected, so we can't do anything.")
            sys.exit(1)
        self.data['version'] = version

    def _check_if_tag_already_exists(self):
        """Check if tag already exists and show the difference if so"""
        version = self.data['version']
        if self.vcs.tag_exists(version):
            self.data['tag_already_exists'] = True
            q = (u"There is already a tag {0}, show "
                 u"if there are differences?").format(version)
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
        if len(cmds) == 1:
            print(u"Tag needed to proceed, you can use the following command:")
        for cmd in cmds:
            print(utils.cmd_to_text(cmd))
            if utils.ask(u"Run this command"):
                print(execute_command(cmd))
            else:
                # all commands are needed in order to proceed normally
                print(
                    u"Please create a tag for {0} yourself and rerun.".format(
                        self.data['version']
                    ))
                sys.exit(1)
        if not self.vcs.tag_exists(self.data['version']):
            print(u"\nFailed to create tag {0}!".format(self.data['version']))
            sys.exit(1)

    def _pypi_command(self, command):
        """Run a command that accesses PyPI or similar.

        We offer to retry the command if it fails.
        """
        try:
            # Note that if something goes wrong, it may just be
            # because we detect a warning: the command may have
            # succeeded after all.  So the fail message is a bit
            # cautious.
            result = utils.execute_command(
                command, allow_retry=True,
                fail_message=u"Package upload may have failed.")
        except utils.CommandException:
            logger.error(u"Command failed: %r", command)
            tagdir = self.data.get('tagdir')
            if tagdir:
                logger.info((
                    u"Note: we have placed a fresh tag checkout in {0}. You "
                    u"can retry uploading from there if needed."
                    ).format(tagdir))
            sys.exit(1)
        return result

    def _upload_distributions(self, package):
        # See if creating an sdist (and maybe a wheel) actually works.
        # Also, this makes the sdist (and wheel) available for plugins.
        # And for twine, who will just upload the created files.
        logger.info((
            u"Making a source distribution of a fresh tag checkout (in {0})."
            ).format(self.data['tagdir']))
        result = utils.execute_command(utils.setup_py([u'sdist']))
        utils.show_interesting_lines(result)
        if self.pypiconfig.create_wheel():
            logger.info(
                u"Making a wheel of a fresh tag checkout (in {0}).".format(
                    self.data['tagdir']
                ))
            result = utils.execute_command(utils.setup_py([u'bdist_wheel']))
        utils.show_interesting_lines(result)
        if not self.pypiconfig.is_pypi_configured():
            logger.warn((
                u"You must have a properly configured %s file in your home "
                u"dir to upload to a package index.").format(
                    pypi.DIST_CONFIG_FILE
                ))
            return

        # If twine is available, we prefer it for uploading.  But:
        # currently, when a package is not yet registered, twine
        # upload will fail.
        use_twine = utils.has_twine()

        # First ask if we want to upload to pypi.
        use_pypi = package_in_pypi(package)
        if use_pypi:
            logger.info(u"This package is registered on PyPI.")
        else:
            logger.warn(u"This package is NOT registered on PyPI.")
            if use_twine:
                logger.warn(u"Please login and manually register this "
                            u"package on PyPI first.")

        # Run extra entry point
        self._run_hooks('before_upload')

        if self.pypiconfig.is_old_pypi_config():
            if use_twine:
                shell_command = utils.twine_command([
                    u'upload', u'dist{0}*'.format(os.path.sep)
                    ])
            else:
                if self.pypiconfig.create_wheel():
                    pypi_command = [
                        u'register', u'sdist', u'bdist', u'wheel', u'upload'
                        ]
                else:
                    pypi_command = [u'register', u'sdist', u'upload']
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
            if utils.ask(u"Register and upload to PyPI", default=default,
                         exact=exact):
                logger.info(u"Running: {0}".format(shell_command))
                self._pypi_command(shell_command)

        # The user may have defined other servers to upload to.
        for server in self.pypiconfig.distutils_servers():
            if use_twine:
                shell_command = utils.twine_command([
                    u'upload', u'dist{0}*'.format(os.path.sep), u'-r', server
                    ])
            else:
                if self.pypiconfig.create_wheel():
                    commands = [u'register', u'-r', server, u'sdist',
                                u'bdist_wheel',
                                u'upload', u'-r', server]
                else:
                    commands = [u'register', u'-r', server, u'sdist',
                                u'upload', u'-r', server]
                shell_command = utils.setup_py(commands)
            default = True
            exact = False
            if server == 'pypi' and not use_pypi:
                # We are not yet on pypi.  To avoid an 'Oops...,
                # sorry!' when registering and uploading an internal
                # package we default to False here.
                default = False
                exact = True
            if utils.ask(u"Register and upload to {0}".format(server),
                         default=default, exact=exact):
                logger.info(u"Running: {0}".format(shell_command))
                self._pypi_command(shell_command)

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

        if not utils.ask(u"Check out the tag (for tweaks or pypi/distutils "
                         u"server upload)", default=default_answer):
            return

        package = self.vcs.name
        version = self.data['version']
        logger.info(u"Doing a checkout...")
        self.vcs.checkout_from_tag(version)
        # ^^^ This changes directory to a temp folder.
        self.data['tagdir'] = os.path.realpath(os.getcwd())
        logger.info(u"Tag checkout placed in {0}".format(self.data['tagdir']))

        # Possibly fix setup.cfg.
        if self.setup_cfg.has_bad_commands():
            logger.info(u"This is not advisable for a release.")
            if utils.ask(
                    u"Fix {0} (and commit to tag if possible)".format(
                        self.setup_cfg.config_filename
                    ), default=True):

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
                        u"Fixed {0} on tag for release".format(
                            self.setup_cfg.config_filename
                        ))
                    print(execute_command(command))
                else:
                    logger.debug(u"Not committing in non-svn repository as "
                                 u"this is not needed or may be harmful.")

        # Run extra entry point
        self._run_hooks('after_checkout')

        if 'setup.py' in os.listdir(self.data['tagdir']):
            self._upload_distributions(package)

        # Make sure we are in the expected directory again.
        os.chdir(self.vcs.workingdir)


def datacheck(data):
    """Entrypoint: ensure that the data dict is fully documented"""
    utils.is_data_documented(data, documentation=DATA)


def main(return_tagdir=False):
    utils.parse_options()
    utils.configure_logging()
    releaser = Releaser()
    releaser.run()
    if return_tagdir:
        # At the end, for the benefit of fullrelease.
        return releaser.data.get('tagdir')
    else:
        tagdir = releaser.data.get('tagdir')
        if tagdir:
            logger.info(u"Reminder: tag checkout is in {0}".format(tagdir))
