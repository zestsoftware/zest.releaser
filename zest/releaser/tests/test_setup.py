from __future__ import unicode_literals

import re
import tempfile

from colorama import Fore
import six
import z3c.testsetup
import requests
from zope.testing import renormalizing
from twine.repository import Repository


successful_response = requests.Response()
successful_response.status_code = requests.codes.OK


def mock_package_is_uploaded(self, package, bypass_cache=False):
    """Replacement for twine repository package_is_uploaded command.
    """
    return False


def mock_register(self, package):
    """Replacement for twine repository register command.
    """
    print('MOCK twine register {}'.format(package.filename))
    return successful_response


def mock_upload(self, package, max_redirects=5):
    """Replacement for twine repository upload command.
    """
    print('MOCK twine upload {}'.format(package.filename))
    return successful_response


print('Mocking several twine repository methods.')
Repository.package_is_uploaded = mock_package_is_uploaded
Repository.register = mock_register
Repository.upload = mock_upload

checker = renormalizing.RENormalizing([
    # Date formatting
    (re.compile(r'\d{4}-\d{2}-\d{2}'), '1972-12-25'),
    # Hg tag list hash formatting
    (re.compile(r'\d:[0-9a-f]{12}'), '1:234567890abc'),
    # Hg bare hash formatting
    (re.compile(r'[0-9a-f]{12}'), '234567890abc'),
    # Hg has an updated comment
    (re.compile('updating working directory'),
     'updating to branch default'),
    # Newer Hg no longer prints 'requesting all changes'
    (re.compile('requesting all changes'), ''),
    # Git diff hash formatting
    (re.compile(r'[0-9a-f]{7}\.\.[0-9a-f]{7} [0-9a-f]{6}'),
     '1234567..890abcd ef0123'),
    # .pypirc seems to be case insensitive
    (re.compile('[Pp][Yy][Pp][Ii]'), 'pypi'),
    # Normalize tempdirs.  For this to work reliably, we need to use a prefix
    # in all tempfile.mkdtemp() calls.
    (re.compile(
        '%s/testtemp[^/]+/svnrepo' % re.escape(tempfile.gettempdir())),
     'TESTREPO'),
    (re.compile(
        '/private%s/testtemp[^/]+' % re.escape(tempfile.gettempdir())),
     'TESTTEMP'),  # OSX madness
    (re.compile(
        '%s/testtemp[^/]+' % re.escape(tempfile.gettempdir())),
     'TESTTEMP'),
    (re.compile(re.escape(tempfile.gettempdir())),
     'TMPDIR'),
    # Python 2.7 prints 'Creating tar archive' instead of
    # 'tar -cf dist/tha.example-0.1.tar tha.example-0.1
    #  ...':
    (re.compile('tar -cf dist/tha.example-0.1.tar tha.example-0.1'),
     'Creating tar archive'),
    # Harmless line when using subversion 1.7:
    (re.compile('unrecognized .svn/entries format in'), ''),
    # git before 1.7.9.2 reported 0 deletions when committing:
    (re.compile(', 0 deletions\(-\)'), ''),
    # Change in git 1.7.9.2: '1 files changed':
    (re.compile(' 1 files changed'), ' 1 file changed'),
    # Change in git 1.8.0:
    (re.compile('nothing to commit \(working directory clean\)'),
     'nothing to commit, working directory clean'),
    # Change in git 2.9.1:
    (re.compile('nothing to commit, working directory clean'),
     'nothing to commit, working tree clean'),
    # Change in git 1.8.5, the hash is removed:
    (re.compile('# On branch'),
     'On branch'),
    # Hg 3.3 prints 'committing files' or 'committing <filename>'
    (re.compile(r'^committing.*'), ''),
    # We should ignore coloring by colorama.  Or actually print it
    # clearly.  This catches Fore.RED and Fore.MAGENTA.
    # Note the extra backslash in front of the left bracket, otherwise
    # you get: "error: unexpected end of regular expression"
    (re.compile(re.escape(Fore.RED)), 'RED '),
    (re.compile(re.escape(Fore.MAGENTA)), 'MAGENTA '),
    # svn 1.9 prints 'Committing transaction...'
    (re.compile('Committing transaction...'), ''),
    (re.compile('FileNotFoundError'), 'IOError'),
] + ([

] if six.PY3 else [
    (re.compile('u\''), '\''),
    (re.compile('u"'), '"'),
    (re.compile('zest.releaser.utils.CommandException'), 'CommandException'),
]))


test_suite = z3c.testsetup.register_all_tests('zest.releaser', checker=checker)
