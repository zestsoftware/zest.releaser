Changelog for zest.releaser
===========================

9.5.0 (2025-03-08)
------------------

- Worked around python 3.9 version-reporting issue that could prevent startup.
  [maurits]

- Really build source dist and wheel in isolation.
  Previously we passed along our own ``PYTHONPATH``, but that could lead to an unintended ``setuptools`` version being used.
  [maurits]


9.4.0 (2025-03-05)
------------------

- Requiring the ``wheel`` package now as everybody (rightfully so) uses wheels
  nowadays. It used to be an optional dependency beforehand, though often automatically
  included through setuptools' vendored libraries.
  You can switch off creation of wheels by setting the option ``create-wheel = false``.
  See our `options documentation <https://zestreleaser.readthedocs.io/en/latest/options.html>`_.
  [reinout]


9.3.1 (2025-03-04)
------------------

- Add ``packaging`` to our dependencies.
  We were already pulling this in via another dependency.
  [maurits]

- Removed remaining ``pkg_resources`` usage.
  [reinout, maurits]


9.3.0 (2025-03-03)
------------------

- Added python 3.13 compatibility (=pkg_resources deprecation).
  [stevepiercy]

- Added support for python 3.12 en 3.13 (=we're testing on those two now). 3.12 already
  worked fine, 3.13 needed the pkg_resources fix mentioned above.
  [reinout]

- Dropping support for python 3.8 as it is end of life.
  Also, the ``importlib`` we now use is still provisional in 3.8 and results in some errors.
  [reinout]


9.2.0 (2024-06-16)
------------------

- Fixed version handling documentation to use ``importlib`` instead of
  ``pkg_resources``.
  [reinout]

- Build distributions in an isolated environment.
  Otherwise `build` cannot install packages needed for the build system, for example `hatchling`.
  Fixes `issue 448 <https://github.com/zestsoftware/zest.releaser/issues/448>`_.
  [maurits]


9.1.3 (2024-02-07)
------------------

- Fix to the project setup. ``tox.ini`` uses ``extras =`` instead of ``deps =`` to
  install the test extras.
  [mtelka]


9.1.2 (2024-02-05)
------------------

- If you want to build a release package (release=true, the default), but don't want to
  actually upload it, you can now set the ``upload-pypi`` option to false (default is
  true).
  [leplatrem]


9.1.1 (2023-10-11)
------------------

- When reading ``~/.pypirc`` config, read ``setup.cfg`` as well, as it might
  override some of these values, like ``[distutils] index-servers``.
  Fixes issue #436.  [maurits]


9.1.0 (2023-10-03)
------------------

- Using newer 'build' (``>=1.0.0``) including a slight API change, fixes
  #433. [reinout]

- Typo fix in the readme: we look at ``__version__`` instead of
  the previously-documented ``__versions__``... [reinout]


9.0.0 (2023-09-11)
------------------

- Make final release.  Nothing changed since the last beta.  [maurits]


9.0.0b1 (2023-07-31)
--------------------

- When a command we call exits with a non-zero exit code, clearly state this in the output.
  Ask the user if she wants to continue or not.
  Note that this is tricky to do right.  Some commands like ``git`` seem to print everything to stderr,
  leading us to think there are errors, but the exit code is zero, so it should be fine.
  We do not want to ask too many questions, but we do not want to silently swallow important errors either.
  [maurits]


9.0.0a3 (2023-07-25)
--------------------

- Updated contributors list.

- Documenting ``hook_package_dir`` setting for entry points (which isn't
  needed for most entry points, btw).
  Fixes `issue 370 <https://github.com/zestsoftware/zest.releaser/issues/370>`_.

- Allowing for retry for ``git push``, which might fail because of a protected
  branch. Also displaying that possible cause when it occurs. Fixes `issue 385
  <https://github.com/zestsoftware/zest.releaser/issues/385>`_.


9.0.0a2 (2023-07-19)
--------------------

- Ignore error output when calling `build`.
  We only need to look at the exit code to see if it worked.
  You can call zest.releaser with ``--verbose`` if you want
  to see the possible warnings.

- Removed ``encoding`` config option as nobody is using it anymore (using the
  option would result in a crash). Apparently it isn't needed anymore now that
  we don't use python 2 anymore. Fixes `issue 391
  <https://github.com/zestsoftware/zest.releaser/issues/391>`_.

- The ``longtest`` is now simpler. It runs readme_renderer and just displays
  the result in the browser, without error handling. ``twine check`` should be
  used if you want a real hard check (``longtest --headless`` is
  deprecated). The advantage is that longtest now also renders markdown
  correctly.  This adds `readme_renderer[md]` as dependency.
  Fixes `issue 363 <https://github.com/zestsoftware/zest.releaser/issues/363>`_.


9.0.0a1 (2023-07-13)
--------------------

- Changed build system to pypa/build instead of explicitly using
  setuptools.

- Zest.releaser's settings can now also be placed in ``pyproject.toml``.

- Use native namespace packages for ``zest.releaser``, instead of
  deprecated ``pkg_resources`` based ones.

- Added pre-commit config for neater code (black, flake8, isort).

- Dropped support for python 3.7. Together with switching to ``build`` and
  ``pyproject.toml``, this warrants a major version bump.


8.0.0 (2023-05-05)
------------------

- Make final release, no changes since latest alpha.  [maurits]


8.0.0a2 (2023-04-06)
--------------------

- Always create wheels, except when you explicitly switch this off in the config:
  ``[zest.releaser] create-wheel = no``.
  If the ``wheel`` package is not available, we still do not create wheels.
  Fixes `issue 406 <https://github.com/zestsoftware/zest.releaser/issues/406>`_.
  [maurits]

- Do not fail when tag versions cannot be parsed.
  This can happen in ``lasttaglog``, ``lasttagdiff``, and ``bumpversion``, with ``setuptools`` 66 or higher.
  Fixes `issue 408 <https://github.com/zestsoftware/zest.releaser/issues/408>`_.
  [maurits]


8.0.0a1 (2023-02-08)
--------------------

- Drop support for Python 3.6.  [maurits]

- Support reading and writing the version in ``pyproject.toml``.
  See `issue 295 <https://github.com/zestsoftware/zest.releaser/issues/295>`_,
  `issue 373 <https://github.com/zestsoftware/zest.releaser/issues/373>`_,
  and `PEP-621 <https://peps.python.org/pep-0621/>`_,
  [maurits]


7.3.0 (2023-02-07)
------------------

- Add option ``run-pre-commit = yes / no``.
  Default: no.
  When set to true, pre commit hooks are run.
  This may interfere with releasing when they fail.
  [maurits]


7.2.0 (2022-12-09)
------------------

- Auto-detect ``history_format`` based on history filename.
  [ericof]

- Add ``history_format`` option, to explicitly set changelogs
  entries in Markdown.
  [ericof]


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
