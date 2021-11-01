# GPL, (c) Reinout van Rees

import logging
import os
import sys
from urllib import request
from urllib.error import HTTPError

import requests
from colorama import Fore

try:
    from twine.cli import dispatch as twine_dispatch
except ImportError:
    print("twine.cli.dispatch apparently cannot be imported anymore")
    print("See https://github.com/zestsoftware/zest.releaser/pull/309/")
    print("Try a newer zest.releaser or an older twine (and warn us ")
    print("by reacting in that pull request, please).")
    raise

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
        request.urlopen(url)
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
            print(f"\nFailed to create tag {tag}!")
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
        files_in_dist = sorted(
            os.path.join('dist', filename) for filename in os.listdir('dist')
        )

        register = self.pypiconfig.register_package()

        # If TWINE_REPOSITORY_URL is set, use it.
        if self.pypiconfig.twine_repository_url():
            if not self._ask_upload(package,
                                    self.pypiconfig.twine_repository_url(),
                                    register):
                return

            if register:
                self._retry_twine("register", None, files_in_dist[:1])

            self._retry_twine("upload", None, files_in_dist)
            # Only upload to the server specified in the environment
            return

        # Upload to the repository in the environment or .pypirc
        servers = self.pypiconfig.distutils_servers()

        for server in servers:
            if not self._ask_upload(package, server, register):
                continue

            if register:
                logger.info("Registering...")
                # We only need the first file, it has all the needed info
                self._retry_twine('register', server, files_in_dist[:1])
            self._retry_twine('upload', server, files_in_dist)

    def _ask_upload(self, package, server, register):
        """Ask if the package should be registered and/or uploaded.

        Args:
            package (str): The name of the package.
            server (str): The distutils server name or URL.
            register (bool): Whether or not the package should be registered.
        """
        default = True
        exact = False
        if server == 'pypi' and not package_in_pypi(package):
            logger.info("This package does NOT exist yet on PyPI.")
            # We are not yet on pypi.  To avoid an 'Oops...,
            # sorry!' when registering and uploading an internal
            # package we default to False here.
            default = False
            exact = True
        question = "Upload"
        if register:
            question = "Register and upload"
        return utils.ask(f"{question} to {server}",
                     default=default, exact=exact)

    def _retry_twine(self, twine_command, server, filenames):
        """Attempt to execute a Twine command.

        Args:
            twine_command: The Twine command to use (eg. register, upload).
            server: The distutils server name from a `.pipyrc` config file.
                If this is `None` the TWINE_REPOSITORY_URL environment variable
                will be used instead of a distutils server name.
            filenames: A list of files which will be uploaded.
        """
        twine_args = (twine_command,)

        if server is not None:
            twine_args += ('-r', server)

        if twine_command == 'register':
            pass
        elif twine_command == 'upload':
            twine_args += ('--skip-existing', )
        else:
            print(Fore.RED + "Unknown twine command: %s" % twine_command)
            sys.exit(1)
        twine_args += tuple(filenames)
        try:
            twine_dispatch(twine_args)
            return
        except requests.HTTPError as e:
            # Something went wrong.  Close repository.
            response = e.response
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
            return self._retry_twine(twine_command, server, filenames)

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
