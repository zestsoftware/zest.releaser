from commands import getoutput
import logging
import tempfile
import zest.releaser.vcs

logger = logging.getLogger('zest.releaser')

class Hg(zest.releaser.vcs.BaseVersionControl):
    """Command proxy for Mercurial"""
    internal_filename = '.hg'

    @property
    def name(self):
        return self.get_setup_py_name()
    
    def available_tags(self):
        tag_info = getoutput('hg tags')
        tags = [line[:line.find(' ')]  for line in tag_info.split('\n')]
        logger.debug("Available tags: %r", tags)
        return tags

    def prepare_checkout_dir(self, prefix):
        return tempfile.mktemp(prefix=prefix)
    
    def cmd_diff(self):
        return 'hg diff'

    def cmd_commit(self, message):
        return 'hg commit -v -m "%s"' % message

    def cmd_diff_last_commit_against_tag(self, version):
        current_revision = getoutput('hg identify')
        current_revision = current_revision[:current_revision.find(' ')]
        return "hg diff -r %s -r %s" % (version, current_revision)

    def cmd_create_tag(self, version):
        return 'hg tag -m "Tagging %s" %s' % (version, version)

    def cmd_checkout_from_tag(self, version, checkout_dir):
        return 'hg clone -r %s . %s' % (version, checkout_dir)
