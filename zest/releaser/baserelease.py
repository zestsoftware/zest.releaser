"""Provide a base for the three releasers"""

from __future__ import unicode_literals

import pkg_resources

from zest.releaser import utils
from zest.releaser import choose
from zest.releaser import pypi


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
