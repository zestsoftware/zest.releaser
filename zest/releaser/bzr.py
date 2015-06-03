import logging
import tempfile
import os

from zest.releaser.utils import execute_command
from zest.releaser.vcs import BaseVersionControl

logger = logging.getLogger(__name__)


class Bzr(BaseVersionControl):
    """Command proxy for Bazaar"""
    internal_filename = u'.bzr'
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
        tag_info = execute_command([u'bzr', u'tags'])
        tags = [line[:line.find(u' ')] for line in tag_info.split(u'\n')]
        tags = [tag for tag in tags if tag]
        logger.debug(u"Available tags: {0!r}".format(tags))
        return tags

    def prepare_checkout_dir(self, prefix):
        """Return directory where a tag checkout can be made"""
        return tempfile.mkdtemp(prefix=prefix)

    def tag_url(self, version):
        # this doesn't apply to Bazaar, so we just return the
        # version name given ...
        return version

    def cmd_diff(self):
        return [u'bzr', u'diff']

    def cmd_commit(self, message):
        return [u'bzr', u'commit', u'-v', u'-m', message]

    def cmd_diff_last_commit_against_tag(self, version):
        return [u"bzr", u"diff", u"-r", u"tag:{0}..-1".format(version)]

    def cmd_log_since_tag(self, version):
        return [u"bzr", u"log", u"-r", u"tag:{0}..-1".format(version)]

    def cmd_create_tag(self, version):
        return [[u'bzr', u'tag', version]]

    def cmd_checkout_from_tag(self, version, checkout_dir):
        source = self.workingdir
        target = checkout_dir
        return [[u'bzr', u'checkout', u'-r', u'tag:{0}'.format(version),
                 source, target]]

    def is_clean_checkout(self):
        """Is this a clean checkout?

        When you try to do commits in bazaar but you are on a tag you
        will get this error:

        "working tree is out of date, run 'bzr update'"

        That should be clear enough already.  Well, we can run 'bzr
        status' and see what we get.
        """
        # Check for changes to versioned files.
        if execute_command([u'bzr', u'status', u'--versioned']):
            # Local changes.
            return False
        return True

    def list_files(self):
        """List files in version control."""
        return execute_command([u'bzr', u'ls', u'--recursive']).splitlines()
