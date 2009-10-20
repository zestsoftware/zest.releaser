from commands import getoutput
import logging
import tempfile
import os

from zest.releaser.vcs import BaseVersionControl

logger = logging.getLogger('git')


class Git(BaseVersionControl):
    """Command proxy for Git"""
    internal_filename = '.git'

    @property
    def name(self):
        package_name = self.get_setup_py_name()
        if package_name:
            return package_name
        # No setup.py? With git we can probably only fall back to the directory
        # name as there's no svn-url with a usable name in it.
        dir_name = os.path.basename(os.getcwd())
        return dir_name

    def available_tags(self):
        tag_info = getoutput('git tag')
        tags = [line[:line.find(' ')]  for line in tag_info.split('\n')]
        logger.debug("Available tags: %r", tags)
        return tags

    def prepare_checkout_dir(self, prefix):
        return tempfile.mktemp(prefix=prefix)

    def tag_url(self, version):
        # this doesn't apply to Git, so we just return the
        # version name given ...
        return version

    def cmd_diff(self):
        return 'git diff'

    def cmd_commit(self, message):
        return 'git commit -a -m "%s"' % message

    def cmd_diff_last_commit_against_tag(self, version):
        current_revision = getoutput('git identify')
        current_revision = current_revision.split(' ')[0]
        # + at the end of the revision denotes uncommitted changes
        current_revision = current_revision.rstrip('+')
        return "git diff -r %s -r %s" % (version, current_revision)

    def cmd_create_tag(self, version):
        return 'git tag %s -m "Tagging %s"' % (version, version)

    def cmd_checkout_from_tag(self, version, checkout_dir):
        return 'git clone -r %s . %s' % (version, checkout_dir)
