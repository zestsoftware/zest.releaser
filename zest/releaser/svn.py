from commands import getoutput
import logging
import zest.releaser.utils
import zest.releaser.vcs

logger = logging.getLogger('utils')

class Subversion(zest.releaser.vcs.BaseVersionControl):
    """Command proxy for Subversion"""
    internal_filename = '.svn'
    
    def show_diff_offer_commit(self, message):
        diff = getoutput('svn diff')
        logger.info("The 'svn diff':\n\n%s\n", diff)
        if zest.releaser.utils.ask("OK to commit this"):
            commit = getoutput('svn commit -m "%s"' % message)
            logger.info(commit)

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
            if ask("Shall I create it"):
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

    def tag_exists(self, version):
        for tag in self.available_tags():
            if tag == version:
                return True
        return False
    
    def cmd_diff_last_commit_against_tag(self, version):
        url = self._svn_info()
        name, base = self._extract_name_and_base(url)
        tag_url = base + 'tags/' + version
        return "svn diff %s %s" % (tag_url, url)

    def cmd_create_tag(self, version):
        url = self._svn_info()
        name, base = self._extract_name_and_base(url)
        tag_url = base + 'tags/' + version
        return 'svn cp %s %s -m "Tagging %s"' % (url, tag_url, version)

    def cmd_checkout_from_tag(self, version, checkout_dir):
        url = self._svn_info()
        name, base = self._extract_name_and_base(url)
        tag_url = base + 'tags/' + version
        return 'svn co %s %s' % (tag_url, checkout_dir)
