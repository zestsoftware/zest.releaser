from __future__ import unicode_literals

import logging
import tempfile
import os
import sys

from zest.releaser.utils import execute_command
from zest.releaser.vcs import BaseVersionControl

logger = logging.getLogger(__name__)


class Bzr(BaseVersionControl):
    """Command proxy for Bazaar"""
    internal_filename = '.bzr'
    setuptools_helper_package = 'setuptools_bzr'

    @property
    def name(self):
        package_name = self.get_setup_py_name()
        if package_name:
            return package_name
        # No setup.py? With bzr we can probably only fall back to the directory
        # name as there's no svn-url with a usable name in it.
        dir_name = os.path.basename(os.getcwd())
        return dir_name

    def available_tags(self):
        tag_info = execute_command(['bzr', 'tags'])
        tags = [line[:line.find(' ')] for line in tag_info.split('\n')]
        tags = [tag for tag in tags if tag]
        logger.debug("Available tags: '%s'", ', '.join(tags))
        return tags

    def prepare_checkout_dir(self, prefix):
        """Return directory where a tag checkout can be made"""
        return tempfile.mkdtemp(prefix=prefix)

    def tag_url(self, version):
        # this doesn't apply to Bazaar, so we just return the
        # version name given ...
        return version

    def cmd_diff(self):
        return ['bzr', 'diff']

    def cmd_commit(self, message):
        return ['bzr', 'commit', '-v', '-m', message]

    def cmd_diff_last_commit_against_tag(self, version):
        return ["bzr", "diff", "-r", "tag:%s..-1" % version]

    def cmd_log_since_tag(self, version):
        return ["bzr", "log", "-r", "tag:%s..-1" % version]

    def cmd_create_tag(self, version, message, sign=False):
        if sign:
            logger.error("bzr does not support signing tags, sorry. "
                         "Please check your configuration in 'setup.cfg'.")
            sys.exit(20)
        return ["bzr", "tag", version]

    def cmd_checkout_from_tag(self, version, checkout_dir):
        source = self.reporoot
        target = checkout_dir
        return ["bzr", "checkout", "-r", "tag:%s" % version,
                source, target]

    def is_clean_checkout(self):
        """Is this a clean checkout?

        When you try to do commits in bazaar but you are on a tag you
        will get this error:

        "working tree is out of date, run 'bzr update'"

        That should be clear enough already.  Well, we can run 'bzr
        status' and see what we get.
        """
        # Check for changes to versioned files.
        if execute_command(['bzr', 'status', '--versioned']):
            # Local changes.
            return False
        return True

    def list_files(self):
        """List files in version control."""
        return execute_command(['bzr', 'ls', '--recursive']).splitlines()
