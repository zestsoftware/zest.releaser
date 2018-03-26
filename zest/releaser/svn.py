from __future__ import unicode_literals

import tempfile
import logging
import sys

from zest.releaser import utils
from zest.releaser.utils import execute_command
from zest.releaser.vcs import BaseVersionControl

logger = logging.getLogger(__name__)


class Subversion(BaseVersionControl):
    """Command proxy for Subversion"""
    internal_filename = '.svn'
    setuptools_helper_package = 'setuptools_subversion'

    def _svn_info(self):
        """Return svn url"""
        if not hasattr(self, '_cached_url'):
            our_info = execute_command(['svn', 'info'])
            url = [line for line in our_info.split('\n')
                   if line.startswith('URL')][0]
            # In English, you have 'URL:', in French 'URL :'
            self._cached_url = url.split(':', 1)[1].strip()
        return self._cached_url

    def _base_from_svn(self):
        # Get repository root url without trunk/tags/branches.
        base = self._svn_info()
        # Split and reverse, then look for the first trunk, tag or branch.
        split_url = list(reversed(base.split('/')))
        for remove in ['trunk', 'tags', 'branches', 'tag', 'branch']:
            if remove in split_url:
                split_url = split_url[split_url.index(remove) + 1:]
                base = '/'.join(reversed(split_url))
                # One trunk/tag/branch is quite enough.
                break
        if not base.endswith('/'):
            base += '/'
        logger.debug("Base url is %s", base)
        return base

    def _branch_url_from_svn(self):
        # Get trunk url, or branches/something, or tags/1.0.
        # This is usually the same as self._svn_info(),
        # except when you are not in the repo root.
        # For example, if you are in trunk/my-pkg1, and don't go
        # to the repo root, this returns 'trunk' without 'my-pkg1'.
        # Needed for https://github.com/zestsoftware/zest.releaser/issues/213
        base = self._svn_info()
        split_url = base.split('/')
        if 'trunk' in split_url:
            # Get url including trunk.
            base = '/'.join(split_url[:split_url.index('trunk') + 1])
        else:
            # Get url including branch name or tag id.
            # Most logical is that this is called for branches,
            # so first look for those.
            for flag in ['branches', 'branch', 'tags', 'tag']:
                if flag in split_url:
                    base = '/'.join(split_url[:split_url.index(flag) + 2])
                    break
        logger.debug("Branch url is %s", base)
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
        failure_messages = ["non-existent in that revision",
                            "W160013",
                            ]
        base = self._base_from_svn()
        tag_info = execute_command(
            ['svn', 'list', '%s%s' % (base, default_plural)])
        # Look for one of the failure messages:
        found = [1 for mess in failure_messages if mess in tag_info]
        if not found:
            return default_plural
        logger.debug("tags dir does not exist at %s%s", base, default_plural)

        tag_info = execute_command(
            ['svn', 'list', '%s%s' % (base, fallback_singular)])
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
        if tags_name is None:
            # Suggest to create a tags dir with the default plural /tags name.
            print("tags dir does not exist at %s" % base + 'tags')
            if utils.ask("Shall I create it"):
                cmd = ['svn', 'mkdir', base + 'tags',
                       '-m', "Creating tags directory."]
                logger.info("Running '%s'", utils.format_command(cmd))
                print(execute_command(cmd))
                tags_name = self._tags_name
                assert tags_name == 'tags'
            else:
                sys.exit(1)

        tag_info = execute_command(
            ['svn', 'list', '--non-interactive', base + tags_name])
        network_errors = [
            'Could not resolve hostname',
            'E670008',
            'Repository moved',
            'Unable to connect',
        ]
        found_errors = [1 for network_error in network_errors
                        if network_error in tag_info]
        if found_errors:
            logger.error('Network problem: %s', tag_info)
            sys.exit(1)
        tags = [line.replace('/', '').strip()
                for line in tag_info.split('\n')]
        tags = [tag for tag in tags if tag]  # filter empty ones
        logger.debug("Available tags: '%s'", ', '.join(tags))
        return tags

    def prepare_checkout_dir(self, prefix):
        """Return directory where a tag checkout can be made"""
        return tempfile.mkdtemp(prefix=prefix)

    def tag_url(self, version):
        base = self._base_from_svn()
        return base + self._tags_name + '/' + version

    def cmd_diff(self):
        return ['svn', 'diff', '--non-interactive']

    def cmd_commit(self, message):
        return ['svn', 'commit', '--non-interactive', '-m', message]

    def cmd_diff_last_commit_against_tag(self, version):
        url = self._svn_info()
        tag_url = self.tag_url(version)
        return ['svn', '--non-interactive', 'diff', tag_url, url]

    def cmd_log_since_tag(self, version):
        """Return log since a tagged version till the last commit of
        the working copy.
        """
        url = self._svn_info()
        tag_url = self.tag_url(version)
        tag_info = execute_command(
            ['svn', 'info', '--non-interactive', tag_url])
        # Search for: Last Changed Rev: 42761
        revision = None
        for line in tag_info.split('\n'):
            line = line.lower()
            if len(line.split(':')) == 2:
                revision = line.split(':')[-1].strip()
        if not revision:
            logger.error('Could not find revision when tag was made: %s',
                         tag_info)
            sys.exit(1)
        return ['svn', '--non-interactive', 'log', '-r%s:HEAD' % revision, url]

    def cmd_create_tag(self, version, message, sign=False):
        if sign:
            logger.error("svn does not support signing tags, sorry. "
                         "Please check your configuration in 'setup.cfg'.")
            sys.exit(20)
        url = self._branch_url_from_svn()
        tag_url = self.tag_url(version)
        return ['svn', 'cp', '--non-interactive', url, tag_url,
                '-m', message]

    def cmd_checkout_from_tag(self, version, checkout_dir):
        tag_url = self.tag_url(version)
        return ['svn', 'co', '--non-interactive', tag_url, checkout_dir]

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

    def list_files(self):
        """List files in version control."""
        return execute_command(
            ['svn', 'ls', '--non-interactive', '--recursive']).splitlines()
