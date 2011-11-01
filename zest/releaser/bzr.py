import logging
import tempfile
import os

from zest.releaser.utils import system
from zest.releaser.vcs import BaseVersionControl

logger = logging.getLogger('bazaar')


class Bzr(BaseVersionControl):
    """Command proxy for Bazaar"""
    internal_filename = '.bzr'

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
        tag_info = system('bzr tags')
        tags = [line[:line.find(' ')] for line in tag_info.split('\n')]
        tags = [tag for tag in tags if tag]
        logger.debug("Available tags: %r", tags)
        return tags

    def prepare_checkout_dir(self, prefix):
        """Return directory where a tag checkout can be made"""
        return tempfile.mkdtemp(prefix=prefix)

    def tag_url(self, version):
        # this doesn't apply to Bazaar, so we just return the
        # version name given ...
        return version

    def cmd_diff(self):
        return 'bzr diff'

    def cmd_commit(self, message):
        return 'bzr commit -v -m "%s"' % message

    def cmd_diff_last_commit_against_tag(self, version):
        return "bzr diff -r tag:%s..-1" % version

    def cmd_log_since_tag(self, version):
        return "bzr log -r tag:%s..-1" % version

    def cmd_create_tag(self, version):
        return 'bzr tag %s' % version

    def cmd_checkout_from_tag(self, version, checkout_dir):
        source = self.workingdir
        target = checkout_dir
        return 'bzr checkout -r tag:%s %s %s' % (version, source, target)

    def is_clean_checkout(self):
        """Is this a clean checkout?

        When you try to do commits in bazaar but you are on a tag you
        will get this error:

        "working tree is out of date, run 'bzr update'"

        That should be clear enough already.  Well, we can run 'bzr
        status' and see what we get.
        """
        # Check for changes to versioned files.
        if system('bzr status --versioned'):
            # Local changes.
            return False
        return True
