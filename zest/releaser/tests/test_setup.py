import re
import tempfile

import z3c.testsetup
from zope.testing import renormalizing


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
    # 'register sdist --formats=zip upload' or
    # 'mregister sdist --formats=zip mupload -r pypi' are both fine:
    (re.compile('mregister sdist --formats=zip mupload -r [alpha]*$'),
     'register sdist --formats=zip upload'),
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
    ])


test_suite = z3c.testsetup.register_all_tests('zest.releaser', checker=checker)
