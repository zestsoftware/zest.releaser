Information for developers of zest.releaser
===========================================

Running tests
-------------

We like to use zc.buildout to get a test environment with any versions of
needed python packages pinned.  When you are in the root folder of your
zest.releaser checkout, do this::

  $ python bootstrap.py  # Or a different python version.
  $ bin/buildout
  $ bin/test


Python versions
---------------

The tests currently pass on python 2.6 and 2.7. Using
2.6.2 specifically will give test failures. Travis continuous integration
tests 2.6 and 2.7 for us automatically.


Necessary programs
------------------

To run the tests, you need to have the supported versioning systems
installed: svn, hg (mercurial), git and git-svn. On ubuntu::

  $ sudo apt-get install subversion git bzr mercurial git-svn

There may be test failures when you have different versions of these programs.
In that case, please investigate as these may be genuine errors.


Setuptools is needed
--------------------

You also need distribute (or setuptools) in your system path.  This is because
we basically call 'sys.executable setup.py egg_info' directly (in the tests
and in the actual code), which will give an import error on setuptools
otherwise.  There is a branch with a hack that solves this but it sounds too
hacky.


Configuration for mercurial, bzr and git
----------------------------------------

For mercurial you may get test failures because of extra output like
this::

  No username found, using 'name@domain' instead.

To avoid this, create a file ~/.hgrc with something like this in it::

  [ui]
  username = Author Name <email@address.domain>

If you keep having problems, `Ubuntu explains it
<https://help.ubuntu.com/community/Mercurial>`_ quite good.

There is a similar problem with bazaar.  Since bzr version 2.2, it
refuses to guess what your username and email is, so you have to
set it once, like this, otherwise you get test failures::

  $ bzr whoami "Author Name <email@address.domain>"

And the same for git, so you should do::

  $ git config --global user.name "Your Name"
  $ git config --global user.email you@example.com

For release testing we expected a functioning .pypirc file in your
home dir, with an old-style configuration, but the tests now use an
own config file.
