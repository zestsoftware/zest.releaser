Package releasing made easy
===========================


zest.releaser is collection of command-line programs to help you
automate the task of releasing a software project. It's particularly
helpful with Python package projects, but it can also be used for
non-Python projects. For example, it's used to tag buildouts - a project
only needs a ``version.txt`` file to be used with zest.releaser.

It will help you to automate:

* Updating the version number. The version number can either be in setup.py
  or version.txt. For example, 0.3 dev (current) to 0.3 (release) to 0.4 dev
  (new development version).

* Updating the history/changes file. It logs the release date on release
  and adds a new section for the upcoming changes (new development version).

* Tagging the release. It creates a tag in your version control system
  named after the released version number.

* Uploading a source release to PyPI. It will only do this if the package
  is already registered there, the Zest Releaser is careful not to publish
  your private projects! It can also check out the tag in a temporary
  directory in case you need to modify it.

.. contents::


Installation
------------

Just a simple ``easy_install zest.releaser`` is enough.

Alternatively, buildout users can install zest.releaser as part of a
specific project's buildout, by having a buildout configuration such as::

    [buildout]
    parts = releaser

    [releaser]
    recipe = zc.recipe.egg
    eggs = zest.releaser


You must also have a version control system installed. Zest.releaser currently
supports Subversion, Mercurial and Git (and others could be added).


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
  HISTORY.txt with this and offers to commit those changes to version control.

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

- If you are using svn, your svn is structured with /trunk, /tags and
  optionally /branches.  Both a /trunk or a /branches/something checkout
  is ok.

- There's a version.txt or setup.py in your project. The version.txt
  has a single line with the version number (newline optional). The
  setup.py should have a single ``version = '0.3'`` line
  somewhere. You can also have it in the actual ``setup()`` call, on
  its own line still, as `` version = '0.3',``. Indentation and the
  comma are preserved.  If you need something special, you can always
  do a ``version=version`` and put the actual version statement in a
  zest.releaser-friendly format near the top of the file. Reading (in
  Plone products) a version.txt into setup.py works great, too.

- The history file (either HISTORY.txt or CHANGES.txt) restriction is probably
  the most severe at the moment. zest.releaser searches for a restructuredtext
  header with parenthesis. So something like::

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

The svn source can be found at
https://svn.plone.org/svn/collective/zest.releaser/trunk . If you have access
to the collective, you can fix bugs right away.  Bigger changes on a branch
please and mail reinout@vanrees.org and maurits@vanrees.org about it :-)

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
