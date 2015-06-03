"""Set up functional test fixtures"""
import os
import pkg_resources
import shutil
import sys
import tarfile
import tempfile

from six import StringIO
from six.moves.urllib.error import HTTPError
from six.moves.urllib import request as urllib2
from zest.releaser import utils
from zest.releaser.postrelease import NOTHING_CHANGED_YET
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
    test.orig_urlopen = urllib2.urlopen
    test.mock_pypi_available = []

    def _make_mock_urlopen(mock_pypi_available):
        # To fix scope issues in Python 3 without using "nonlocal" and
        # breaking Python 2

        def _mock_urlopen(url):
            # print "Mock opening", url
            package = url.replace(u'https://pypi.python.org/simple/', u'')
            if package not in mock_pypi_available:
                raise HTTPError(
                    url, 404,
                    u'HTTP Error 404: Not Found (%s does not have any releases)'
                    % package, None, None)
            else:
                answer = u' '.join(mock_pypi_available)
            return StringIO(answer)

        return _mock_urlopen

    urllib2.urlopen = _make_mock_urlopen(test.mock_pypi_available)

    # Extract example project
    example_tar = pkg_resources.resource_filename(
        'zest.releaser.tests', 'example.tar')
    tf = tarfile.TarFile(example_tar)
    tf.extractall(path=test.tempdir)
    sourcedir = os.path.join(test.tempdir, 'tha.example')

    # Init svn repo.
    repodir = os.path.join(test.tempdir, 'svnrepo')
    execute_command([u'svnadmin', u'create', repodir])
    repo_url = 'file://' + repodir  # TODO: urllib or so for windows
    # Import example project
    execute_command([u'svn', u'mkdir', u'{0}/tha.example'.format(repo_url),
                     u'-m', 'mkdir'])
    execute_command([u'svn', u'mkdir',
                     u'{0}/tha.example/tags'.format(repo_url),
                     u'-m', u'mkdir'])
    execute_command([u'svn', u'import', sourcedir,
                     u'{0}/tha.example/trunk'.format(repo_url),
                     u'-m', u'import'])
    # Subversion checkout
    svnsourcedir = os.path.join(test.tempdir, 'tha.example-svn')
    execute_command([u'svn', u'co', u'{0}/tha.example/trunk'.format(repo_url),
                     svnsourcedir])
    execute_command([u'svn', u'propset', u'svn:ignore',
                     u'tha.example.egg-info *.pyc',
                     '{0}/src'.format(svnsourcedir)])
    execute_command([u'svn', u'up', svnsourcedir])
    execute_command([u'svn', u'commit', svnsourcedir,
                     u'-m', 'ignoring egginfo'])

    # Mercurial initialization
    hgsourcedir = os.path.join(test.tempdir, 'tha.example-hg')
    shutil.copytree(sourcedir, hgsourcedir)
    execute_command([u"hg", u"init", hgsourcedir])
    open(os.path.join(hgsourcedir, '.hgignore'), 'wb').write(
        b'tha.example.egg-info\n\.pyc$\n')
    execute_command([u"hg", u"add", hgsourcedir])
    execute_command([u"hg", u"commit", u"-m", "init", hgsourcedir])

    # Bazaar initialization
    bzrsourcedir = os.path.join(test.tempdir, 'tha.example-bzr')
    shutil.copytree(sourcedir, bzrsourcedir)
    execute_command([u"bzr", u"init", bzrsourcedir])
    open(os.path.join(bzrsourcedir, '.bzrignore'), 'w').write(
        'tha.example.egg-info\n*.pyc\n')
    execute_command([u"bzr", u"add", bzrsourcedir])
    execute_command([u"bzr", u"commit", u"-m", u"init", bzrsourcedir])

    # Git initialization
    gitsourcedir = os.path.join(test.tempdir, 'tha.example-git')
    shutil.copytree(sourcedir, gitsourcedir)
    os.chdir(gitsourcedir)
    execute_command([u"git", u"init"])
    open(os.path.join(gitsourcedir, '.gitignore'), 'w').write(
        'tha.example.egg-info\n*.pyc\n')
    execute_command([u"git", u"add", u"."])
    execute_command([u"git", u"commit", u"-a", u"-m", u'init'])
    os.chdir(test.orig_dir)

    # Git svn initialization
    gitsvnsourcedir = os.path.join(test.tempdir, 'tha.example-gitsvn')
    execute_command([u'git', u'svn', u'clone',
                     u'-s', '{0}/tha.example'.format(repo_url),
                     gitsvnsourcedir])
    os.chdir(test.orig_dir)

    def svnhead(*filename_parts):
        filename = os.path.join(svnsourcedir, *filename_parts)
        lines = open(filename).readlines()
        for line in lines[:5]:
            print(line.strip())

    def hghead(*filename_parts):
        filename = os.path.join(hgsourcedir, *filename_parts)
        lines = open(filename).readlines()
        for line in lines[:5]:
            print(line.strip())

    def bzrhead(*filename_parts):
        filename = os.path.join(bzrsourcedir, *filename_parts)
        lines = open(filename).readlines()
        for line in lines[:5]:
            print(line.strip())

    def githead(*filename_parts):
        filename = os.path.join(gitsourcedir, *filename_parts)
        lines = open(filename).readlines()
        for line in lines[:5]:
            print(line.strip())

    def add_changelog_entry():
        # Replace '- Nothing changed yet.'  by a different entry.
        orig_changes = open('CHANGES.txt').read()
        new_changes = orig_changes.replace(
            NOTHING_CHANGED_YET, '- Brown bag release.')
        open('CHANGES.txt', 'w').write(new_changes)

    test.globs.update({'tempdir': test.tempdir,
                       'repo_url': repo_url,
                       'svnsourcedir': svnsourcedir,
                       'hgsourcedir': hgsourcedir,
                       'bzrsourcedir': bzrsourcedir,
                       'gitsourcedir': gitsourcedir,
                       'gitsvnsourcedir': gitsvnsourcedir,
                       'svnhead': svnhead,
                       'hghead': hghead,
                       'bzrhead': bzrhead,
                       'githead': githead,
                       'mock_pypi_available': test.mock_pypi_available,
                       'add_changelog_entry': add_changelog_entry,
                       })


def teardown(test):
    sys.exit = test.orig_exit
    urllib2.urlopen = test.orig_urlopen
    os.chdir(test.orig_dir)
    sys.argv[1:] = test.orig_argv
    shutil.rmtree(test.tempdir)
    # Reset constants to original settings:
    utils.AUTO_RESPONSE = False
    utils.TESTMODE = False
