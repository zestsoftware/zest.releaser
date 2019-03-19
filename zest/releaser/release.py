# GPL, (c) Reinout van Rees
from __future__ import unicode_literals

import logging
import os
import sys

from colorama import Fore
from requests import codes
from six.moves.urllib.error import HTTPError
from six.moves.urllib import request as urllib2
from twine.repository import Repository
from twine.package import PackageFile

from zest.releaser import baserelease
from zest.releaser import pypi
from zest.releaser import utils
from zest.releaser.utils import execute_command


# Documentation for self.data.  You get runtime warnings when something is in
# self.data that is not in this list.  Embarrasment-driven documentation!
DATA = baserelease.DATA.copy()
DATA.update({
    'tag_already_exists': "Internal detail, don't touch this :-)",
    'tagdir': '''Directory where the tag checkout is placed (*if* a tag
    checkout has been made)''',
    'tagworkingdir': '''Working directory inside the tag checkout. This is
    the same, except when you make a release from within a sub directory.
    We then make sure you end up in the same relative directory after a
    checkout is done.''',
    'version': "Version we're releasing",
    'tag': "Tag we're releasing",
    'tag-message': "Commit message for the tag",
    'tag-signing': "Sign tag using gpg or pgp",
})

logger = logging.getLogger(__name__)


def package_in_pypi(package):
    """Check whether the package is registered on pypi"""
    url = 'https://pypi.org/simple/%s' % package
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
        # dictionary for holding twine repository information
        self._repositories = {}
        # Prepare some defaults for potential overriding.
        self.data.update(dict(
            # Nothing yet
        ))

    def prepare(self):
        """Collect some data needed for releasing"""
        self._grab_version()
        tag = self.pypiconfig.tag_format(self.data['version'])
        self.data['tag'] = tag
        self.data['tag-message'] = self.pypiconfig.tag_message(
            self.data['version'])
        self.data['tag-signing'] = self.pypiconfig.tag_signing()
        self.data['tag_already_exists'] = self.vcs.tag_exists(tag)

    def execute(self):
        """Do the actual releasing"""
        self._info_if_tag_already_exists()
        self._make_tag()
        self._release()

    def _info_if_tag_already_exists(self):
        if self.data['tag_already_exists']:
            # Safety feature.
            version = self.data['version']
            tag = self.data['tag']
            q = ("There is already a tag %s, show "
                 "if there are differences?" % version)
            if utils.ask(q):
                diff_command = self.vcs.cmd_diff_last_commit_against_tag(tag)
                print(utils.format_command(diff_command))
                print(execute_command(diff_command))

    def _make_tag(self):
        version = self.data['version']
        tag = self.data['tag']
        if self.data['tag_already_exists']:
            return
        cmds = self.vcs.cmd_create_tag(tag, self.data['tag-message'],
                                       self.data['tag-signing'])
        assert isinstance(cmds, (list, tuple))  # transitional guard
        if not isinstance(cmds[0], (list, tuple)):
            cmds = [cmds]
        if len(cmds) == 1:
            print("Tag needed to proceed, you can use the following command:")
        for cmd in cmds:
            print(utils.format_command(cmd))
            if utils.ask("Run this command"):
                print(execute_command(cmd))
            else:
                # all commands are needed in order to proceed normally
                print("Please create a tag %s for %s yourself and rerun." %
                      (tag, version))
                sys.exit(1)
        if not self.vcs.tag_exists(tag):
            print("\nFailed to create tag %s!" % (tag,))
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
            logger.error(
                "You must have a properly configured %s file in "
                "your home dir to upload to a Python package index.",
                pypi.DIST_CONFIG_FILE)
            if utils.ask("Do you want to continue without uploading?",
                         default=False):
                return
            sys.exit(1)

        # Run extra entry point
        self._run_hooks('before_upload')

        # Get list of all files to upload.
        files_in_dist = sorted([
            os.path.join('dist', filename) for filename in os.listdir('dist')]
        )

        # Get servers/repositories.
        servers = self.pypiconfig.distutils_servers()

        register = self.pypiconfig.register_package()
        for server in servers:
            if register:
                question = "Register and upload"
            else:
                question = "Upload"
            default = True
            exact = False
            if server == 'pypi' and not package_in_pypi(package):
                logger.info("This package does NOT exist yet on PyPI.")
                # We are not yet on pypi.  To avoid an 'Oops...,
                # sorry!' when registering and uploading an internal
                # package we default to False here.
                default = False
                exact = True
            if utils.ask("%s to %s" % (question, server),
                         default=default, exact=exact):
                if register:
                    logger.info("Registering...")
                    # We only need the first file, it has all the needed info
                    self._retry_twine('register', server, files_in_dist[0])
                for filename in files_in_dist:
                    self._retry_twine('upload', server, filename)
        self._close_all_repositories()

    def _get_repository(self, server):
        if server not in self._repositories:
            self._repositories[server] = Repository(
                **self.pypiconfig.get_server_config(server))
        return self._repositories[server]

    def _close_all_repositories(self):
        for repository in self._repositories.values():
            repository.close()

    def _drop_repository(self, server):
        self._repositories.pop(server, None)

    def _retry_twine(self, twine_command, server, filename):
        repository = self._get_repository(server)
        package_file = PackageFile.from_filename(filename, comment=None)
        if twine_command == 'register':
            # Register the package.
            twine_function = repository.register
            twine_args = (package_file, )
        elif twine_command == 'upload':
            try:
                already_uploaded = repository.package_is_uploaded(package_file)
            except ValueError:
                # For a new package, the call fails, at least with twine 1.8.1.
                # This is the same as when calling `twine --skip-existing` on
                # the command line.  See
                # https://github.com/pypa/twine/issues/220
                logger.warning('Error calling package_is_uploaded from twine. '
                               'Probably new project. Will try uploading.')
                already_uploaded = False
            if already_uploaded:
                logger.warning(
                    'A file %s has already been uploaded. Ignoring.', filename)
                return
            twine_function = repository.upload
            twine_args = (package_file, )
        else:
            print(Fore.RED + "Unknown twine command: %s" % twine_command)
            sys.exit(1)
        response = twine_function(*twine_args)
        ok_status_codes = [codes.OK, codes.CREATED]
        if response is not None and response.status_code in ok_status_codes:
            return
        # Something went wrong.  Close repository.
        repository.close()
        self._drop_repository(server)
        if response is not None:
            # Some errors reported by PyPI after register or upload may be
            # fine.  The register command is not really needed anymore with the
            # new PyPI.  See https://github.com/pypa/twine/issues/200
            # This might change, but for now the register command fails.
            if (twine_command == 'register'
                    and response.reason == 'This API is no longer supported, '
                    'instead simply upload the file.'):
                return
            # Show the error.
            print(Fore.RED + "Response status code: %s" % response.status_code)
            print(Fore.RED + "Reason: %s" % response.reason)
        print(Fore.RED + "There were errors or warnings.")
        logger.exception("Package %s has failed.", twine_command)
        retry = utils.retry_yes_no(['twine', twine_command])
        if retry:
            logger.info("Retrying.")
            # Reload the pypi config so changes that the user has made to
            # influence the retry can take effect.
            self.pypiconfig.reload()
            return self._retry_twine(twine_command, server, filename)

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
        tag = self.data['tag']
        logger.info("Doing a checkout...")
        self.vcs.checkout_from_tag(tag)
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
