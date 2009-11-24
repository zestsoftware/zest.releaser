"""Set up functional test fixtures"""
import commands
import os
import pkg_resources
import shutil
import sys
import tarfile
import tempfile
import urllib
import StringIO


def setup(test):
    partstestdir = os.getcwd() # Buildout's test run in parts/test
    test.orig_dir = partstestdir
    buildoutbindir = os.path.join(partstestdir, '..', '..', 'bin')
    test.tempdir = tempfile.mkdtemp()

    # Monkey patch sys.exit
    test.orig_exit = sys.exit

    def _exit(code=None):
        msg = "SYSTEM EXIT (code=%s)" % code
        raise RuntimeError(msg)

    sys.exit = _exit

    # Monkey patch urllib for pypi access mocking.
    test.orig_urlopen = urllib.urlopen
    test.mock_pypi_available = []

    def _mock_urlopen(url):
        #print "Mock opening", url
        package = url.replace('http://pypi.python.org/simple/', '')
        if package not in test.mock_pypi_available:
            answer = 'Not found'
        else:
            answer = ' '.join(test.mock_pypi_available)
        return StringIO.StringIO(buf=answer)

    urllib.urlopen = _mock_urlopen

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
    commands.getoutput('svnadmin create %s' % repodir)
    repo_url = 'file://' + repodir # TODO: urllib or so for windows
    # Import example project
    commands.getoutput('svn mkdir %s/tha.example -m "mkdir"' % repo_url)
    commands.getoutput('svn mkdir %s/tha.example/tags -m "mkdir"' % repo_url)
    commands.getoutput(
        'svn import %s %s/tha.example/trunk -m "import"' % (sourcedir,
                                                            repo_url))
    # Subversion checkout
    svnsourcedir = os.path.join(test.tempdir, 'tha.example-svn')
    commands.getoutput(
        'svn co %s/tha.example/trunk %s' % (repo_url, svnsourcedir))

    # Mercurial initialization
    hgsourcedir = os.path.join(test.tempdir, 'tha.example-hg')
    shutil.copytree(sourcedir, hgsourcedir)
    commands.getoutput("hg init %s" % hgsourcedir)
    commands.getoutput("hg add %s" % hgsourcedir)
    commands.getoutput("hg commit -m 'init' %s" % hgsourcedir)

    # Git initialization
    gitsourcedir = os.path.join(test.tempdir, 'tha.example-git')
    shutil.copytree(sourcedir, gitsourcedir)
    os.chdir(gitsourcedir)
    commands.getoutput("git init")
    commands.getoutput("git add .")
    commands.getoutput("git commit -a -m 'init'")
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

    def githead(*filename_parts):
        filename = os.path.join(gitsourcedir, *filename_parts)
        lines = open(filename).readlines()
        for line in lines[:5]:
            print line,

    test.globs.update({'tempdir': test.tempdir,
                       'repo_url': repo_url,
                       'svnsourcedir': svnsourcedir,
                       'hgsourcedir': hgsourcedir,
                       'gitsourcedir': gitsourcedir,
                       'svnhead': svnhead,
                       'hghead': hghead,
                       'githead': githead,
                       'mock_pypi_available': test.mock_pypi_available,
                       })


def teardown(test):
    sys.exit = test.orig_exit
    urllib.urlopen = test.orig_urlopen
    os.chdir(test.orig_dir)
    #print "Left over tempdir:", test.tempdir
    shutil.rmtree(test.tempdir)


def restore_mupload(test):
    from zest.releaser import pypi
    try:
        from collective.dist import mupload
    except ImportError:
        mupload = None
    pypi.mupload = mupload
