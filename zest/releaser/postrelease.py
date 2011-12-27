"""Do the checks and tasks that have to happen after doing a release.
"""
import datetime
import logging
import sys

from zest.releaser import baserelease
from zest.releaser import utils
from zest.releaser.utils import system

logger = logging.getLogger('postrelease')

TODAY = datetime.datetime.today().strftime('%Y-%m-%d')
NOTHING_CHANGED_YET = '- Nothing changed yet.'
COMMIT_MSG = 'Back to development: %(new_version)s'
DEV_VERSION_TEMPLATE = '%(new_version)s.dev0'

DATA = {
    # Documentation for self.data.  You get runtime warnings when something is
    # in self.data that is not in this list.  Embarrasment-driven
    # documentation!
    'workingdir': 'Original working directory',
    'name': 'Name of the project being released',
    'nothing_changed_yet': 'First line in new changelog section',
    'new_version': 'New development version (so 1.1)',
    'dev_version': 'New development version with dev marker (so 1.1.dev0)',
    'commit_msg': 'Message template used when committing',
    'history_header': 'Header template used for 1st history header',
    'dev_version_template': 'Template for dev version number',
    }


class Postreleaser(baserelease.Basereleaser):
    """Post-release tasks like resetting version number.

    self.data holds data that can optionally be changed by plugins.

    """

    def __init__(self):
        baserelease.Basereleaser.__init__(self)
        # Prepare some defaults for potential overriding.
        self.data.update(dict(
            nothing_changed_yet=NOTHING_CHANGED_YET,
            commit_msg=COMMIT_MSG,
            dev_version_template=DEV_VERSION_TEMPLATE))

    def prepare(self):
        """Prepare self.data by asking about new dev version"""
        if not utils.sanity_check(self.vcs):
            logger.critical("Sanity check failed.")
            sys.exit(1)
        self._ask_for_new_dev_version()

    def execute(self):
        """Make the changes and offer a commit"""
        self._update_version()
        self._update_history()
        self._diff_and_commit()
        self._push()

    def _ask_for_new_dev_version(self):
        """Ask for and store a new dev version string."""
        current = self.vcs.version
        # Clean it up to a non-development version.
        current = utils.cleanup_version(current)
        # Try to make sure that the suggestion for next version after
        # 1.1.19 is not 1.1.110, but 1.1.20.
        current_split = current.split('.')
        major = '.'.join(current_split[:-1])
        minor = current_split[-1]
        try:
            minor = int(minor) + 1
            suggestion = '.'.join([major, str(minor)])
        except ValueError:
            # Fall back on simply updating the last character when it is
            # an integer.
            try:
                last = int(current[-1]) + 1
                suggestion = current[:-1] + str(last)
            except ValueError:
                logger.warn("Version does not end with a number, so we can't "
                            "calculate a suggestion for a next version.")
                suggestion = None
        print "Current version is %r" % current
        if suggestion:
            suggestion_string = ' [%s]' % suggestion
        else:
            suggestion_string = ''
        q = ("Enter new development version ('.dev0' will be appended)"
             "%s: " % suggestion_string)
        version = utils.get_input(q).strip()
        if not version:
            version = suggestion
        if not version:
            logger.error("No version entered.")
            sys.exit()

        self.data['new_version'] = version
        dev_version = self.data['dev_version_template'] % self.data
        self.data['dev_version'] = dev_version
        logger.info("New version string is %r",
                    dev_version)

    def _update_version(self):
        """Update the version in vcs"""
        self.vcs.version = self.data['dev_version']

    def _update_history(self):
        """Update the history file"""
        version = self.data['new_version']
        history = self.vcs.history_file()
        if not history:
            logger.warn("No history file found")
            return
        history_lines = open(history).read().split('\n')
        headings = utils.extract_headings_from_history(history_lines)
        if not len(headings):
            logger.warn("No detectable existing version headings in the "
                        "history file.")
            inject_location = 0
            underline_char = '-'
        else:
            first = headings[0]
            inject_location = first['line']
            underline_line = first['line'] + 1
            try:
                underline_char = history_lines[underline_line][0]
            except IndexError:
                logger.debug("No character on line below header.")
                underline_char = '-'
        header = '%s (unreleased)' % version
        inject = [header,
                  underline_char * len(header),
                  '',
                  self.data['nothing_changed_yet'],
                  '',
                  '']
        history_lines[inject_location:inject_location] = inject
        contents = '\n'.join(history_lines)
        open(history, 'w').write(contents)
        logger.info("Injected new section into the history: %r", header)

    def _diff_and_commit(self):
        """Show diff and offer commit"""
        diff_cmd = self.vcs.cmd_diff()
        diff = system(diff_cmd)
        if sys.version.startswith('2.6.2'):
            # python2.6.2 bug... http://bugs.python.org/issue5170 This is the
            # spot it can surface as we show a part of the changelog which can
            # contain every kind of character.  The rest is mostly ascii.
            print "Diff results:"
            print diff
        else:
            # Common case
            logger.info("The '%s':\n\n%s\n" % (diff_cmd, diff))
        if utils.ask("OK to commit this"):
            msg = self.data['commit_msg'] % self.data
            commit_cmd = self.vcs.cmd_commit(msg)
            commit = system(commit_cmd)
            logger.info(commit)

    def _push(self):
        """Offer to push changes, if needed."""
        push_cmds = self.vcs.push_commands()
        if not push_cmds:
            return
        if utils.ask("OK to push commits to the server?"):
            for push_cmd in push_cmds:
                output = system(push_cmd)
                logger.info(output)


def datacheck(data):
    """Entrypoint: ensure that the data dict is fully documented"""
    utils.is_data_documented(data, documentation=DATA)


def main():
    logging.basicConfig(level=utils.loglevel(),
                        format="%(levelname)s: %(message)s")
    postreleaser = Postreleaser()
    postreleaser.run()
