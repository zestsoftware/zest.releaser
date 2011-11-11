import tempfile
import logging
import sys

from zest.releaser import utils
from zest.releaser.utils import system
from zest.releaser.vcs import BaseVersionControl

logger = logging.getLogger('zest.releaser')


class Subversion(BaseVersionControl):
    """Command proxy for Subversion"""
    internal_filename = '.svn'

    def _svn_info(self):
        """Return svn url"""
        our_info = system('svn info')
        if not hasattr(self, '_cached_url'):
            url = [line for line in our_info.split('\n')
                   if line.startswith('URL')][0]
            # In English, you have 'URL:', in French 'URL :'
            self._cached_url = url.split(':', 1)[1].strip()
        return self._cached_url

    def _base_from_svn(self):
        base = self._svn_info()
        # Note: slashes are used to prevent problems with 'tha.tagfinder'-like
        # project names...
        for remove in ['/trunk', '/tags', '/branches', '/tag', '/branch']:
            base = base.rsplit(remove, 1)[0]
        if not base.endswith('/'):
            base += '/'
        logger.debug("Base url is %s", base)
        return base

    def _name_from_svn(self):
        base = self._base_from_svn()
        parts = base.split('/')
        parts = [p for p in parts if p]
        name = parts[-1]
        logger.debug("Name is %s", name)
        return name

    @property
    def _tags_name(self):
        """Return name for tags dir

        Normally the plural /tags, but some projects have the singular /tag.

        """
        default_plural = 'tags'
        fallback_singular = 'tag'
        # svn 1.7 introduced a slightly different message and a warning code.
        failure_messages = ["non-existent in that revision", "W160013"]
        base = self._base_from_svn()
        tag_info = system('svn list %s%s' % (base, default_plural))
        # Look for one of the failure messages:
        found = [1 for mess in failure_messages if mess in tag_info]
        if not found:
            return default_plural
        logger.debug("tags dir does not exist at %s%s", base, default_plural)

        tag_info = system('svn list %s%s' % (base, fallback_singular))
        # Look for one of the failure messages:
        found = [1 for mess in failure_messages if mess in tag_info]
        if not found:
            return fallback_singular
        logger.debug("tags dir does not exist at %s%s, either", base,
                     fallback_singular)
        return None

    @property
    def name(self):
        package_name = self.get_setup_py_name()
        if package_name:
            return package_name
        else:
            return self._name_from_svn()

    def available_tags(self):
        base = self._base_from_svn()
        tags_name = self._tags_name
        if tags_name == None:
            # Suggest to create a tags dir with the default plural /tags name.
            print "tags dir does not exist at %s" % base + 'tags'
            if utils.ask("Shall I create it"):
                cmd = 'svn mkdir %stags -m "Creating tags directory."' % (base)
                logger.info("Running %r", cmd)
                print system(cmd)
                tags_name = self._tags_name
                assert tags_name == 'tags'
            else:
                sys.exit(0)

        tag_info = system('svn list %s%s' % (base, tags_name))
        if 'Could not resolve hostname' in tag_info or \
                'Repository moved' in tag_info:
            logger.error('Network problem: %s', tag_info)
            sys.exit()
        tags = [line.replace('/', '') for line in tag_info.split('\n')]
        tags = [tag for tag in tags if tag]  # filter empty ones
        logger.debug("Available tags: %r", tags)
        return tags

    def prepare_checkout_dir(self, prefix):
        """Return directory where a tag checkout can be made"""
        return tempfile.mkdtemp(prefix=prefix)

    def tag_url(self, version):
        base = self._base_from_svn()
        return base + self._tags_name + '/' + version

    def cmd_diff(self):
        return 'svn diff'

    def cmd_commit(self, message):
        return 'svn commit -m "%s"' % message

    def cmd_diff_last_commit_against_tag(self, version):
        url = self._svn_info()
        tag_url = self.tag_url(version)
        return "svn --non-interactive diff %s %s" % (tag_url, url)

    def cmd_log_since_tag(self, version):
        """Return log since a tagged version till the last commit of
        the working copy.
        """
        url = self._svn_info()
        tag_url = self.tag_url(version)
        tag_info = system('svn info %s' % tag_url)
        # Search for: Last Changed Rev: 42761
        revision = None
        for line in tag_info.split('\n'):
            line = line.lower()
            if len(line.split(':')) == 2:
                revision = line.split(':')[-1].strip()
        if not revision:
            logger.error('Could not find revision when tag was made: %s',
                         tag_info)
            sys.exit()
        return "svn --non-interactive log -r%s:HEAD %s" % (revision, url)

    def cmd_create_tag(self, version):
        url = self._svn_info()
        tag_url = self.tag_url(version)
        return 'svn cp %s %s -m "Tagging %s"' % (url, tag_url, version)

    def cmd_checkout_from_tag(self, version, checkout_dir):
        tag_url = self.tag_url(version)
        return 'svn co %s %s' % (tag_url, checkout_dir)

    def is_clean_checkout(self):
        """Is this a clean checkout?
        """
        if self._svn_info().startswith(self._base_from_svn() + 'tag'):
            # We should not commit on a tag.
            return False
        # We could do 'svn status --ignore-externals --quiet' and
        # regard any output as a non-clean checkout, but when there
        # are externals this still always prints some lines, which
        # would give false negatives.  So we ignore it.
        return True
