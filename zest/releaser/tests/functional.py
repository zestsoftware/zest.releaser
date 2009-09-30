"""Set up functional test fixtures"""
import commands
import os
import shutil
import tempfile
import pkg_resources
import tarfile


def setup(test):
    test.tempdir = tempfile.mkdtemp()
    # TODO: check if svnadmin is installed and set variable accordingly.
    # Init svn repo.
    repodir = os.path.join(test.tempdir, 'svnrepo')
    commands.getoutput('svnadmin create %s' % repodir)
    repo_url = 'file://' + repodir # TODO: urllib or so for windows
    # Prepare and check in example project
    # Note: extractall only exists in python2.5
    example_tar = pkg_resources.resource_filename(
        'zest.releaser.tests', 'example.tar')
    tarfile.TarFile(example_tar).extractall(path=test.tempdir)
    sourcedir = os.path.join(test.tempdir, 'tha.example')
    commands.getoutput('svn mkdir %s/tha.example -m "mkdir"' % repo_url)
    commands.getoutput('svn mkdir %s/tha.example/tags -m "mkdir"' % repo_url)
    commands.getoutput(
        'svn import %s %s/tha.example/trunk -m "import"' % (sourcedir,
                                                            repo_url))
    # Zap the source dir and make it a checkout
    shutil.rmtree(sourcedir)
    commands.getoutput(
        'svn co %s/tha.example/trunk %s' % (repo_url, sourcedir))

    test.globs.update({'tempdir': test.tempdir,
                       'repo_url': repo_url,
                       'sourcedir': sourcedir})


def teardown(test):
    # Temporary we don't clean up the temp dir as we're setting up the test
    # setup, so we need to be able to see what happens.
    print "Left over tempdir:", test.tempdir

    # TODO: delete tempdir
    #shutil.rmtree(test.tempdir)

