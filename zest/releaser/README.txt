Package releasing made easy
===========================


zest.releaser is collection of command-line programs to help you
automate the task of releasing a software project. It's particularly
helpful with Python package projects, but it can also be used for
non-Python projects. For example, it's used to tag buildouts - a project
only needs a ``version.txt`` file to be used with zest.releaser.

It will help you to automate:

* Updating the version number. The version number can either be in
  setup.py or version.txt. For example, 0.3.dev0 (current) to 0.3
  (release) to 0.4.dev0 (new development version).

* Updating the history/changes file. It logs the release date on release
  and adds a new section for the upcoming changes (new development version).

* Tagging the release. It creates a tag in your version control system
  named after the released version number.

* Uploading a source release to PyPI. It will only do this if the
  package is already registered there (else it will ask, defaulting to
  'no'); the Zest Releaser is careful not to publish your private
  projects! It can also check out the tag in a temporary directory in
  case you need to modify it.

.. contents::


Installation
------------

Getting a good installation consists of two steps: getting the
zest.releaser commands, and setting up your environment so you can
upload releases to pypi (if you want that).

Get the zest.releaser commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Just a simple ``pip zest.releaser`` or ``easy_install zest.releaser``
is enough.

Alternatively, buildout users can install zest.releaser as part of a
specific project's buildout, by having a buildout configuration such as::

    [buildout]
    parts = releaser

    [releaser]
    recipe = zc.recipe.egg
    eggs = zest.releaser


Prepare for pypi distribution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Of course you must have a version control system installed.
zest.releaser currently supports:

- Subversion (svn)

- Mercurial (hg)

- Git (git)

- Bazaar (bzr)

Others could be added if there are volunteers.

When the (full)release command tries to upload your package to a pypi
server, zest.releaser basically just executes the command ``python
setup.py register sdist upload``.  The ``python`` here is the same
python that was used to install zest.releaser.  If that command would
fail when you try it manually (for example because you have not
configured a .pypirc file yet), then zest.releaser does not magically
make it work.  This means that you may need to have some extra python
packages installed:

- setuptools or distribute (when using subversion 1.5 or higher you
  need setuptools 0.6c11 or higher or any distribute version)

- setuptools-git (Setuptools plugin for finding files under Git
  version control)

- setuptools_hg (Setuptools plugin for finding files under Mercurial
  version control)

- setuptools_bzr (Setuptools plugin for finding files under Bazaar
  version control)

- collective.dist (when using python2.4, depending on your
  ``~/.pypirc`` file)

- setuptools_subversion (Setuptools plugin for finding files under
  Subversion version control.)  You probably need this when you
  upgrade to the recent subversion 1.7.  If you suddenly start missing
  files in the sdists you upload to PyPI you definitely need it.
  Alternatively: set up a proper MANIFEST.in as that method works with
  any version control system.

The setuptools plugins are mostly so you do not miss files in the
generated sdist that is uploaded to pypi.

For more info, see the section on `Uploading to pypi server(s)`_.

In general, if you are missing files in the uploaded package, the best
is to put a proper ``MANIFEST.in`` file next to your ``setup.py``.
See `zest.pocompile`_ for an example.

.. _`zest.pocompile`: http://pypi.python.org/pypi/zest.pocompile


Running
-------

Zest.releaser gives you four commands to help in releasing python
packages.  They must be run in a version controlled checkout.  The commands
are:

- **prerelease**: asks you for a version number (defaults to the current
  version minus a 'dev' or so), updates the setup.py or version.txt and the
  HISTORY.txt/CHANGES.txt/CHANGES with this new version number and offers to
  commit those changes to subversion (or bzr or hg or git)

- **release**: copies the the trunk or branch of the current checkout and
  creates a version control tag of it.  Makes a checkout of the tag in a
  temporary directory.  Offers to register and upload a source dist
  of this package to PyPI (Python Package Index).  Note: if the package has
  not been registered yet, it will not do that for you.  You must register the
  package manually (``python setup.py register``) so this remains a conscious
  decision.  The main reason is that you want to avoid having to say: "Oops, I
  uploaded our client code to the internet; and this is the initial version
  with the plaintext root passwords."

- **postrelease**: asks you for a version number (gives a sane default), adds
  a development marker to it, updates the setup.py or version.txt and the
  HISTORY.txt/CHANGES.txt with this and offers to commit those changes to
  version control. Note that with git and hg, you'd also be asked to push your
  changes (since 3.27). Otherwise the release and tag only live in your local
  hg/git repository and not on the server.

- **fullrelease**: all of the above in order.

There are two additional tools:

- **longtest**: small tool that renders a setup.py's long description
  and opens it in a web browser. This assumes an installed docutils
  (as it needs ``rst2html.py``).

- **lasttagdiff**: small tool that shows the diff of the currently committed
  trunk with the last released tag.  Handy for checking whether all the
  changes are adequately described in the HISTORY.txt/CHANGES.txt.


Details
=======


Current assumptions
-------------------

Zest.releaser originated at `Zest software <http://zestsoftware.nl>`_ so there
are some assumptions build-in that might or might not fit you.  Lots of people
are using it in various companies and open source projects, so it'll probably
fit :-)

- If you are using svn, your svn is structured with /trunk, /tags (or
  /tag) and optionally /branches (or /branch).  Both a /trunk or a
  /branches/something checkout is ok.

- There's a version.txt or setup.py in your project. The version.txt
  has a single line with the version number (newline optional). The
  setup.py should have a single ``version = '0.3'`` line
  somewhere. You can also have it in the actual ``setup()`` call, on
  its own line still, as `` version = '0.3',``. Indentation and the
  comma are preserved.  If you need something special, you can always
  do a ``version=version`` and put the actual version statement in a
  zest.releaser-friendly format near the top of the file. Reading (in
  Plone products) a version.txt into setup.py works great, too.

- The history file (either HISTORY.txt, CHANGES.txt or CHANGES)
  restriction is probably the most severe at the moment. zest.releaser
  searches for a restructuredtext header with parenthesis. So
  something like::

    Changelog for xyz
    =================

    0.3 (unreleased)
    ----------------

    - Did something

    0.2 (1972-12-25)
    ----------------

    - Reinout was born.

  That's just the style we started with.  Pretty clear and useful.  It also
  supports the current zopeskel style with ``0.3 - unreleased``.

- If using Python 2.4 you don't want to have tar.gz eggs due to `an obscure bug
  on python <http://bugs.python.org/issue1719898>`_


Development notes, bug tracker
------------------------------

The source code can be found on github:
https://github.com/zestsoftware/zest.releaser

If you are going to do a fix or want to run the tests, please see the
``DEVELOPERS.txt`` file in the root of the package.

Bugs can be added to https://bugs.launchpad.net/zest.releaser .

Note that there are alternative release scripts available, for instance
http://pypi.python.org/pypi/collective.releaser which installs itself as a
setuptools command ("python setup.py release"), so it "only" works with
setuptools projects.


Uploading to pypi server(s)
---------------------------

Like noted earlier, for safety reasons zest.releaser will only offer
to upload your package to http://pypi.python.org when the package is
already registered there.  If this is not the case yet, you can go to
the directory where zest.releaser put the checkout (or make a fresh
checkout yourself.  Then with the python version of your choice do::

  python setup.py register sdist upload

For this to work you will need a ``.pypirc`` file in your home
directory that has your pypi login credentials like this::

  [server-login]
  username:maurits
  password:secret

Since python 2.6, or in earlier python versions with collective.dist,
you can specify multiple indexes for uploading your package in
``.pypirc``::

  [distutils]
  index-servers =
    pypi
    local

  [pypi]
  #pypi.python.org
  username:maurits
  password:secret

  [local]
  repository:http://localhost:8080/test/products/
  username:maurits
  password:secret
  # You may need to specify the realm, which is the domain the
  # server sends back when you do a challenge:
  #realm:Zope

See http://pypi.python.org/pypi/collective.dist for more info.

When all this is configured correctly, zest.releaser will first
reregister and upload at the official pypi (if the package is
registered there already).  Then it will offer to upload to the other
index servers that you have specified in ``.pypirc``.

Note that since version 3.15, zest.releaser also looks for this
information in the setup.cfg if your package has that file.  One way
to use this, is to restrict the servers that zest.releaser will ask
you upload to.  If you have defined 40 index-servers in your pypirc
but you have the following in your setup.cfg, you will not be asked to
upload to any server::

  [distutils]
  index-servers =

Note that after creating the tag we still ask you if you want to
checkout that tag for tweaks or pypi/distutils server upload.  We
could add some extra checks to see if that is really needed, but
someone who does not have index-servers listed, may still want to use
an entry point like `gocept.zestreleaser.customupload`_ to do
uploading, or do some manual steps first before uploading.

Some people will hardly ever want to do a release on PyPI but in 99
out of 100 cases only want to create a tag.  They won't like the
default answer of 'yes' to that question of whether to create a
checkout of the tag.  So since version 3.16 you can influence this
default answer.  You can add some lines to the ``.pypirc`` file in
your home directory to change the default answer for all packages, or
change it for individual packages in their ``setup.cfg`` file.  The
lines are this::

  [zest.releaser]
  release = no

You can use no/false/off/0 or yes/true/on/1 as answers; upper, lower
or mixed case are all fine.
