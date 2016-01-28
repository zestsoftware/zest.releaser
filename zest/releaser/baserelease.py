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

logger = logging.getLogger(__name__)


class Basereleaser(object):

    def __init__(self, vcs=None):
        if vcs is None:
            self.vcs = choose.version_control()
        else:
            # In a fullrelease, we share the determined vcs between
            # prerelease, release and postrelease.
            self.vcs = vcs
        self.data = {'workingdir': self.vcs.workingdir,
                     'reporoot': self.vcs.reporoot,
                     'name': self.vcs.name}
        self.setup_cfg = pypi.SetupConfig()
        if self.setup_cfg.no_input():
            utils.AUTO_RESPONSE = True
        if utils.TESTMODE:
            pypirc_old = pkg_resources.resource_filename(
                'zest.releaser.tests', 'pypirc_old.txt')
            self.pypiconfig = pypi.PypiConfig(pypirc_old)
        else:
            self.pypiconfig = pypi.PypiConfig()

    def _grab_version(self):
        """Just grab the version.

        This may be overridden to get a different version, like in prerelease.
        """
        version = self.vcs.version
        if not version:
            logger.critical("No version detected, so we can't do anything.")
            sys.exit(1)
        self.data['version'] = version

    def _grab_history(self, initial=False):
        """Calculate the needed history/changelog changes

        Every history heading looks like '1.0 b4 (1972-12-25)'. Extract them,
        check if the first one matches the version and whether it has a the
        current date.

        This is called twice, with initial first True, then False.
        When False, some warnings are skipped.

        """
        default_location = None
        config = self.setup_cfg.config
        if config and config.has_option('zest.releaser', 'history_file'):
            default_location = config.get('zest.releaser', 'history_file')
        history_file = self.vcs.history_file(location=default_location)
        if not history_file:
            if initial:
                logger.warn("No history file found")
            self.data['history_lines'] = None
            self.data['history_file'] = None
            self.data['history_encoding'] = None
            return
        logger.debug("Checking %s", history_file)
        history_lines, history_encoding = read_text_file(history_file)
        history_lines = history_lines.split('\n')
        headings = utils.extract_headings_from_history(history_lines)
        if not len(headings):
            logger.error("No detectable version heading in the history "
                         "file %s", history_file)
            sys.exit(1)
        if change_header:
            good_heading = self.data['history_header'] % self.data
            # ^^^ history_header is a string with %(abc)s replacements.
            line = headings[0]['line']
            previous = history_lines[line]
            history_lines[line] = good_heading
            logger.debug("Set heading from %r to %r.", previous, good_heading)
            history_lines[line + 1] = utils.fix_rst_heading(
                heading=good_heading,
                below=history_lines[line + 1])
            logger.debug("Set line below heading to %r",
                         history_lines[line + 1])
        self.data['history_lines'] = history_lines
        self.data['history_file'] = history_file
        self.data['history_encoding'] = history_encoding

        # Look for 'Nothing changed yet' under the latest header.  Not
        # nice if this text ends up in the changelog.  Did nothing happen?
        start = headings[0]['line']
        if len(headings) > 1:
            # Include the next header plus underline, as this is nice
            # to show in the history_last_release.
            end = headings[1]['line'] + 2
        else:
            end = len(history_lines)
        history_last_release = '\n'.join(history_lines[start:end])
        self.data['history_last_release'] = history_last_release
        if check_nothing_changed:
            if (initial and self.data['nothing_changed_yet'] in
                    history_last_release):
                # We want quotes around the text, but also want to avoid
                # printing text with a u'unicode marker' in front...
                pretty_nothing_changed = '"{}"'.format(
                    self.data['nothing_changed_yet'])
                if not utils.ask(
                        "WARNING: Changelog contains {}. Are you sure you "
                        "want to release?".format(pretty_nothing_changed),
                        default=False):
                    logger.info("You can use the 'lasttaglog' command to "
                                "see the commits since the last tag.")
                    sys.exit(1)

        # Look for required text under the latest header.  This can be a list,
        # in which case only one item needs to be there.
        required = self.data.get('required_changelog_text')
        if initial and required:
            if isinstance(required, six.string_types):
                required = [required]
            found = False
            for text in required:
                if text in history_last_release:
                    found = True
                    break
            if not found:
                pretty_required = '"{}"'.format('", "'.join(required))
                if not utils.ask(
                        "WARNING: Changelog should contain at least one of "
                        "these required strings: {}. Are you sure you "
                        "want to release?".format(pretty_required),
                        default=False):
                    sys.exit(1)

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
        if utils.ask("OK to push commits to the server?"):
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
