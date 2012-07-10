"""Provide a base for the three releasers"""

from zest.releaser import utils
from zest.releaser import choose
from zest.releaser import pypi


class Basereleaser(object):

    def __init__(self):
        self.vcs = choose.version_control()
        self.data = {'workingdir': self.vcs.workingdir,
                     'name': self.vcs.name}
        self.setup_cfg = pypi.SetupConfig()

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
