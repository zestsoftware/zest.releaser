Information for developers of zest.releaser itself
===================================================

**Note:** the whole test setup used to be quite elaborate and hard to get right.
Since version 7, this is much less so.
You just need ``git`` and ``tox``.

If you still run into problems, there is a solution however: docker.
See the next section on this page.
It is still work-in-progress, we'll probably add a docker-compose file, for
example. And support for testing different python versions with docker. (3.13
is used now).

So: for easy testing, use the docker commands, described next.
The rest of the document explains the original test setup requirements.


Testing with docker
-------------------

If you have docker installed, all you need to do to run the tests is::

  $ docker build . -t zest:dev
  $ docker run --rm zest:dev

The "run" command runs the tests. It uses the code copied into the dockerfile
in the build step, but you probably want to test your current version. For
that, mount the code directory into the docker::

  $ docker run --rm -v $(pwd):/zest.releaser/ zest:dev


Running tests
-------------

Actually, this should be easy now, because we use tox.
So ``pip install tox`` somewhere, probably in a virtualenv, maybe the current directory,
and call it::

    $ tox

You probably want to run the tests for all environments in parallel::

    $ tox -p auto

To run a specific environment and a specific test file::

    $ tox -e py38 -- utils.txt


Code formatting
---------------

We use black/flake8/isort. To make it easy to configure and run, there's a
pre-commit config. Enable it with::

    $ pre-commit install

That will run it before every commit. You can also run it periodically when
developing::

    $ pre-commit run --all


Python versions
---------------

The tests currently pass on python 3.10-3.13 and PyPy 3.11.


Necessary programs
------------------

To run the tests, you need to have the supported versioning systems installed.
Since version 7, we only support ``git``, which you already have installed
probably :-)

There may be test failures when you have different versions of these programs.
In that case, please investigate as these *may* be genuine errors.  In the
past, ``git`` commands would give slightly different output.  If the output of
a command changes again, we may need extra compatibility code in
``test_setup.py``.


Building the documentation locally
-------------------------------------

If you worked on the documentation, we suggest you verify the markup
and the result by building the documentation locally and view your
results.

For building the documentation::

    $ python3.9 -m venv .
    $ bin/pip install sphinx sphinx_rtd_theme
    $ bin/pip install -e .
    $ bin/sphinx-build doc/source/ doc/build/

For viewing the documentation open :file:`doc/build/html/index.html`
in your browser, e.g. by running::

    $ xdg-open doc/build/html/index.html
