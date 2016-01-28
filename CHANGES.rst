Changelog for zest.releaser
===========================

6.6 (unreleased)
----------------

- Moved ``_diff_and_commit``, ``_push`` and ``_grab_version`` to
  ``baserelease.py``, as the first was duplicated and the second and
  third may be handy for other code too.  ``_grab_version`` is the
  basic implementation, and is overridden in the prereleaser.  [maurits]


6.5 (2016-01-05)
----------------

- Adjusted ``bin/longtest`` for the (necessary) rename of the ``readme``
  library to ``readme_renderer``.
  Fixes #153

  Note: the current ``readme`` package on pypi is broken to force an
  upgrade. If you use an older zest.releaser, you have to pin ``readme`` to
  ``0.6.0``, it works just fine.
  [reinout]


6.4 (2015-11-13)
----------------

- Fixed error when retrying twine command.
  Fixes #148
  [maurits]


6.3 (2015-11-11)
----------------

- Fixed exception when logging an exception when a twine command
  fails.
  [maurits]


6.2 (2015-10-29)
----------------

New:

- Use ``twine`` as library instead of as command.  You no longer need
  to have ``twine`` on your ``PATH``.
  Fixes issue #142.
  [maurits]


6.1 (2015-10-29)
----------------

Fixes:

- Fixed registering on servers other than PyPI.  We forgot to specify
  the server in that case.
  [maurits]


6.0 (2015-10-27)
----------------

- Made ``twine`` a core dependency.  We now always use it for
  registering and uploading.  We require at least version 1.6.0, as
  this introduces the ``register`` command.
  [maurits]

- When uploading with ``twine`` first use the ``twine register``
  command.  On PyPI, when the project is already registered, we do not
  call it again, but we can only check this for PyPI, not for other
  servers.
  Issue #128.
  [maurits]

- Always exit with error code 1 when we exit explicitly.  In some
  cases we would exit with success code 0 when we exited based on the
  answer to a question.  This happened when the user did not want us
  to create the missing ``tags`` directory in subversion, and also
  after asking if the user wanted to continue even though 'nothing
  changed yet' was in the history.
  [maurits]

- Extensions can now tell zest.releaser to look for specific required
  words in the history.  Just add ``required_changelog_text`` to the
  prerelease data.  It can be a string or a list, for example
  ``["New:", "Fixes:"]``.  For a list, only one of them needs to be
  present.
  [maurits]

- Look for the 'Nothing changed yet' text in the complete text of the
  history entries of the current release, instead of looking at it
  line by line.  This means that zest releaser extensions can overwrite
  ``nothing_changed_yet`` in the prerelease data to span multiple lines.
  [maurits]

- zest.releaser extensions can now look at
  ``history_insert_line_here`` in the prerelease data.  On this line
  number in the history file they can add an extra changelog entry if
  wanted.
  [maurits]

- Added ``history_last_release`` to the prerelease data.  This is the
  text with all history entries of the current release.
  [maurits]

- When using the ``--no-input`` option, show the question and the
  chosen answer.  Otherwise in case of a problem it is not clear why
  the command stopped.
  Fixes issue #136.
  [maurits]


5.7 (2015-10-14)
----------------

- The history/changelog file is now written back with the originally detected
  encoding. The functionality was added in 5.2, but only used for writing the
  ``setup.py``, not the changelog. This is fixed now.
  [reinout]


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

.. # Note: for older changes see ``doc/sources/changelog.rst``.

.. _twine: https://pypi.python.org/pypi/twine
