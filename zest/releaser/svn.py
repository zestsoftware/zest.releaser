import tempfile
import logging
import sys

from zest.releaser import utils
from zest.releaser.utils import execute_command
from zest.releaser.vcs import BaseVersionControl

logger = logging.getLogger(__name__)


class Subversion(BaseVersionControl):
    """Command proxy for Subversion"""
    internal_filename = u'.svn'
    setuptools_helper_package = 'setuptools_subversion'

    def _svn_info(self):
        """Return svn url"""
        our_info = execute_command([u'svn', u'info'])
        if not hasattr(self, '_cached_url'):
            url = [line for line in our_info.split(u'\n')
                   if line.startswith(u'URL')][0]
            # In English, you have 'URL:', in French 'URL :'
            self._cached_url = url.split(':', 1)[1].strip()
        return self._cached_url

    def _base_from_svn(self):
        base = self._svn_info()
        # Note: slashes are used to prevent problems with 'tha.tagfinder'-like
        # project names...
        for remove in [u'/trunk', u'/tags', u'/branches', u'/tag', u'/branch']:
            base = base.rsplit(remove, 1)[0]
        if not base.endswith(u'/'):
            base += u'/'
        logger.debug(u"Base url is {0}".format(base))
        return base

    def _name_from_svn(self):
        base = self._base_from_svn()
        parts = base.split(u'/')
        parts = [p for p in parts if p]
        name = parts[-1]
        logger.debug(u"Name is {0}".format(name))
        return name

    @property
    def _tags_name(self):
        """Return name for tags dir

        Normally the plural /tags, but some projects have the singular /tag.

        """
        default_plural = u'tags'
        fallback_singular = u'tag'
        # svn 1.7 introduced a slightly different message and a warning code.
        failure_messages = [u"non-existent in that revision",
                            u"W160013",
                            ]
        base = self._base_from_svn()
        tag_info = execute_command([
            u'svn', u'list', u'{0}{1}'.format(base, default_plural)
            ])
        # Look for one of the failure messages:
        found = [1 for mess in failure_messages if mess in tag_info]
        if not found:
            return default_plural
        logger.debug(
            u"tags dir does not exist at {0}{1}".format(base, default_plural))

        tag_info = execute_command([
            u'svn', u'list', u'{0}{1}'.format(base, fallback_singular)
            ])
        # Look for one of the failure messages:
        found = [1 for mess in failure_messages if mess in tag_info]
        if not found:
            return fallback_singular
        logger.debug(u"tags dir does not exist at {0}{1}, either".format(
            base, fallback_singular))
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
        if tags_name is None:
            # Suggest to create a tags dir with the default plural /tags name.
            print(u"tags dir does not exist at {0}tags".format(base))
            if utils.ask(u"Shall I create it"):
                cmd = [
                    u'svn', u'mkdir', u'{0}tags'.format(base),
                    u'-m', u'Creating tags directory.'
                    ]
                logger.info(u"Running {0!r}".format(cmd))
                print(execute_command(cmd))
                tags_name = self._tags_name
                assert tags_name == u'tags'
            else:
                sys.exit(0)

        tag_info = execute_command([u'svn', u'list', u'{0}{1}'.format(base, tags_name)])
        network_errors = [
            u'Could not resolve hostname',
            u'E670008',
            u'Repository moved',
            u'Unable to connect',
        ]
        found_errors = [1 for network_error in network_errors
                        if network_error in tag_info]
        if found_errors:
            logger.error(u'Network problem: {0}'.format(tag_info))
            sys.exit(1)
        tags = [line.replace(u'/', u'').strip()
                for line in tag_info.split(u'\n')]
        tags = [tag for tag in tags if tag]  # filter empty ones
        logger.debug(u"Available tags: {0!r}".format(tags))
        return tags

    def prepare_checkout_dir(self, prefix):
        """Return directory where a tag checkout can be made"""
        return tempfile.mkdtemp(prefix=prefix)

    def tag_url(self, version):
        base = self._base_from_svn()
        return base + self._tags_name + '/' + version

    def cmd_diff(self):
        return [u'svn', u'diff']

    def cmd_commit(self, message):
        return [u'svn', u'commit', u'-m', message]

    def cmd_diff_last_commit_against_tag(self, version):
        url = self._svn_info()
        tag_url = self.tag_url(version)
        return [u"svn", u'--non-interactive', u'diff', tag_url, url]

    def cmd_log_since_tag(self, version):
        """Return log since a tagged version till the last commit of
        the working copy.
        """
        url = self._svn_info()
        tag_url = self.tag_url(version)
        tag_info = execute_command([u'svn', u'info', tag_url])
        # Search for: Last Changed Rev: 42761
        revision = None
        for line in tag_info.split(u'\n'):
            line = line.lower()
            if len(line.split(u':')) == 2:
                revision = line.split(':')[-1].strip()
        if not revision:
            logger.error(
                u'Could not find revision when tag was made: {0}'.format(
                    tag_info
                ))
            sys.exit(1)
        return [u"svn", u"--non-interactive", u"log"
                u"-r{0}:HEAD".format(revision), url]

    def cmd_create_tag(self, version):
        url = self._svn_info()
        tag_url = self.tag_url(version)
        return [[u'svn', u'cp', url, tag_url, u'-m',
                 u"Tagging {0}".format(version)]]

    def cmd_checkout_from_tag(self, version, checkout_dir):
        tag_url = self.tag_url(version)
        return [[u'svn', u'co', tag_url, checkout_dir]]

    def is_clean_checkout(self):
        """Is this a clean checkout?"""
        if self._svn_info().startswith(self._base_from_svn() + u'tag'):
            # We should not commit on a tag.
            return False
        # We could do 'svn status --ignore-externals --quiet' and
        # regard any output as a non-clean checkout, but when there
        # are externals this still always prints some lines, which
        # would give false negatives.  So we ignore it.
        return True

    def list_files(self):
        """List files in version control."""
        return execute_command([u'svn', u'ls', u'--recursive']).splitlines()
