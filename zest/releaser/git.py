from __future__ import unicode_literals

import logging
import tempfile
import os.path
import sys

from zest.releaser.utils import fs_to_text
from zest.releaser.utils import execute_command
from zest.releaser.vcs import BaseVersionControl

logger = logging.getLogger(__name__)


class Git(BaseVersionControl):
    """Command proxy for Git"""
    internal_filename = '.git'
    setuptools_helper_package = 'setuptools-git'

    def is_setuptools_helper_package_installed(self):
        # The package is setuptools-git with a dash, the module is
        # setuptools_git with an underscore.  Thanks.
        try:
            __import__('setuptools_git')
        except ImportError:
            return False
        return True

    @property
    def name(self):
        package_name = self.get_setup_py_name()
        if package_name:
            return package_name
        # No setup.py? With git we can probably only fall back to the directory
        # name as there's no svn-url with a usable name in it.
        dir_name = os.path.basename(os.getcwd())
        dir_name = fs_to_text(dir_name)
        return dir_name

    def available_tags(self):
        tag_info = execute_command(['git', 'tag'])
        tags = [line for line in tag_info.split('\n') if line]
        logger.debug("Available tags: '%s'", ', '.join(tags))
        return tags

    def prepare_checkout_dir(self, prefix):
        # Watch out: some git versions can't clone into an existing
        # directory, even when it is empty.
        temp = tempfile.mkdtemp(prefix=prefix)
        cwd = os.getcwd()
        os.chdir(temp)
        cmd = ['git', 'clone', '--depth', '1', self.reporoot, 'gitclone']
        logger.debug(execute_command(cmd))
        clonedir = os.path.join(temp, 'gitclone')
        os.chdir(clonedir)
        cmd = ['git', 'submodule', 'update', '--init', '--recursive']
        logger.debug(execute_command(cmd))
        os.chdir(cwd)
        return clonedir

    def tag_url(self, version):
        # this doesn't apply to Git, so we just return the
        # version name given ...
        return version

    def cmd_diff(self):
        return ['git', 'diff']

    def cmd_commit(self, message):
        return ['git', 'commit', '-a', '-m', message]

    def cmd_diff_last_commit_against_tag(self, version):
        return ['git', 'diff', version]

    def cmd_log_since_tag(self, version):
        """Return log since a tagged version till the last commit of
        the working copy.
        """
        return ['git', 'log', '%s..HEAD' % version]

    def cmd_create_tag(self, version, message, sign=False):
        cmd = ['git', 'tag', version, '-a', '-m', message]
        if sign:
            cmd.append("--sign")
        if os.path.isdir('.git/svn'):
            print("\nEXPERIMENTAL support for git-svn tagging!\n")
            with open('.git/HEAD') as f:
                cur_branch = f.read().strip().split('/')[-1]
            print("You are on branch %s." % (cur_branch,))
            if cur_branch != 'master':
                print("Only the master branch is supported for "
                      "git-svn tagging.")
                print("Please tag yourself.")
                print("'git tag' needs to list tag named %s." % (version,))
                sys.exit(1)
            cmd = [cmd]

            trunk = None
            # In Git v2.0, the default prefix will change from "" (no prefix)
            # to "origin/", try both here.
            for t in ['.git/refs/remotes/trunk',
                      '.git/refs/remotes/origin/trunk']:
                if os.path.isfile(t):
                    with open(t) as f:
                        trunk = f.read()

            if not trunk:
                print('No SVN remote found (only the default svn ' +
                      'prefixes ("" or "origin/") are supported).')
                sys.exit(1)

            with open('.git/refs/heads/master') as f:
                local_head = f.read()
            if local_head != trunk:
                print("Your local master diverges from trunk.\n")
                # dcommit before local tagging
                cmd.insert(0, ['git', 'svn', 'dcommit'])
            # create tag in svn
            cmd.append(['git', 'svn', 'tag', '-m', message, version])
        return cmd

    def cmd_checkout_from_tag(self, version, checkout_dir):
        if not (os.path.realpath(os.getcwd()) ==
                os.path.realpath(checkout_dir)):
            # Specific to git: we need to be in that directory for the command
            # to work.
            logger.warning("We haven't been chdir'ed to %s", checkout_dir)
            sys.exit(1)
        return [['git', 'checkout', version],
                ['git', 'submodule', 'update', '--init', '--recursive']]

    def is_clean_checkout(self):
        """Is this a clean checkout?
        """
        head = execute_command(['git', 'symbolic-ref', '--quiet', 'HEAD'])
        # This returns something like 'refs/heads/maurits-warn-on-tag'
        # or nothing.  Nothing would be bad as that indicates a
        # detached head: likely a tag checkout
        if not head:
            # Greetings from Nearly Headless Nick.
            return False
        if execute_command(
                ['git', 'status', '--short', '--untracked-files=no']):
            # Uncommitted changes in files that are tracked.
            return False
        return True

    def push_commands(self):
        """Push changes to the server."""
        return [['git', 'push'],
                ['git', 'push', '--tags']]

    def list_files(self):
        """List files in version control."""
        return execute_command(
            ['git', 'ls-tree', '-r', 'HEAD', '--name-only']).splitlines()
