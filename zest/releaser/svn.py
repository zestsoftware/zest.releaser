from commands import getoutput
import logging
import zest.releaser.utils
import zest.releaser.vcs

logger = logging.getLogger('utils')

class Subversion(zest.releaser.vcs.BaseVersionControl):
    """Command proxy for Subversion"""
    internal_filename = '.svn'
    
    def show_diff_offer_commit(self, message):
        """Show the svn diff and offer to commit it."""
        diff = getoutput('svn diff')
        logger.info("The 'svn diff':\n\n%s\n", diff)
        if zest.releaser.utils.ask("OK to commit this"):
            commit = getoutput('svn commit -m "%s"' % message)
            logger.info(commit)
