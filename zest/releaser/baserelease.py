"""Provide a base for the three releasers"""

from __future__ import unicode_literals

import logging
import pkg_resources
import six
import sys

from zest.releaser import utils
from zest.releaser import choose
from zest.releaser import pypi
from zest.releaser.utils import execute_command
from zest.releaser.utils import read_text_file
from zest.releaser.utils import write_text_file

logger = logging.getLogger(__name__)


# Documentation for self.data.  You get runtime warnings when something is in
# self.data that is not in this list.  Embarrasment-driven documentation!  This
# is the data that is available for all commands.  Individual commands may add
# or override data.  Note that not all data is actually used or filled in by
# all commands.
DATA = {
    'commit_msg': 'Message template used when committing',
    'headings': 'Extracted headings from the history file',
    'history_encoding': 'The detected encoding of the history file',
    'history_file': 'Filename of history/changelog file (when found)',
    'history_header': 'Header template used for 1st history header',
    'history_insert_line_here': (
        'Line number where an extra changelog entry can be inserted.'),
    'history_last_release': (
        'Full text of all history entries of the current release'),
    'history_lines': 'List with all history file lines (when found)',
    'name': 'Name of the project being released',
    'new_version': 'New version to write, possibly with development marker',
    'nothing_changed_yet': (
        'First line in new changelog section, '
        'warn when this is still in there before releasing'),
    'original_version': 'Original package version before any changes',
    'reporoot': 'Root of the version control repository',
    'required_changelog_text': (
        'Text that must be present in the changelog. Can be a string or a '
        'list, for example ["New:", "Fixes:"]. For a list, only one of them '
        'needs to be present.'),
    'workingdir': 'Original working directory',
}
NOTHING_CHANGED_YET = '- Nothing changed yet.'


class Basereleaser(object):

    def __init__(self, vcs=None):
        if vcs is None:
            self.vcs = choose.version_control()
        else:
            # In a fullrelease, we share the determined vcs between
            # prerelease, release and postrelease.
            self.vcs = vcs
        self.data = {
            'name': self.vcs.name,
            'nothing_changed_yet': NOTHING_CHANGED_YET,
            'reporoot': self.vcs.reporoot,
            'workingdir': self.vcs.workingdir,
        }
        self.setup_cfg = pypi.SetupConfig()
        if utils.TESTMODE:
            pypirc_old = pkg_resources.resource_filename(
                'zest.releaser.tests', 'pypirc_old.txt')
            self.pypiconfig = pypi.PypiConfig(pypirc_old)
        else:
            self.pypiconfig = pypi.PypiConfig()
        if self.pypiconfig.no_input():
            utils.AUTO_RESPONSE = True

    def _grab_version(self, initial=False):
        """Just grab the version.

        This may be overridden to get a different version, like in prerelease.

        The 'initial' parameter may be used to making a difference
        between initially getting the current version, and later getting
        a suggested version or asking the user.
        """
        # 'initial' is not used in this method, but may be used by sub classes.
        # Mention it here so a check on landscape.io does not complain about an
        # unused argument.
        initial  # noqa
        version = self.vcs.version
        if not version:
            logger.critical("No version detected, so we can't do anything.")
            sys.exit(1)
        self.data['version'] = version

    def _grab_history(self):
        """Calculate the needed history/changelog changes

        Every history heading looks like '1.0 b4 (1972-12-25)'. Extract them,
        check if the first one matches the version and whether it has a the
        current date.
        """
        self.data['history_lines'] = []
        self.data['history_file'] = None
        self.data['history_encoding'] = None
        self.data['headings'] = []
        self.data['history_last_release'] = ''
        self.data['history_insert_line_here'] = 0
        default_location = None
        config = self.setup_cfg.config
        if config and config.has_option('zest.releaser', 'history_file'):
            default_location = config.get('zest.releaser', 'history_file')
        history_file = self.vcs.history_file(location=default_location)
        self.data['history_file'] = history_file
        if not history_file:
            logger.warn("No history file found")
            return
        logger.debug("Checking %s", history_file)
        history_lines, history_encoding = read_text_file(history_file)
        history_lines = history_lines.split('\n')
        headings = utils.extract_headings_from_history(history_lines)
        if not headings:
            logger.warn("No detectable version heading in the history "
                        "file %s", history_file)
            return
        self.data['history_lines'] = history_lines
        self.data['history_encoding'] = history_encoding
        self.data['headings'] = headings

        # Grab last header.
        start = headings[0]['line']
        if len(headings) > 1:
            # Include the next header plus underline, as this is nice
            # to show in the history_last_release.
            end = headings[1]['line'] + 2
        else:
            end = len(history_lines)
        history_last_release = '\n'.join(history_lines[start:end])
        self.data['history_last_release'] = history_last_release

        # Add line number where an extra changelog entry can be inserted.  Can
        # be useful for entry points.  'start' is the header, +1 is the
        # underline, +2 is probably an empty line, so then we should take +3.
        # Or rather: the first non-empty line.
        insert = start + 2
        while insert < end:
            if history_lines[insert].strip():
                break
            insert += 1
        self.data['history_insert_line_here'] = insert

    def _change_header(self, add=False):
        """Change the latest header.

        Change the version number and the release date or development status.

        @add:
        - False: edit current header (prerelease)
        - True: add header (postrelease)
        """
        if self.data['history_file'] is None:
            return
        good_heading = self.data['history_header'] % self.data
        # ^^^ history_header is a string with %(abc)s replacements.
        headings = self.data['headings']
        history_lines = self.data['history_lines']
        previous = ''
        underline_char = '-'
        empty = False
        if not history_lines:
            # Remember that we were empty to start with.
            empty = True
            # prepare header line
            history_lines.append('')
        if len(history_lines) <= 1:
            # prepare underline
            history_lines.append(underline_char)
        if not headings:
            # Mock a heading
            headings = [{'line': 0}]
            inject_location = 0
        first = headings[0]
        inject_location = first['line']
        underline_line = first['line'] + 1
        try:
            underline_char = history_lines[underline_line][0]
        except IndexError:
            logger.debug("No character on line below header.")
            underline_char = '-'
        previous = history_lines[inject_location]
        if add:
            inject = [
                good_heading,
                underline_char * len(good_heading),
                '',
                self.data['nothing_changed_yet'],
                '',
                '',
            ]
            if empty:
                history_lines = []
            history_lines[inject_location:inject_location] = inject
        else:
            # edit current line
            history_lines[inject_location] = good_heading
            logger.debug("Set heading from %r to %r.", previous, good_heading)
            history_lines[underline_line] = utils.fix_rst_heading(
                heading=good_heading,
                below=history_lines[underline_line])
            logger.debug("Set line below heading to %r",
                         history_lines[underline_line])
        # Setting history_lines is not needed, except when we have replaced the
        # original instead of changing it.  So just set it.
        self.data['history_lines'] = history_lines

    def _insert_changelog_entry(self, message):
        """Insert changelog entry."""
        if self.data['history_file'] is None:
            return
        insert = self.data['history_insert_line_here']
        lines = []
        prefix = utils.get_list_item(self.data['history_lines'])
        for index, line in enumerate(message.splitlines()):
            if index == 0:
                line = '{} {}'.format(prefix, line)
            else:
                line = '{}  {}'.format(' ' * len(prefix), line)
            lines.append(line)
        lines.append('')
        self.data['history_lines'][insert:insert] = lines

    def _check_nothing_changed(self):
        """Look for 'Nothing changed yet' under the latest header.

        Not nice if this text ends up in the changelog.  Did nothing
        happen?
        """
        if self.data['history_file'] is None:
            return
        nothing_yet = self.data['nothing_changed_yet']
        if nothing_yet not in self.data['history_last_release']:
            return
        # We want quotes around the text, but also want to avoid
        # printing text with a u'unicode marker' in front...
        pretty_nothing_changed = '"{}"'.format(nothing_yet)
        if not utils.ask(
                "WARNING: Changelog contains {}. Are you sure you "
                "want to release?".format(pretty_nothing_changed),
                default=False):
            logger.info("You can use the 'lasttaglog' command to "
                        "see the commits since the last tag.")
            sys.exit(1)

    def _check_required(self):
        """Look for required text under the latest header.

        This can be a list, in which case only one item needs to be
        there.
        """
        if self.data['history_file'] is None:
            return
        required = self.data.get('required_changelog_text')
        if not required:
            return
        if isinstance(required, six.string_types):
            required = [required]
        history_last_release = self.data['history_last_release']
        for text in required:
            if text in history_last_release:
                # Found it, all is fine.
                return
        pretty_required = '"{}"'.format('", "'.join(required))
        if not utils.ask(
                "WARNING: Changelog should contain at least one of "
                "these required strings: {}. Are you sure you "
                "want to release?".format(pretty_required),
                default=False):
            sys.exit(1)

    def _write_version(self):
        if self.data['new_version'] != self.data['original_version']:
            # self.vcs.version writes it to the file it got the version from.
            self.vcs.version = self.data['new_version']
            logger.info("Changed version from %s to %s",
                        self.data['original_version'],
                        self.data['new_version'])

    def _write_history(self):
        """Write previously-calculated history lines back to the file"""
        if self.data['history_file'] is None:
            return
        contents = '\n'.join(self.data['history_lines'])
        history = self.data['history_file']
        write_text_file(
            history, contents, encoding=self.data['history_encoding'])
        logger.info("History file %s updated.", history)

    def _diff_and_commit(self, commit_msg=''):
        """Show diff and offer commit.

        commit_msg is optional.  If it is not there, we get the
        commit_msg from self.data.  That is the usual mode and is at
        least used in prerelease and postrelease.  If it is not there
        either, we ask.
        """
        if not commit_msg:
            if 'commit_msg' not in self.data:
                # Ask until we get a non-empty commit message.
                while not commit_msg:
                    commit_msg = utils.get_input(
                        "What is the commit message? ")
            else:
                commit_msg = self.data['commit_msg']

        diff_cmd = self.vcs.cmd_diff()
        diff = execute_command(diff_cmd)
        if sys.version.startswith('2.6.2'):
            # python2.6.2 bug... http://bugs.python.org/issue5170 This is the
            # spot it can surface as we show a part of the changelog which can
            # contain every kind of character.  The rest is mostly ascii.
            print("Diff results:")
            print(diff)
        else:
            # Common case
            logger.info("The '%s':\n\n%s\n", diff_cmd, diff)
        if utils.ask("OK to commit this"):
            msg = commit_msg % self.data
            msg = self.update_commit_message(msg)
            commit_cmd = self.vcs.cmd_commit(msg)
            commit = execute_command(commit_cmd)
            logger.info(commit)

    def _push(self):
        """Offer to push changes, if needed."""
        push_cmds = self.vcs.push_commands()
        if not push_cmds:
            return
        default_anwer = self.pypiconfig.push_changes()
        if utils.ask("OK to push commits to the server?",
                     default=default_anwer):
            for push_cmd in push_cmds:
                output = execute_command(push_cmd)
                logger.info(output)

    def _run_hooks(self, when):
        which_releaser = self.__class__.__name__.lower()
        utils.run_hooks(self.setup_cfg, which_releaser, when, self.data)

    def run(self):
        self._run_hooks('before')
        self.prepare()
        self._run_hooks('middle')
        self.execute()
        self._run_hooks('after')

    def prepare(self):
        raise NotImplementedError()

    def execute(self):
        raise NotImplementedError()

    def update_commit_message(self, msg):
        extra_message = self.pypiconfig.extra_message()
        if extra_message:
            msg += '\n\n%s' % extra_message
        return msg
