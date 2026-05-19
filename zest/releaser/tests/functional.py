"""Set up functional test fixtures"""

from packaging.utils import canonicalize_name
from zest.releaser import choose
from zest.releaser import utils
from zest.releaser.baserelease import NOTHING_CHANGED_YET
from zest.releaser.utils import execute_command
from zest.releaser.utils import filename_from_test_dir

import os
import requests
import shutil
import sys
import tarfile
import tempfile


def setup(test):
    # Reset constants to original settings:
    utils.AUTO_RESPONSE = False
    utils.TESTMODE = False

    partstestdir = os.getcwd()  # Buildout's test run in parts/test
    test.orig_dir = partstestdir
    test.tempdir = tempfile.mkdtemp(prefix="testtemp")
    test.orig_argv = sys.argv[1:]
    sys.argv[1:] = []
    # Monkey patch sys.exit
    test.orig_exit = sys.exit

    def _exit(code=None):
        msg = "SYSTEM EXIT (code=%s)" % code
        raise RuntimeError(msg)

    sys.exit = _exit

    # Monkey the requests library for PyPI access mocking.
    test.orig_requests_head = requests.head
    test.mock_pypi_available = []

    class MockResponse:
        def __init__(self, ok):
            self.ok = ok

    def _make_mock_head(mock_pypi_available):
        def _mock_head(url):
            package = url.replace("https://pypi.org/simple/", "").replace("/", "")
            # package my.example has been canonicalized to my-example,
            # so we do the same in our mock list.
            canonical_packages = [
                canonicalize_name(name) for name in mock_pypi_available
            ]
            return MockResponse(package in canonical_packages)

        return _mock_head

    requests.head = _make_mock_head(test.mock_pypi_available)

    # Extract example project
    example_tar = filename_from_test_dir("example.tar")
    with tarfile.TarFile(example_tar) as tf:
        tf.extractall(path=test.tempdir)
    sourcedir = os.path.join(test.tempdir, "tha.example")

    # Git initialization
    gitsourcedir = os.path.join(test.tempdir, "tha.example-git")
    shutil.copytree(sourcedir, gitsourcedir)
    os.chdir(gitsourcedir)
    execute_command(["git", "init", "-b", "main"])
    # Configure local git.
    execute_command(["git", "config", "--local", "user.name", "Temp user"])
    execute_command(["git", "config", "--local", "user.email", "temp@example.com"])
    execute_command(["git", "config", "--local", "commit.gpgsign", "false"])
    execute_command(["git", "config", "--local", "tag.gpgsign", "false"])
    execute_command(["git", "add", "."])
    execute_command(["git", "commit", "-a", "-m", "init" "-n"])
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
        with open("CHANGES.txt") as f:
            orig_changes = f.read()
        new_changes = orig_changes.replace(NOTHING_CHANGED_YET, "- Brown bag release.")
        with open("CHANGES.txt", "w") as f:
            f.write(new_changes)
        commit_all_changes()

    def rename_changelog(src: str, dst: str):
        execute_command(["git", "mv", src, dst])
        commit_all_changes()

    test.globs.update(
        {
            "tempdir": test.tempdir,
            "gitsourcedir": gitsourcedir,
            "githead": githead,
            "mock_pypi_available": test.mock_pypi_available,
            "add_changelog_entry": add_changelog_entry,
            "commit_all_changes": commit_all_changes,
            "rename_changelog": rename_changelog,
        }
    )


def teardown(test):
    sys.exit = test.orig_exit
    requests.head = test.orig_requests_head
    os.chdir(test.orig_dir)
    sys.argv[1:] = test.orig_argv
    shutil.rmtree(test.tempdir)
    # Reset constants to original settings:
    utils.AUTO_RESPONSE = False
    utils.TESTMODE = False
