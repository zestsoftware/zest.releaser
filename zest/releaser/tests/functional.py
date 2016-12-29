"""Set up functional test fixtures"""
from __future__ import unicode_literals

import os
import shutil
import sys
import tarfile
import tempfile

import pkg_resources
from colorama import Fore
from six import StringIO
from six.moves.urllib import request as urllib2
from six.moves.urllib.error import HTTPError

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
    test.orig_urlopen = urllib2.urlopen
    test.mock_pypi_available = []

    def _make_mock_urlopen(mock_pypi_available):
        def _mock_urlopen(url):
            # print "Mock opening", url
            package = url.replace('https://pypi.python.org/simple/', '')
            if package not in mock_pypi_available:
                raise HTTPError(
                    url, 404,
                    'HTTP Error 404: Not Found (%s does not have any releases)'
                    % package, None, None)
            else:
                answer = ' '.join(mock_pypi_available)
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
    # With newer svn versions (1.8), we need to add the --compatible-version
    # argument, because some 'git svn' versions cannot handle higher versions.
    # You get this error when doing 'git svn clone':
    # "Expected FS format between '1' and '4'; found format '6'"
    # But on svn 1.6, this option is not available so it crashes.  So we try.
    result = execute_command(
        'svnadmin create --compatible-version=1.6 %s' % repodir)
    if Fore.RED in result:
        execute_command('svnadmin create %s' % repodir)

    repo_url = 'file://' + repodir  # TODO: urllib or so for windows
    # Import example project
    execute_command('svn mkdir %s/tha.example -m "mkdir"' % repo_url)
    execute_command('svn mkdir %s/tha.example/tags -m "mkdir"' % repo_url)
    execute_command(
        'svn import %s %s/tha.example/trunk -m "import"' % (sourcedir,
                                                            repo_url))
    # Subversion checkout
    svnsourcedir = os.path.join(test.tempdir, 'tha.example-svn')
    execute_command(
        'svn co %s/tha.example/trunk %s' % (repo_url, svnsourcedir))
    execute_command(
        'svn propset svn:ignore "tha.example.egg-info *.pyc" %s/src ' %
        svnsourcedir)
    execute_command('svn up %s' % svnsourcedir)
    execute_command('svn commit %s -m "ignoring egginfo"' % svnsourcedir)

    # Mercurial initialization
    hgsourcedir = os.path.join(test.tempdir, 'tha.example-hg')
    shutil.copytree(sourcedir, hgsourcedir)
    execute_command("hg init %s" % hgsourcedir)
    with open(os.path.join(hgsourcedir, '.hgignore'), 'wb') as f:
        f.write('tha.example.egg-info\n\\.pyc$\n'.encode('utf-8'))
    execute_command("hg add %s" % hgsourcedir)
    execute_command("hg commit -m 'init' %s" % hgsourcedir)

    # Bazaar initialization
    bzrsourcedir = os.path.join(test.tempdir, 'tha.example-bzr')
    shutil.copytree(sourcedir, bzrsourcedir)
    execute_command("bzr init %s" % bzrsourcedir)
    with open(os.path.join(bzrsourcedir, '.bzrignore'), 'w') as f:
        f.write('tha.example.egg-info\n*.pyc\n')
    execute_command("bzr add %s" % bzrsourcedir)
    execute_command("bzr commit -m 'init' %s" % bzrsourcedir)

    # Git initialization
    gitsourcedir = os.path.join(test.tempdir, 'tha.example-git')
    shutil.copytree(sourcedir, gitsourcedir)
    os.chdir(gitsourcedir)
    execute_command("git init")
    with open(os.path.join(gitsourcedir, '.gitignore'), 'w') as f:
        f.write('tha.example.egg-info\n*.pyc\n')
    execute_command("git add .")
    execute_command("git commit -a -m 'init'")
    os.chdir(test.orig_dir)

    # Git svn initialization
    gitsvnsourcedir = os.path.join(test.tempdir, 'tha.example-gitsvn')
    execute_command(
        'git svn clone -s %s/tha.example %s' % (repo_url, gitsvnsourcedir))
    os.chdir(test.orig_dir)

    def svnhead(*filename_parts):
        filename = os.path.join(svnsourcedir, *filename_parts)
        with open(filename) as f:
            lines = f.readlines()
        for line in lines[:5]:
            print(line.strip())

    def hghead(*filename_parts):
        filename = os.path.join(hgsourcedir, *filename_parts)
        with open(filename) as f:
            lines = f.readlines()
        for line in lines[:5]:
            print(line.strip())

    def bzrhead(*filename_parts):
        filename = os.path.join(bzrsourcedir, *filename_parts)
        with open(filename) as f:
            lines = f.readlines()
        for line in lines[:5]:
            print(line.strip())

    def githead(*filename_parts):
        filename = os.path.join(gitsourcedir, *filename_parts)
        with open(filename) as f:
            lines = f.readlines()
        for line in lines[:5]:
            print(line.strip())

    def add_changelog_entry():
        # Replace '- Nothing changed yet.'  by a different entry.
        with open('CHANGES.txt') as f:
            orig_changes = f.read()
        new_changes = orig_changes.replace(
            NOTHING_CHANGED_YET, '- Brown bag release.')
        with open('CHANGES.txt', 'w') as f:
            f.write(new_changes)

    test.globs.update({'unicode_literals': unicode_literals,
                       'tempdir': test.tempdir,
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
