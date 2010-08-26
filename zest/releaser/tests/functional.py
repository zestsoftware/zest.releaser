"""Set up functional test fixtures"""
import os
import pkg_resources
import shutil
import sys
import tarfile
import tempfile
import urllib2
import StringIO

from zest.releaser.utils import system
from zest.releaser.release import Releaser

orig_python24_check = None

def setup(test):
    partstestdir = os.getcwd() # Buildout's test run in parts/test
    test.orig_dir = partstestdir
    buildoutbindir = os.path.join(partstestdir, '..', '..', 'bin')
    test.tempdir = tempfile.mkdtemp(prefix='testtemp')

    # Monkey patch sys.exit
    test.orig_exit = sys.exit

    # Monkey patch for python 24 check. Otherwise we would need different tests
    # For python24 and higher
    orig_python24_check = Releaser._is_python24
    Releaser._is_python24 = lambda(self): False

    def _exit(code=None):
        msg = "SYSTEM EXIT (code=%s)" % code
        raise RuntimeError(msg)

    sys.exit = _exit

    # Monkey patch urllib for pypi access mocking.
    test.orig_urlopen = urllib2.urlopen
    test.mock_pypi_available = []

    def _mock_urlopen(url):
        #print "Mock opening", url
        package = url.replace('http://pypi.python.org/simple/', '')
        if package not in test.mock_pypi_available:
            raise urllib2.HTTPError(
                url, 404,
                'HTTP Error 404: Not Found (%s does not have any releases)'
                % package, None, None)
        else:
            answer = ' '.join(test.mock_pypi_available)
        return StringIO.StringIO(buf=answer)

    urllib2.urlopen = _mock_urlopen

    # Extract example project
    example_tar = pkg_resources.resource_filename(
        'zest.releaser.tests', 'example.tar')
    tf = tarfile.TarFile(example_tar)
    try:
        tf.extractall(path=test.tempdir)
    except AttributeError:
        # BBB for python2.4
        for name in tf.getnames():
            tf.extract(name, test.tempdir)


    sourcedir = os.path.join(test.tempdir, 'tha.example')

    # Init svn repo.
    repodir = os.path.join(test.tempdir, 'svnrepo')
    system('svnadmin create %s' % repodir)
    repo_url = 'file://' + repodir # TODO: urllib or so for windows
    # Import example project
    system('svn mkdir %s/tha.example -m "mkdir"' % repo_url)
    system('svn mkdir %s/tha.example/tags -m "mkdir"' % repo_url)
    system(
        'svn import %s %s/tha.example/trunk -m "import"' % (sourcedir,
                                                            repo_url))
    # Subversion checkout
    svnsourcedir = os.path.join(test.tempdir, 'tha.example-svn')
    system(
        'svn co %s/tha.example/trunk %s' % (repo_url, svnsourcedir))
    system(
        'svn propset svn:ignore tha.example.egg-info %s/src '% svnsourcedir)
    system('svn up %s' % svnsourcedir)
    system('svn commit %s -m "ignoring egginfo"' % svnsourcedir)

    # Mercurial initialization
    hgsourcedir = os.path.join(test.tempdir, 'tha.example-hg')
    shutil.copytree(sourcedir, hgsourcedir)
    system("hg init %s" % hgsourcedir)
    open(os.path.join(hgsourcedir, '.hgignore'), 'w').write(
        'tha.example.egg-info\n')
    system("hg add %s" % hgsourcedir)
    system("hg commit -m 'init' %s" % hgsourcedir)

    # Bazaar initialization
    bzrsourcedir = os.path.join(test.tempdir, 'tha.example-bzr')
    shutil.copytree(sourcedir, bzrsourcedir)
    system("bzr init %s" % bzrsourcedir)
    open(os.path.join(bzrsourcedir, '.bzrignore'), 'w').write(
        'tha.example.egg-info\n')
    system("bzr add %s" % bzrsourcedir)
    system("bzr commit -m 'init' %s" % bzrsourcedir)

    # Git initialization
    gitsourcedir = os.path.join(test.tempdir, 'tha.example-git')
    shutil.copytree(sourcedir, gitsourcedir)
    os.chdir(gitsourcedir)
    system("git init")
    open(os.path.join(gitsourcedir, '.gitignore'), 'w').write(
        'tha.example.egg-info\n')
    system("git add .")
    system("git commit -a -m 'init'")
    os.chdir(test.orig_dir)

    # Git svn initialization
    gitsvnsourcedir = os.path.join(test.tempdir, 'tha.example-gitsvn')
    system(
        'git svn clone -s %s/tha.example %s' % (repo_url, gitsvnsourcedir))
    os.chdir(test.orig_dir)

    def svnhead(*filename_parts):
        filename = os.path.join(svnsourcedir, *filename_parts)
        lines = open(filename).readlines()
        for line in lines[:5]:
            print line,

    def hghead(*filename_parts):
        filename = os.path.join(hgsourcedir, *filename_parts)
        lines = open(filename).readlines()
        for line in lines[:5]:
            print line,

    def bzrhead(*filename_parts):
        filename = os.path.join(bzrsourcedir, *filename_parts)
        lines = open(filename).readlines()
        for line in lines[:5]:
            print line,

    def githead(*filename_parts):
        filename = os.path.join(gitsourcedir, *filename_parts)
        lines = open(filename).readlines()
        for line in lines[:5]:
            print line,

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
                       })


def teardown(test):
    sys.exit = test.orig_exit
    urllib2.urlopen = test.orig_urlopen
    os.chdir(test.orig_dir)
    #print "Left over tempdir:", test.tempdir
    shutil.rmtree(test.tempdir)


def restore_mupload(test):
    from zest.releaser import pypi

    # Undo monkey patch
    Releaser._is_python24 = orig_python24_check
    try:
        from collective.dist import mupload
    except ImportError:
        mupload = None
    pypi.mupload = mupload
