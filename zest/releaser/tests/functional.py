"""Set up functional test fixtures"""
import shutil
import tempfile


def setup(test):
    test.tempdir = tempfile.mkdtemp()
    test.globs.update({'tempdir': test.tempdir})


def teardown(test):
    # Temporary we don't clean up the temp dir as we're setting up the test
    # setup, so we need to be able to see what happens.
    print "Left over tempdir:", test.tempdir

    # TODO: delete tempdir
    #shutil.rmtree(test.tempdir)

