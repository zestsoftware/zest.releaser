Information for developers of zest.releaser itself
===================================================

**Note:** the whole test setup used to be quite elaborate and hard to get right.
Since version 7, this is much less so.
You just need ``git`` and ``tox``.

If you still run into problems, there is a solution however: docker.
See the next section on this page.
It is still work-in-progress, we'll probably add a docker-compose file, for
example. And support for testing different python versions with docker. (3.8
is used now).

So: for easy testing, use the docker commands, described next.
The rest of the document explains the original test setup requirements.


Testing with docker
-------------------

If you have docker installed, all you need to do to run the tests is::

  $ docker build . -t zest:dev
  $ docker run --rm zest:dev

The "build" step runs bootstrap and buildout. Re-run it periodically to get
the latest versions of if you've changed the buildout config.

Note: buildout should not be needed anymore, because we use ``tox``.
So the Dockerfile was updated, but not tested.

The "run" command runs the tests. It uses the code copied into the dockerfile
in the build step, but you probably want to test your current version. For
that, mount the code directory into the docker::

  $ docker run --rm -v $(pwd):/zest.releaser/ zest:dev


Running tests
-------------

Actually, this should be easy now, because we use tox.
So ``pip install tox`` somewhere, probably in a virtualenv, maybe the current directory,
and call it:

    tox

You probably want to run the tests for all environments in parallel::

    tox -p auto

To run a specific environment and a specific test file::

    tox -e py38 -- utils.txt


Python versions
---------------

The tests currently pass on python 3.6-3.10 and PyPy3.


Necessary programs
------------------

To run the tests, you need to have the supported versioning systems installed.
Since version 7, we only support ``git``.
On ubuntu::

  $ sudo apt-get install git

There may be test failures when you have different versions of these programs.
In that case, please investigate as these may be genuine errors.
In the past, ``git`` commands would give slightly different output.
If the output of a command changes again, we may need extra compatibility code in ``test_setup.py``


Setuptools is needed
--------------------

You also need ``setuptools`` in your system path.  This is because
we basically call 'sys.executable setup.py egg_info' directly (in the tests
and in the actual code), which will give an import error on setuptools
otherwise.  There is a branch with a hack that solves this but it sounds too
hacky.

TODO: calling ``setup.py`` from the command line is not recommended anymore.
We should upgrade the code to no longer do that.


Building the documentation locally
-------------------------------------

If you worked on the documentation, we suggest you verify the markup
and the result by building the documentation locally and view your
results.

For building the documentation::

    $ python3.9 -mvenv .
    $ bin/pip install sphinx sphinx_rtd_theme
    $ bin/pip install -e .
    $ bin/sphinx-build doc/source/ doc/build/

For viewing the documentation open :file:`doc/build/html/index.html`
in your browser, e.g. by running::

    $ xdg-open doc/build/html/index.html
