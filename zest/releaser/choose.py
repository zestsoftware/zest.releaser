import logging
import os
import ConfigParser
import sys
from zest.releaser import git
from zest.releaser import hg
from zest.releaser import svn

logger = logging.getLogger('chooser')


class VersionControlFactory(object):

    CONFIGFILE = '.zest.release.rc'
    DEFAULTS = {'subversion': {'tags': 'tags'}}

    def __init__(self):
        self.update()

    def update(self):
        self.curdir = os.getcwd()
        self.curdir_contents = os.listdir('.')

    def choose(self):
        """Return an object that provides the version control interface based
        on the detected version control system."""
        self.update()
        curdir_contents = self.curdir_contents
        if '.svn' in curdir_contents:
            return self.choose_svn()
        elif '.hg' in curdir_contents:
            return hg.Hg()
        elif '.git' in curdir_contents:
            return git.Git()
        else:
            logger.critical('No version control system detected.')
            sys.exit(1)

    __call__ = choose

    def choose_svn(self):
        if self.CONFIGFILE not in self.curdir_contents:
            return svn.Subversion()
        else:
            config = ConfigParser.ConfigParser(self.DEFAULTS)
            config.read([self.CONFIGFILE])
            tags = config.get('subversion', 'tags')
            logger.info('Subversion uses %s' % tags)
            return svn.Subversion(tags=tags)


version_control = VersionControlFactory()
