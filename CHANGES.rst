Changelog for zest.releaser
===========================

7.1.0 (2022-11-23)
------------------

- Add the ``bumpversion`` options to the ``postrelease`` command.
  This means ``feature``, ``breaking``, and ``final``.
  [rnc, maurits]

- Add ``--final`` option to ``bumpversion`` command.
  This removes alpha / beta / rc markers from the version.
  [maurits]

- Add support for Python 3.11, remove ``z3c.testsetup`` from test dependencies.  [maurits]


7.0.0 (2022-09-09)
------------------

- Optionally add prefix text to commit messages.  This can be used ensure your messages follow some regular expression.
  To activate this, add ``prefix-message = [TAG]`` to a ``[zest.releaser]``
  section in the ``setup.cfg`` of your package, or your global
  ``~/.pypirc``.  Or add your favorite geeky quotes there.
  [LvffY]


7.0.0a3 (2022-04-04)
--------------------

- Bug 381: In ``prerelease``, check with ``pep440`` if the version is canonical.
  Added ``pep440`` to the ``recommended`` extra, not to the core dependencies:
  ``zest.releaser`` can also be used for non-Python projects.
  [maurits]


7.0.0a2 (2022-02-10)
--------------------

- Add ``--headless`` option to ``longtest``.


7.0.0a1 (2021-12-01)
--------------------

Big cleanup to ease future development:

- Removed support for Subversion (``svn``), Bazaar (``bzr``), Mercurial (``hg``).

- Removed support for Python 2 and 3.5.

- Added support for Python 3.9 and 3.10.

- Tested with Python 3.6-3.10 plus PyPy3.

- Switched from Travis to GitHub Actions.

- Simplified running commands by using ``subprocess.run``.


.. # Note: for older changes see ``doc/sources/changelog.rst``.
