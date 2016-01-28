"""Provide a base for the three releasers"""

from __future__ import unicode_literals

import logging
import pkg_resources
import sys

from zest.releaser import utils
from zest.releaser import choose
from zest.releaser import pypi
from zest.releaser.utils import execute_command

logger = logging.getLogger(__name__)


class Basereleaser(object):

    def __init__(self, vcs=None):
        if vcs is None:
            self.vcs = choose.version_control()
        else:
            # In a fullrelease, we share the determined vcs between
            # prerelease, release and postrelease.
            self.vcs = vcs
        self.data = {'workingdir': self.vcs.workingdir,
                     'reporoot': self.vcs.reporoot,
                     'name': self.vcs.name}
        self.setup_cfg = pypi.SetupConfig()
        if self.setup_cfg.no_input():
            utils.AUTO_RESPONSE = True
        if utils.TESTMODE:
            pypirc_old = pkg_resources.resource_filename(
                'zest.releaser.tests', 'pypirc_old.txt')
            self.pypiconfig = pypi.PypiConfig(pypirc_old)
        else:
            self.pypiconfig = pypi.PypiConfig()

    def _grab_version(self):
        """Just grab the version.

        This may be overridden to get a different version, like in prerelease.
        """
        version = self.vcs.version
        if not version:
            logger.critical("No version detected, so we can't do anything.")
            sys.exit(1)
        self.data['version'] = version

    def _diff_and_commit(self, commit_msg=''):
        """Show diff and offer commit.

        commit_msg is optional.  If it is not there, we get the
        commit_msg from self.data.  That is the usual mode and is at
        least used in prerelease and postrelease.  If it is not there
        either, we ask.
        """
        if not commit_msg:
            if 'commit_msg' not in self.data:
                # Ask until we get a non-empty commit message.
                while not commit_msg:
                    commit_msg = utils.get_input(
                        "What is the commit message? ")
            else:
                commit_msg = self.data['commit_msg']

        diff_cmd = self.vcs.cmd_diff()
        diff = execute_command(diff_cmd)
        if sys.version.startswith('2.6.2'):
            # python2.6.2 bug... http://bugs.python.org/issue5170 This is the
            # spot it can surface as we show a part of the changelog which can
            # contain every kind of character.  The rest is mostly ascii.
            print("Diff results:")
            print(diff)
        else:
            # Common case
            logger.info("The '%s':\n\n%s\n", diff_cmd, diff)
        if utils.ask("OK to commit this"):
            msg = commit_msg % self.data
            msg = self.update_commit_message(msg)
            commit_cmd = self.vcs.cmd_commit(msg)
            commit = execute_command(commit_cmd)
            logger.info(commit)

    def _push(self):
        """Offer to push changes, if needed."""
        push_cmds = self.vcs.push_commands()
        if not push_cmds:
            return
        if utils.ask("OK to push commits to the server?"):
            for push_cmd in push_cmds:
                output = execute_command(push_cmd)
                logger.info(output)

    def _run_hooks(self, when):
        which_releaser = self.__class__.__name__.lower()
        utils.run_hooks(self.setup_cfg, which_releaser, when, self.data)

    def run(self):
        self._run_hooks('before')
        self.prepare()
        self._run_hooks('middle')
        self.execute()
        self._run_hooks('after')

    def prepare(self):
        raise NotImplementedError()

    def execute(self):
        raise NotImplementedError()

    def update_commit_message(self, msg):
        extra_message = self.pypiconfig.extra_message()
        if extra_message:
            msg += '\n\n%s' % extra_message
        return msg
