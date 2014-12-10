import logging
import tempfile
import os

from zest.releaser.utils import system
from zest.releaser.vcs import BaseVersionControl

logger = logging.getLogger(__name__)


class Hg(BaseVersionControl):
    """Command proxy for Mercurial"""
    internal_filename = '.hg'
    setuptools_helper_package = 'setuptools_hg'

    @property
    def name(self):
        package_name = self.get_setup_py_name()
        if package_name:
            return package_name
        # No setup.py? With hg we can probably only fall back to the directory
        # name as there's no svn-url with a usable name in it.
        dir_name = os.path.basename(os.getcwd())
        return dir_name

    def available_tags(self):
        tag_info = system('hg tags', emit_stderr=False)
        tags = [line[:line.find(' ')] for line in tag_info.split('\n')]
        tags = [tag for tag in tags if tag]
        tags.remove('tip')  # Not functional for us
        logger.debug("Available tags: %r", tags)
        return tags

    def prepare_checkout_dir(self, prefix):
        """Return directory where a tag checkout can be made"""
        return tempfile.mkdtemp(prefix=prefix)

    def tag_url(self, version):
        # this doesn't apply to Mercurial, so we just return the
        # version name given ...
        return version

    def cmd_diff(self):
        return 'hg diff'

    def cmd_commit(self, message):
        return 'hg commit -v -m "%s"' % message

    def cmd_diff_last_commit_against_tag(self, version):
        current_revision = system('hg identify', emit_stderr=False)
        current_revision = current_revision.split(' ')[0]
        # + at the end of the revision denotes uncommitted changes
        current_revision = current_revision.rstrip('+')
        return "hg diff -r %s -r %s" % (version, current_revision)

    def cmd_log_since_tag(self, version):
        current_revision = system('hg identify', emit_stderr=False)
        current_revision = current_revision.split(' ')[0]
        # + at the end of the revision denotes uncommitted changes
        current_revision = current_revision.rstrip('+')
        return "hg log -r %s -r %s" % (version, current_revision)

    def cmd_create_tag(self, version):
        # Note: place the '-m' before the argument for hg 1.1 support.
        return 'hg tag -m "Tagging %s" %s' % (version, version)

    def cmd_checkout_from_tag(self, version, checkout_dir):
        source = self.workingdir
        target = checkout_dir
        return 'hg clone -r %s %s %s' % (version, source, target)

    def checkout_from_tag(self, version):
        package = self.name
        prefix = '%s-%s-' % (package, version)
        # Not all hg versions can do a checkout in an existing or even
        # just in the current directory.
        tagdir = tempfile.mktemp(prefix=prefix)
        cmd = self.cmd_checkout_from_tag(version, tagdir)
        print system(cmd)
        os.chdir(tagdir)

    def is_clean_checkout(self):
        """Is this a clean checkout?
        """
        # The --quiet option ignores untracked (unknown and ignored)
        # files, which seems reasonable.
        if system('hg status --quiet', emit_stderr=False):
            # Local changes.
            return False
        return True

    def push_commands(self):
        """Return commands to push changes to the server."""
        return ['hg push']

    def list_files(self):
        """List files in version control."""
        return system('hg locate', emit_stderr=False).splitlines()
