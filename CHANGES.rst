Changelog for zest.releaser
===========================

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

- Small fixes to the developers documentation and to the automatic `travis CI
  <http://travis-ci.org/#!/zestsoftware/zest.releaser/>`_ tests configuration.


3.37 (2012-07-14)
-----------------

- Documentation update! Started sphinx documentation at
  `zestreleaser.readthedocs.org
  <http://zestreleaser.readthedocs.org>`_. Removed documentation from the
  README and put it into sphinx.

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
