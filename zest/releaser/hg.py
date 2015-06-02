import logging
import tempfile
import os

from zest.releaser.utils import fs_to_text
from zest.releaser.utils import execute_command
from zest.releaser.vcs import BaseVersionControl

logger = logging.getLogger(__name__)


class Hg(BaseVersionControl):
    """Command proxy for Mercurial"""
    internal_filename = u'.hg'
    setuptools_helper_package = 'setuptools_hg'

    @property
    def name(self):
        package_name = self.get_setup_py_name()
        if package_name:
            return package_name
        # No setup.py? With hg we can probably only fall back to the directory
        # name as there's no svn-url with a usable name in it.
        dir_name = os.path.basename(os.getcwd())
        dir_name = fs_to_text(dir_name)
        return dir_name

    def available_tags(self):
        tag_info = execute_command([u'hg', u'tags'])
        tags = [line[:line.find(u' ')] for line in tag_info.split(u'\n')]
        tags = [tag for tag in tags if tag]
        while u'tip' in tags:
            tags.remove(u'tip')  # Not functional for us
        logger.debug(u"Available tags: {0}".format(tags))
        return tags

    def prepare_checkout_dir(self, prefix):
        """Return directory where a tag checkout can be made"""
        return tempfile.mkdtemp(prefix=prefix)

    def tag_url(self, version):
        # this doesn't apply to Mercurial, so we just return the
        # version name given ...
        return version

    def cmd_diff(self):
        return [u'hg', u'diff']

    def cmd_commit(self, message):
        return [u'hg', u'commit', u'-v', u'-m', message]

    def cmd_diff_last_commit_against_tag(self, version):
        current_revision = execute_command([u'hg', u'identify'])
        current_revision = current_revision.split(u' ')[0]
        # + at the end of the revision denotes uncommitted changes
        current_revision = current_revision.rstrip(u'+')
        return [u"hg", u"diff", u"-r", version, u"-r", current_revision]

    def cmd_log_since_tag(self, version):
        current_revision = execute_command([u'hg', u'identify'])
        current_revision = current_revision.split(u' ')[0]
        # + at the end of the revision denotes uncommitted changes
        current_revision = current_revision.rstrip(u'+')
        return [u"hg", u"log", u"-r", version, "-r", current_revision]

    def cmd_create_tag(self, version):
        # Note: place the '-m' before the argument for hg 1.1 support.
        return [[u'hg', u'tag', u'-m', u"Tagging {0}".format(version), version]]

    def cmd_checkout_from_tag(self, version, checkout_dir):
        source = self.workingdir
        target = checkout_dir
        return [[u'hg', u'clone', u'-r', version, source, target]]

    def checkout_from_tag(self, version):
        package = self.name
        prefix = u'{0}-{1}-'.format(package, version)
        # Not all hg versions can do a checkout in an existing or even
        # just in the current directory.
        tagdir = tempfile.mktemp(prefix=prefix)
        cmds = self.cmd_checkout_from_tag(version, tagdir)
        for cmd in cmds:
            print(execute_command(cmd))
        os.chdir(tagdir)

    def is_clean_checkout(self):
        """Is this a clean checkout?
        """
        # The --quiet option ignores untracked (unknown and ignored)
        # files, which seems reasonable.
        if execute_command([u'hg', u'status', u'--quiet']):
            # Local changes.
            return False
        return True

    def push_commands(self):
        """Return commands to push changes to the server."""
        return [[u'hg', u'push']]

    def list_files(self):
        """List files in version control."""
        return execute_command([u'hg', u'locate']).splitlines()
