Changelog for zest.releaser
===========================

5.6 (2015-09-23)
----------------

- Add support for PyPy.
  [jamadden]


5.5 (2015-09-05)
----------------

- The ``bin/longtest`` command adds the correct utf-8 character encoding hint
  to the resulting html so that non-ascii long descriptions are properly
  rendered in all browsers.
  [reinout]


5.4 (2015-08-28)
----------------

- Requiring at least version 0.6 of the (optional, btw) readme package. The
  API of readme changed slightly. Only needed when you want to check your
  package's long description with ``bin/longtest``.
  [reinout]


5.3 (2015-08-21)
----------------

- Fixed typo in svn command to show the changelog since the last tag.
  [awello]


5.2 (2015-07-27)
----------------

- When we find no version control in the current directory, look a few
  directories up.  When looking for version and history files, we look
  in the current directory and its sub directories, and not in the
  repository root.  After making a tag checkout, we change directory
  to the same relative path that we were in before.  You can use this
  when you want to release a Python package that is in a sub directory
  of the repository.  When we detect this, we first offer to change to
  the root directory of the repository.
  [maurits]

- Write file with the same encoding that we used for reading them.
  Issue #109.
  [maurits]


5.1 (2015-06-11)
----------------

- Fix writing history/changelog file with non-ascii.  Issue #109.
  [maurits]

- Release zest.releaser as universal wheel, so one wheel for Python 2
  and 3.  As usual, we release it also as a source distribution.
  [maurits]

- Regard "Skipping installation of __init__.py (namespace package)" as
  warning, printing it in magenta.  This can happen when creating a
  wheel.  Issue #108.
  [maurits]


5.0 (2015-06-05)
----------------

- Python 3 support.
  [mitchellrj]

- Use the same `readme` library that PyPI uses to parse long
  descriptions when we test and render them.
  [mitchellrj]


4.0 (2015-05-21)
----------------

- Try not to treat warnings as errors.
  [maurits]

- Allow retrying some commands when there is an error.  Currently only
  for commands that talk to PyPI or another package index.  We ask the
  user if she wants to retry: Yes, no, quit.
  [maurits]

- Added support for twine_.  If the ``twine`` command is available, it
  is used for uploading to PyPI.  It is installed automatically if you
  use the ``zest.releaser[recommended]`` extra.  Note that if the
  ``twine`` command is not available, you may need to change your
  system ``PATH`` or need to install ``twine`` explicitly.  This seems
  more needed when using ``zc.buildout`` than when using ``pip``.
  Added ``releaser.before_upload`` entry point.  Issue #59.
  [maurits]

- Added ``check-manifest`` and ``pyroma`` to the ``recommended``
  extra.  Issue #49.
  [maurits]

- Python 2.6 not officially supported anymore.  It may still work, but
  we are no longer testing against it.
  [maurits]

- Do not accept ``y`` or ``n`` as answer for a new version.
  [maurits]

- Use ``colorama`` to output errors in red.
  Issue #86
  [maurits]

- Show errors when uploading to PyPI.  They were unintentionally
  swallowed before, so you did not notice when an upload failed.
  Issue #84.
  [maurits]

- Warn when between the last postrelease and a new prerelease no
  changelog entry has been added.  '- Nothing changed yet' would still
  be in there.
  Issue #26.
  [maurits]

- Remove code for support of collective.sdist.  That package was a backport
  from distutils for Python 2.5 and earlier, which we do not support.
  [maurits]

- Add optional support for uploading Python wheels.  Use the new
  ``zest.releaser[recommended]`` extra, or run ``pip install wheel``
  yourself next to ``zest.releaser``.  Create or edit ``setup.cfg`` in
  your project (or globally in your ``~/.pypirc``) and create a section
  ``[zest.releaser]`` with ``create-wheel = yes`` to create a wheel to
  upload to PyPI.  See http://pythonwheels.com for deciding whether
  this is a good idea for your package.  Briefly, if it is a pure
  Python 2 *or* pure Python 3 package: just do it.
  Issue #55
  [maurits]

- Optionally add extra text to commit messages.  This can be used to
  avoid running Travis Continuous Integration builds.  See
  http://docs.travis-ci.com/user/how-to-skip-a-build/.  To activate
  this, add ``extra-message = [ci skip]`` to a ``[zest.releaser]``
  section in the ``setup.cfg`` of your package, or your global
  ``~/.pypirc``.  Or add your favorite geeky quotes there.
  [maurits]

- Fix a random test failure on Travis CI, by resetting ``AUTO_RESPONSE``.
  [maurits]

- Added clarification to logging: making an sdist/wheel now says that it is
  being created in a temp folder. Fixes #61.
  [reinout]


3.56 (2015-03-18)
-----------------

- No need anymore to force .zip for sdist.
  Issue #76
  [reinout]

- Still read ``setup.cfg`` even if ``~/.pypirc`` is wrong or missing.
  Issue #74
  [tomviner]


3.55 (2015-02-03)
-----------------

- Experimental work to ignore setuptools' stderr output. This might help with
  some of the version warnings, which can break zest.releaser's output
  parsing. [reinout]

- Fix for #72. Grabbing the version from the ``setup.py`` on windows can fail
  with an "Invalid Signature" error because setuptools cannot find the
  crypto dll. Fixed by making sure setuptools gets the full ``os.environ``
  including the ``SYSTEMROOT`` variable. [codewarrior0]


3.54 (2014-12-29)
-----------------

- Blacklisting ``debian/changelog`` when searching for changelog-like
  filenames as it gets picked in favour of ``docs/changelog.rst``. The
  debian one is by definition unreadable for us.


3.53.2 (2014-11-21)
-------------------

- Additional fix to 3.53: ``version.rst`` (and .md) also needed to be looked
  up in a second spot.


3.53 (2014-11-10)
-----------------

- Also allowing .md extension in addition to .rst/.txt/.markdown for
  ``CHANGES.txt``.
  [reinout]

- Similarly, ``version.txt`` (if you use that for non-setup.py-projects) can
  now be ``version.rst`` or .md/.markdown, too.
  [reinout]


3.52 (2014-07-17)
-----------------

- Fixed "longtest" command when run with a python without setuptools
  installed. Similar fix to the one in 3.51.
  See https://github.com/zestsoftware/zest.releaser/issues/57
  [reinout]


3.51 (2014-07-17)
-----------------

- When calling ``python setup.py`` use the same PYTHONPATH environment
  as the script has.
  https://github.com/zestsoftware/zest.releaser/issues/24
  [maurits]


3.50 (2014-01-16)
-----------------

- Changed command "hg manifest" to "hg locate" to list files in Mercurial.
  The former prints out file permissions along with the file name, causing a bug.
  [rafaelbco]


3.49 (2013-12-06)
-----------------

- Support git-svn checkouts with the default "origin/" prefix.
  [kuno]


3.48 (2013-11-26)
-----------------

- When using git, checkout submodules.
  [dnozay]


3.47 (2013-09-25)
-----------------

- Always create an egg (``sdist``), even when there is no proper pypi
  configuration file.  This helps plugins that use our entry points.
  Fixes https://github.com/zestsoftware/zest.releaser/issues/45
  [maurits]


3.46 (2013-06-28)
-----------------

- Support actually updating ``VERSION`` as well.
  Issue #43.


3.45 (2013-04-17)
-----------------

- Supporting ``VERSION`` (without extension) in addition to the
  old-zope-products-``VERSION.txt`` files.


3.44 (2013-03-21)
-----------------

- Added optional ``python-file-with-version`` setting for the
  ``[zest.releaser]`` section in ``setup.cfg``. If set, zest.releaser extracts
  the version from that file's ``__version__`` attribute. (See `PEP 396
  <http://www.python.org/dev/peps/pep-0396/>`_).

- File writes now use the platform's default line endings instead of always
  writing ``\n`` unix style line endings. (Technically, we write using ``w``
  instead of ``wb`` mode).

- Added link to other documentation sources in the sphinx docs.

- Noting in our pypi classifiers that we support python 2.6+, not python
  2.4/2.5. Slowly things will creep into zest.releaser's code that break
  compatibility with those old versions. And we want to get it to work on
  python 3 and that's easier with just 2.6/2.7 support.


3.43 (2013-02-04)
-----------------

- Added ``--no-input`` commandline option for running automatically without
  asking for input. Useful when started from some build tool. See the
  documentation at the end of
  http://zestreleaser.readthedocs.org/en/latest/uploading.html .
  [reinout, based upon a patch by j-san]


3.42 (2013-01-07)
-----------------

- When finding multiple version, changes or history files, pick the
  one with the shortest path.
  [maurits]

- Support project-specific hooks listed in setup.cfg.
  [iguananaut]


3.41 (2012-11-02)
-----------------

- Getting the version from setup.py can give a traceback if the
  setup.py has an error.  During prerelease this would result in a
  proposed version of 'Traceback'.  Now we print the traceback and
  quit.
  [maurits]


3.40 (2012-10-13)
-----------------

- Support svn (1.7+) checkouts that are not directly in the root. Only applies
  when someone checks out a whole tree and wants to release one of the items
  in a subdirectory. Fixes #27.


3.39 (2012-09-26)
-----------------

- Only search for files in version control.  This is when finding a
  history file or version.txt file.  We should not edit files that
  are not in our package.  Fixes issue #22.
  [maurits]


3.38 (2012-09-25)
-----------------

- Fixed svn tag extraction on windows: a ``\r`` could end up at the
  end of every tag name. Thanks Wouter Vanden Hove for reporting it!

- Small fixes to the developers documentation and to the automatic
  `travis CI <http://travis-ci.org/#!/zestsoftware/zest.releaser/>`_
  tests configuration.


3.37 (2012-07-14)
-----------------

- Documentation update! Started sphinx documentation at
  `zestreleaser.readthedocs.org <http://zestreleaser.readthedocs.org>`_.
  Removed documentation from the README and put it into sphinx.

- Actually ask if the user wants to continue with the release when
  there is no MANIFEST.in.  We asked for a yes/no answer, but the
  question was missing.
  [maurits]


3.36 (2012-06-26)
-----------------

- Improved changes/history file detection and fixed the documentation at this
  point. We now recognize CHANGES, HISTORY and CHANGELOG with .rst, .txt,
  .markdown and with no extension.

- Set up `travis CI <http://travis-ci.org/#!/zestsoftware/zest.releaser/>`_
  integration. Our tests pass on python 2.5, 2.6 and 2.7.


3.35 (2012-06-21)
-----------------

- When checking for recommended files, ask if the user wants to
  continue when we suspect the created PyPI release may be broken.
  See issue #10.
  [maurits]

- Preserve existing EOL in setup.py and history file (See
  http://docs.python.org/tutorial/inputoutput.html#reading-and-writing-files)
  [tom_gross]


3.34 (2012-03-20)
-----------------

- In the warning about a missing MANIFEST.in file, also suggest to
  install setuptools_subversion/git, etc.
  Fixes issue #4.
  [maurits]


3.33 (2012-03-20)
-----------------

- Fix python 2.4 issues with tarfile by always creating a zip file.
  Formerly we would only do this when using python2.4 for doing the
  release, but a tarball sdist created by python2.6 could still break
  when the end user is using python 2.4.
  [kiorky]


3.32 (2012-03-09)
-----------------

- In prerelease recommend the user to add a MANIFEST.in file.
  See http://docs.python.org/distutils/sourcedist.html for
  more info.
  [maurits]


3.31 (2012-02-23)
-----------------

- Fixed test for unadvised egg_info commands on tag, which could
  result in a ConfigParser error.
  [maurits]


3.30 (2011-12-27)
-----------------

- Added some more PyPI classifiers.  Tested with Python 2.4, 2,4, 2.6,
  and 2.7.
  [maurits]

- Moved changes of 3.15 and older to docs/HISTORY.txt.
  [maurits]

- Added GPL license text in the package.
  [maurits]

- Updated README.txt.  Added MANIFEST.in.
  [maurits]


3.29 (2011-12-27)
-----------------

- In postrelease create a version number like 1.0.dev0.
  See http://www.python.org/dev/peps/pep-0386
  [maurits]

- Offer to cleanup setup.cfg on the tag when releasing.  You do not
  want tag_build or tag_svn_revision options in a release usually.
  [maurits]

- For convenience also print the tag checkout location when only doing
  a release (instead of a fullrelease).
  [maurits]


3.28 (2011-11-18)
-----------------

- Git: in pre/postrelease only check for uncommitted changes in files
  that are already tracked.
  [maurits]


3.27 (2011-11-12)
-----------------

- Postrelease now offers (=asks) to push your changes to the server if you're
  using hg or git.

- Support for some legacy projects, often converted from CVS, have multiple
  subprojects under a single trunk. The trunk part from the top level project
  isn't erroneously stripped out anymore. Thanks to Marc Sibson for the fix.


3.26 (2011-11-01)
-----------------

- Added sanity check before doing a prerelease so you are warned when
  you are about to commit on a tag instead of a branch (or trunk or
  master).
  [maurits]


3.25 (2011-10-28)
-----------------

- Removed special handling of subversion lower than 1.7 when searching
  for the history/changes file.  In corner cases it may be that we
  find a wrong HISTORY.txt or CHANGES.txt file when you have it buried
  deep in your directory structure.  Please move it to the root then,
  which is the proper place for it.
  [maurits]

- Fixed finding a history/changes file that is in a sub directory when
  using subversion 1.7 or higher or bazaar.
  [maurits]


3.24 (2011-10-19)
-----------------

- Note: you may need to install setuptools_subversion when you use
  subversion 1.7.  If you suddenly start missing files in the sdists
  you upload to PyPI you definitely need it.  Alternatively: set up a
  proper MANIFEST.in as that method works with any version control
  system.
  [maurits]

- Made compatible with subversion 1.7 (the only relevant change is in
  the code that checks if a tags or tag directory already exists).
  Earlier versions of subversion are of course still supported.
  [maurits]

- Code repository moved to github:
  https://github.com/zestsoftware/zest.releaser
  [maurits]


3.23 (2011-09-28)
-----------------

- Fixed opening the html long description in ``longtest`` on Mac OS X
  Lion or python2.7 by using a ``file://`` url.
  Fixes https://bugs.launchpad.net/zest.releaser/+bug/858011
  [maurits]

.. # Note: for older changes see ``doc/sources/changelog.rst``.

.. _twine: https://pypi.python.org/pypi/twine
