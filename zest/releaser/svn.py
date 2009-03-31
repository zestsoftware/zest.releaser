from commands import getoutput
from tempfile import mkdtemp
import logging
import sys

from zest.releaser import utils
from zest.releaser.vcs import BaseVersionControl

logger = logging.getLogger('zest.releaser')


class Subversion(BaseVersionControl):
    """Command proxy for Subversion"""
    internal_filename = '.svn'

    def _svn_info(self):
        """Return svn url"""
        our_info = getoutput('svn info')
        url = [line for line in our_info.split('\n')
               if 'URL:' in line][0]
        return url.replace('URL:', '').strip()

    def _base_from_svn(self):
        base = self._svn_info()
        for remove in ['trunk', 'tags', 'branches']:
            base = base.split(remove)[0]
        logger.debug("Base url is %s", base)
        return base

    def _extract_name_and_base(self, url):
        """Return name and base svn url from svn url."""
        base = url
        for remove in ['trunk', 'tags', 'branches']:
            base = base.split(remove)[0]
        logger.debug("Base url is %s", base)
        parts = base.split('/')
        parts = [part for part in parts if part]
        name = parts[-1]
        logger.debug("Name is %s", name)
        return name, base

    def _name_from_svn(self):
        base = self.base_from_svn()
        parts = base.split('/')
        parts = [p for p in parts if p]
        return parts[-1]

    @property
    def name(self):
        url = self._svn_info()
        name, base = self._extract_name_and_base(url)
        return name

    def available_tags(self):
        base = self._base_from_svn()
        tag_info = getoutput('svn list %stags' % base)
        if "non-existent in that revision" in tag_info:
            print "tags dir does not exist at %s" % base + 'tags'
            if utils.ask("Shall I create it"):
                cmd = 'svn mkdir %stags -m "Creating tags directory."' % (base)
                logger.info("Running %r", cmd)
                print getoutput(cmd)
                tag_info = getoutput('svn list %stags' % base)
            else:
                sys.exit(0)
        if 'Could not resolve hostname' in tag_info:
            logger.error('Network problem: %s', tag_info)
            sys.exit()
        tags = [line.replace('/', '') for line in tag_info.split('\n')]
        logger.debug("Available tags: %r", tags)
        return tags

    def prepare_checkout_dir(self, prefix):
        return mkdtemp(prefix=prefix)

    def tag_url(self, version):
        url = self._svn_info()
        name, base = self._extract_name_and_base(url)
        return base + 'tags/' + version

    def cmd_diff(self):
        return 'svn diff'

    def cmd_commit(self, message):
        return 'svn commit -m "%s"' % message

    def cmd_diff_last_commit_against_tag(self, version):
        url = self._svn_info()
        tag_url = self.tag_url(version)
        return "svn diff %s %s" % (tag_url, url)

    def cmd_create_tag(self, version):
        url = self._svn_info()
        tag_url = self.tag_url(version)
        return 'svn cp %s %s -m "Tagging %s"' % (url, tag_url, version)

    def cmd_checkout_from_tag(self, version, checkout_dir):
        url = self._svn_info()
        tag_url = self.tag_url(version)
        return 'svn co %s %s' % (tag_url, checkout_dir)
