from .functional import setup
from .functional import teardown
from colorama import Fore
from zope.testing import renormalizing

import doctest
import os
import re
import tempfile
import twine.cli
import unittest


def mock_dispatch(*args):
    print("MOCK twine dispatch {}".format(" ".join(*args)))
    return True


print("Mocking twine.cli.dispatch...")
twine.cli.dispatch = mock_dispatch

checker = renormalizing.RENormalizing(
    [
        # Date formatting
        (re.compile(r"\d{4}-\d{2}-\d{2}"), "1972-12-25"),
        # Git diff hash formatting
        (
            re.compile(r"[0-9a-f]{7}\.\.[0-9a-f]{7} [0-9a-f]{6}"),
            "1234567..890abcd ef0123",
        ),
        # .pypirc seems to be case insensitive
        (re.compile(r"[Pp][Yy][Pp][Ii]"), "pypi"),
        # Normalize tempdirs.  For this to work reliably, we need to use a prefix
        # in all tempfile.mkdtemp() calls.
        (
            re.compile(r"/private%s/testtemp[^/]+" % re.escape(tempfile.gettempdir())),
            "TESTTEMP",
        ),  # OSX madness
        (
            re.compile(r"%s/testtemp[^/]+" % re.escape(tempfile.gettempdir())),
            "TESTTEMP",
        ),
        (re.compile(re.escape(tempfile.gettempdir())), "TMPDIR"),
        # Change in git 2.9.1:
        (
            re.compile(r"nothing to commit, working directory clean"),
            "nothing to commit, working tree clean",
        ),
        # We should ignore coloring by colorama.  Or actually print it
        # clearly.  This catches Fore.RED, Fore.MAGENTA and Fore.RESET.
        (re.compile(re.escape(Fore.RED)), "RED "),
        (re.compile(re.escape(Fore.MAGENTA)), "MAGENTA "),
        (re.compile(re.escape(Fore.RESET)), "RESET "),
    ]
)


def test_suite():
    """Find .txt files and test code examples in them."""
    suite = unittest.TestSuite()

    # These are simple tests without setup.
    simple = [
        "preparedocs.txt",
        "pypi.txt",
        "utils.txt",
    ]
    suite.addTests(
        doctest.DocFileSuite(
            *simple,
            checker=checker,
            optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
        )
    )

    # Now for more involved tests with setup and teardown
    doctests = []
    tests_path = os.path.dirname(__file__)
    for filename in sorted(os.listdir(tests_path)):
        if not filename.endswith(".txt"):
            continue
        if filename in simple:
            continue
        if filename.startswith("pypirc_"):
            # Sample pypirc file
            continue
        doctests.append(filename)

    suite.addTests(
        doctest.DocFileSuite(
            *doctests,
            setUp=setup,
            tearDown=teardown,
            checker=checker,
            optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
        )
    )

    return suite
