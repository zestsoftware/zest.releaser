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
    internal_filename = u'.git'
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
        tag_info = execute_command([u'git', u'tag'])
        tags = [line for line in tag_info.split(u'\n') if line]
        logger.debug(u"Available tags: {!r}".format(tags))
        return tags

    def prepare_checkout_dir(self, prefix):
        # Watch out: some git versions can't clone into an existing
        # directory, even when it is empty.
        temp = tempfile.mkdtemp(prefix=prefix)
        cwd = os.getcwd()
        os.chdir(temp)
        cmd = [u'git', u'clone', self.workingdir, 'gitclone']
        logger.debug(execute_command(cmd))
        clonedir = os.path.join(temp, 'gitclone')
        os.chdir(clonedir)
        cmd = [u'git', u'submodule', u'update', u'--init', u'--recursive']
        logger.debug(execute_command(cmd))
        os.chdir(cwd)
        return clonedir

    def tag_url(self, version):
        # this doesn't apply to Git, so we just return the
        # version name given ...
        return version

    def cmd_diff(self):
        return [u'git', u'diff']

    def cmd_commit(self, message):
        return [u'git', u'commit', u'-a', u'-m', message]

    def cmd_diff_last_commit_against_tag(self, version):
        return [u"git", u'diff', version]

    def cmd_log_since_tag(self, version):
        """Return log since a tagged version till the last commit of
        the working copy.
        """
        return [u"git", u"log", "{0}..HEAD".format(version)]

    def cmd_create_tag(self, version):
        msg = u"Tagging {0}".format(version)
        cmds = [[u'git', u'tag', version, u'-m', msg]]
        if os.path.isdir(u'.git/svn'):
            print(u"\nEXPERIMENTAL support for git-svn tagging!\n")
            cur_branch = open(u'.git/HEAD').read().strip().split(u'/')[-1]
            print(u"You are on branch {0}.".format(cur_branch))
            if cur_branch != u'master':
                print(u"Only the master branch is supported for "
                      u"git-svn tagging.")
                print(u"Please tag yourself.")
                print(u"'git tag' needs to list tag named {0}.".format(version))
                sys.exit(1)

            trunk = None
            # In Git v2.0, the default prefix will change from "" (no prefix)
            # to "origin/", try both here.
            for t in [u'.git/refs/remotes/trunk', u'.git/refs/remotes/origin/trunk']:
                if os.path.isfile(t):
                    trunk = open(t).read()

            if not trunk:
                print(u'No SVN remote found (only the default svn ' +
                      u'prefixes ("" or "origin/") are supported).')
                sys.exit(1)

            local_head = open(u'.git/refs/heads/master').read()
            if local_head != trunk:
                print(u"Your local master diverges from trunk.\n")
                # dcommit before local tagging
                cmds.insert(0, [u'git', u'svn', u'dcommit'])
            # create tag in svn
            cmds.append([u'git', u'svn', u'tag', u'-m', msg, version])
        return cmds

    def cmd_checkout_from_tag(self, version, checkout_dir):
        if not (os.path.realpath(os.getcwd()) ==
                os.path.realpath(checkout_dir)):
            # Specific to git: we need to be in that directory for the command
            # to work.
            logger.warn(u"We haven't been chdir'ed to {0}".format(checkout_dir))
            sys.exit(1)
        return [[u'git', u'checkout', version],
                [u'git', u'submodule', u'update', u'--init', u'--recursive'],
               ]

    def is_clean_checkout(self):
        """Is this a clean checkout?
        """
        head = execute_command([u'git', u'symbolic-ref', u'--quiet', u'HEAD'])
        # This returns something like 'refs/heads/maurits-warn-on-tag'
        # or nothing.  Nothing would be bad as that indicates a
        # detached head: likely a tag checkout
        if not head:
            # Greetings from Nearly Headless Nick.
            return False
        if execute_command([u'git', u'status', u'--short',
                            u'--untracked-files=no']):
            # Uncommitted changes in files that are tracked.
            return False
        return True

    def push_commands(self):
        """Push changes to the server."""
        return [
            [u'git', u'push'],
            [u'git', u'push', u'--tags']
            ]

    def list_files(self):
        """List files in version control."""
        return execute_command([
            u'git', u'ls-tree', u'-r', u'HEAD', u'--name-only'
            ]).splitlines()
