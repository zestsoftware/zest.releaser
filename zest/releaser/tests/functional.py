"""Set up functional test fixtures"""

import os
import shutil
import sys
import tarfile
import tempfile
from io import StringIO
from urllib import request
from urllib.error import HTTPError

import pkg_resources
from colorama import Fore

from zest.releaser import choose
from zest.releaser import utils
from zest.releaser.baserelease import NOTHING_CHANGED_YET
from zest.releaser.utils import execute_command


def setup(test):
    # Reset constants to original settings:
    utils.AUTO_RESPONSE = False
    utils.TESTMODE = False

    partstestdir = os.getcwd()  # Buildout's test run in parts/test
    test.orig_dir = partstestdir
    test.tempdir = tempfile.mkdtemp(prefix='testtemp')
    test.orig_argv = sys.argv[1:]
    sys.argv[1:] = []
    # Monkey patch sys.exit
    test.orig_exit = sys.exit

    def _exit(code=None):
        msg = "SYSTEM EXIT (code=%s)" % code
        raise RuntimeError(msg)

    sys.exit = _exit

    # Monkey patch urllib for pypi access mocking.
    test.orig_urlopen = request.urlopen
    test.mock_pypi_available = []

    def _make_mock_urlopen(mock_pypi_available):
        def _mock_urlopen(url):
            # print "Mock opening", url
            package = url.replace('https://pypi.org/simple/', '')
            if package not in mock_pypi_available:
                raise HTTPError(
                    url, 404,
                    'HTTP Error 404: Not Found (%s does not have any releases)'
                    % package, None, None)
            else:
                answer = ' '.join(mock_pypi_available)
            return StringIO(answer)

        return _mock_urlopen

    request.urlopen = _make_mock_urlopen(test.mock_pypi_available)

    # Extract example project
    example_tar = pkg_resources.resource_filename(
        'zest.releaser.tests', 'example.tar')
    with tarfile.TarFile(example_tar) as tf:
        tf.extractall(path=test.tempdir)
    sourcedir = os.path.join(test.tempdir, 'tha.example')

    # Git initialization
    gitsourcedir = os.path.join(test.tempdir, 'tha.example-git')
    shutil.copytree(sourcedir, gitsourcedir)
    os.chdir(gitsourcedir)
    execute_command(["git", "init"])
    # Configure local git.
    execute_command(["git", "config", "--local", "user.name", "Temp user"])
    execute_command(["git", "config", "--local", "user.email", "temp@example.com"])
    execute_command(["git", "config", "--local", "commit.gpgsign", "false"])
    execute_command(["git", "config", "--local", "tag.gpgsign", "false"])
    execute_command(["git", "add", "."])
    execute_command(["git", "commit", "-a", "-m", "init"])
    os.chdir(test.orig_dir)

    def githead(*filename_parts):
        filename = os.path.join(gitsourcedir, *filename_parts)
        with open(filename) as f:
            lines = f.readlines()
        for line in lines[:5]:
            line = line.strip()
            if line:
                print(line)

    def commit_all_changes(message="Committing all changes"):
        # Get a clean checkout.
        vcs = choose.version_control()
        execute_command(vcs.cmd_commit(message))

    def add_changelog_entry():
        # Replace '- Nothing changed yet.'  by a different entry.
        with open('CHANGES.txt') as f:
            orig_changes = f.read()
        new_changes = orig_changes.replace(
            NOTHING_CHANGED_YET, '- Brown bag release.')
        with open('CHANGES.txt', 'w') as f:
            f.write(new_changes)
        commit_all_changes()

    test.globs.update({'tempdir': test.tempdir,
                       'gitsourcedir': gitsourcedir,
                       'githead': githead,
                       'mock_pypi_available': test.mock_pypi_available,
                       'add_changelog_entry': add_changelog_entry,
                       'commit_all_changes': commit_all_changes,
                       })


def teardown(test):
    sys.exit = test.orig_exit
    request.urlopen = test.orig_urlopen
    os.chdir(test.orig_dir)
    sys.argv[1:] = test.orig_argv
    shutil.rmtree(test.tempdir)
    # Reset constants to original settings:
    utils.AUTO_RESPONSE = False
    utils.TESTMODE = False
