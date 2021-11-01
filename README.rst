Package releasing made easy: zest.releaser overview and installation
====================================================================

zest.releaser is collection of command-line programs to help you automate the
task of releasing a Python project.

It does away with all the boring bits. This is what zest.releaser automates
for you:

* It updates the version number. The version number can either be in
  ``setup.py`` or ``version.txt`` or in a ``__versions__`` attribute in a
  Python file or in ``setup.cfg``. For example, it switches you from
  ``0.3.dev0`` (current development version) to ``0.3`` (release) to
  ``0.4.dev0`` (new development version).

* It updates the history/changes file. It logs the release date on release and
  adds a new heading for the upcoming changes (new development version).

* It tags the release. It creates a tag in your version control system named
  after the released version number.

* It optionally uploads a source release to PyPI. It will only do this if the
  package is already registered there (else it will ask, defaulting to 'no');
  zest releaser is careful not to publish your private projects!


Most important URLs
-------------------

First the three most important links:

- The full documentation is at `zestreleaser.readthedocs.io
  <https://zestreleaser.readthedocs.io>`_.

- We're `on PyPI <https://pypi.org/project/zest.releaser>`_, so we're only
  an ``pip install zest.releaser`` away from installation on your computer.

- The code is at `github.com/zestsoftware/zest.releaser
  <https://github.com/zestsoftware/zest.releaser>`_.


Compatibility / Dependencies
----------------------------

.. image:: https://img.shields.io/pypi/pyversions/zest.releaser?   :alt: PyPI - Python Version
.. image:: https://img.shields.io/pypi/implementation/zest.releaser?   :alt: PyPI - Implementation

``zest.releaser`` works on Python 3.6+, including PyPy3.
Tested until Python 3.10, but see ``tox.ini`` for the canonical place for that.

To be sure: the packages that you release with ``zest.releaser`` may
very well work on other Python versions: that totally depends on your
package.

We depend on:

- ``setuptools`` for the entrypoint hooks that we offer.

- ``colorama`` for colorized output (some errors printed in red).

- ``twine`` for secure uploading via https to pypi. Plain setuptools doesn't
  support this.

Since version 4.0 there is a ``recommended`` extra that you can get by
installing ``zest.releaser[recommended]`` instead of ``zest.releaser``.  It
contains a few trusted add-ons that we feel are useful for the great majority
of ``zest.releaser`` users:

- wheel_ for creating a Python wheel that we upload to PyPI next to
  the standard source distribution.  Wheels are the new Python package
  format.  Create or edit ``setup.cfg`` in your project (or globally
  in your ``~/.pypirc``) and create a section ``[zest.releaser]`` with
  ``create-wheel = yes`` to create a wheel to upload to PyPI.  See
  http://pythonwheels.com for deciding whether this is a good idea for
  your package.  Briefly, if it is a pure Python 2 *or* pure Python 3
  package: just do it. If it is a pure Python 2 *and* a pure Python 3
  project, it is known as a "universal" wheel, because one wheel can
  be installed on all implementations and versions of Python. If you
  indicate this in ``setup.cfg`` with the section ``[bdist_wheel]``
  having ``universal = 1``, then we will automatically upload a wheel,
  unless ``create-wheel`` is explicitly set to false.

- `check-manifest`_ checks your ``MANIFEST.in`` file for completeness,
  or tells you that you need such a file.  It basically checks if all
  version controlled files are ending up the the distribution that we
  will upload.  This may avoid 'brown bag' releases that are missing
  files.

- pyroma_ checks if the package follows best practices of Python
  packaging.  Mostly it performs checks on the ``setup.py`` file, like
  checking for Python version classifiers.

- chardet_, the universal character encoding detector. To do the right thing
  in case your readme or changelog is in a non-utf-8 character set.

- readme_ to check your long description in the same way as pypi does. No more
  unformatted restructured text on your pypi page just because there was a
  small error somewhere. Handy.

.. _wheel: https://pypi.org/project/wheel
.. _`check-manifest`: https://pypi.org/project/check-manifest
.. _pyroma: https://pypi.org/project/pyroma
.. _chardet: https://pypi.org/project/chardet
.. _readme: https://pypi.org/project/readme


Installation
------------

Just a simple ``pip install zest.releaser`` or ``easy_install zest.releaser`` is
enough. If you want the recommended extra utilities, do a ``pip install
zest.releaser[recommended]``.

Alternatively, buildout users can install zest.releaser as part of a specific
project's buildout, by having a buildout configuration such as::

    [buildout]
    parts =
        scripts

    [scripts]
    recipe = zc.recipe.egg
    eggs = zest.releaser[recommended]


Version control systems: svn, hg, git, bzr
------------------------------------------

Of course you must have a version control system installed.  zest.releaser
currently supports:

- Subversion (svn).

- Mercurial (hg).

- Git (git).

- Git-svn.

- Bazaar (bzr).

Others could be added if there are volunteers! Git and mercurial support
have been contributed years ago when we were working with bzr and subversion,
for instance.


Available commands
------------------

Zest.releaser gives you four commands to help in releasing python
packages.  They must be run in a version controlled checkout.  The commands
are:

- **prerelease**: asks you for a version number (defaults to the current
  version minus a 'dev' or so), updates the setup.py or version.txt and the
  CHANGES/HISTORY/CHANGELOG file (with either .rst/.txt/.md/.markdown or no
  extension) with this new version number and offers to commit those changes
  to subversion (or bzr or hg or git).

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
  CHANGES/HISTORY/CHANGELOG file with this and offers to commit those changes
  to version control. Note that with git and hg, you'd also be asked to push
  your changes (since 3.27). Otherwise the release and tag only live in your
  local hg/git repository and not on the server.

- **fullrelease**: all of the above in order.

Note: markdown files should use the "underline" style of headings, not the
"atx" style where you prefix the headers with ``#`` signs.

There are some additional tools:

- **longtest**: small tool that renders a setup.py's long description
  and opens it in a web browser. This assumes an installed docutils
  (as it needs ``rst2html.py``).

- **lasttagdiff**: small tool that shows the *diff* of the current
  branch with the last released tag.  Handy for checking whether all
  the changes are adequately described in the changes file.

- **lasttaglog**: small tool that shows the *log* of the current
  branch since the last released tag.  Handy for checking whether all
  the changes are adequately described in the changes file.

- **addchangelogentry**: pass this a text on the command line and it
  will add this as an entry in the changelog.  This is probably mostly
  useful when you are making the same change in a batch of packages.
  The same text is used as commit message.  In the changelog, the text
  is indented and the first line is started with a dash.  The command
  detects it if you use for example a star as first character of an
  entry.

- **bumpversion**: do not release, only bump the version.  A
  development marker is kept when it is there.  With ``--feature`` we
  update the minor version.  With option ``--breaking`` we update the
  major version.
