"""Provide a base for the three releasers"""

from zest.releaser import utils
from zest.releaser import choose


class Basereleaser(object):

    def __init__(self):
        self.vcs = choose.version_control()
        self.data = {'workingdir': self.vcs.workingdir,
                     'name': self.vcs.name}

    def _run_entry_points(self, when):
        which_releaser = self.__class__.__name__.lower()
        utils.run_entry_points(which_releaser, when, self.data)

    def run(self):
        self._run_entry_points('before')
        self.prepare()
        self._run_entry_points('middle')
        self.execute()
        self._run_entry_points('after')

    def prepare(self):
        raise NotImplementedError()

    def execute(self):
        raise NotImplementedError()
