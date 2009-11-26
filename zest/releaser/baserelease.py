"""Provide a base for the three releasers"""

from zest.releaser import utils
from zest.releaser import choose


class Basereleaser(object):

    def __init__(self):
        self.vcs = choose.version_control()
        self.data = {}

    def run(self):
        self.prepare()
        self.execute()

    def prepare(self):
        raise NotImplementedError()

    def execute(self):
        raise NotImplementedError()

