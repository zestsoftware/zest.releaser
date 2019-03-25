Changelog for zest.releaser
===========================

6.17.2 (2019-03-25)
-------------------

- When ``bdist_wheel`` is in ``setup.cfg``, release a wheel.
  No longer check if this should be a universal wheel or not.
  That is handled automatically when calling ``python setup.py bdist_wheel``.
  You can still set ``[zest.releaser] create-wheel = no`` to prevent creating a wheel.
  Fixes `issue 315 <https://github.com/zestsoftware/zest.releaser/issues/315>`_.
  [maurits]


6.17.1 (2019-03-19)
-------------------

- Also accept 201 as valid statuscode when uploading using twine
  Fixes `issue 318 <https://github.com/zestsoftware/zest.releaser/issues/318>`_
  [fRiSi]


6.17.0 (2019-02-20)
-------------------

- Refuse to edit history header when it looks to be from an already released version.
  We look for a date in it (like 2019-02-20).  Give a warning when this happens.
  Fixes `issue 311 <https://github.com/zestsoftware/zest.releaser/issues/311>`_.
  [maurits]

- Better support for ``zestreleaser.towncrier`` (and similar extensions):
  the update_history setting is now also respected by the ``bumpversion`` command.
  Fixes `issue 310 <https://github.com/zestsoftware/zest.releaser/issues/310>`_.
  [maurits]


6.16.0 (2019-01-17)
-------------------

- Fix for `issue #259 <https://github.com/zestsoftware/zest.releaser/issues/259>`_:
  using zest.releaser on windows no longer can result in accidental extra
  ``\r`` (carriage return) characters in the changelog and your ``setup.py``.
  [reinout]


6.15.4 (2019-01-11)
-------------------

- We retain the existing quoting style for the ``version='1.0'`` in
  ``setup.py`` files. The "black" code formatting prefers double quotes and
  zest.releaser by default wrote single quotes.
  [reinout]

- Fix for `issue #299 <https://github.com/zestsoftware/zest.releaser/issues/299>`_:
  bumpversion now also compares versions numerically instead of as a string,
  so ``2.9 < 2.10`` is now true.
  [reinout]


6.15.3 (2018-12-03)
-------------------

- Fix for `issue #297 <https://github.com/zestsoftware/zest.releaser/issues/297>`_:
  bytes+int problem on python 3 when detecting encodings.
  [reinout]


6.15.2 (2018-08-30)
-------------------

- If a tag already exists, zest.releaser asks a safety question. The location
  where the question gets asked was moved slightly to help a program that uses
  zest.releaser as a library.
  [reinout]

- Switched our readthedocs urls to https.
  [reinout]


6.15.1 (2018-06-22)
-------------------

- Fix for #286: removed the confusing word "register" from the info message
  you got when a package wasn't available yet on pypi.

  Registering isn't used anymore on pypi, but it was still in our textual
  message.
  [reinout]


6.15.0 (2018-05-15)
-------------------

- Use pypi.org, especially when checking if a package is on PyPI.
  Fixes `issue #281 <https://github.com/zestsoftware/zest.releaser/issues/281>`_.
  [maurits]

- Added key ``update_history`` in prerelease and postrelease data.
  Plugins can use this to tell ``zest.releaser`` (and other plugins)
  to not touch the history, presumably because the plugin handles it.
  [maurits]

- Declared ``requests`` dependency.
  Declared ``zope.testing`` test dependency.
  [maurits]


6.14.0 (2018-03-26)
-------------------

- Advertise ``setup.cfg`` option ``[zest.releaser] history-file``.
  Usually zest.releaser can find the correct history or changelog file on its own.
  But sometimes it may not find anything, or it finds multiple files and
  selects the wrong one.
  Then you can set a path here.
  A ``history_file`` option with an underscore was already read, but not documented.
  Now we try both a dash and an underscore for good measure.
  [maurits]

- Use new ``setup.cfg`` option ``[zest.releaser] encoding``.
  Set this to, for example, ``utf-8`` when the encoding of your ``CHANGES.rst``
  file is not determined correctly.
  Fixes `issue 264 <https://github.com/zestsoftware/zest.releaser/issues/264>`_.
  [maurits]

- When inserting changelog entry, check that it conforms to the existing encoding.
  Try to recover if there is a difference, especially when the changelog file
  was ascii and we insert utf-8.  [maurits]

- When determining encoding, first look for coding hints in the file itself.
  Only when that fails, we try ``tokenize`` or ``chardet``.
  Fixes `issue 264 <https://github.com/zestsoftware/zest.releaser/issues/264>`_.
  [maurits]

- Get PyPI password raw, without interpolation.
  If you had a password with a percentage sign, you could get an error.
  Fixes `issue 271 <https://github.com/zestsoftware/zest.releaser/issues/271>`_.
  [maurits]

- Prevent unclosed files.  Python 3.6 warned about them,
  and PyPy may have more problems with it.
  Fixed several other DeprecationWarnings.  [maurits]

- Print commands in a nicer way.
  You could get ugly output like this, especially on Python 2.7:
  ``INFO: The '[u'git', u'diff']':`` or worse:
  ``Command failed: u"t w i n e ' ' u p l o a d"``.
  [maurits]

- Test compatibility with Python 2.7, 3.4, 3.5, 3.6, PyPy2.  [maurits]


6.13.5 (2018-02-16)
-------------------

- Quit in ``postrelease`` when we cannot find a version.
  Fixes `issue #262 <https://github.com/zestsoftware/zest.releaser/issues/262>`.
  [maurits]


6.13.4 (2018-02-05)
-------------------

- Fixed IOError when ``setup.cfg`` is missing and no version is found.
  [maurits]


6.13.3 (2017-12-19)
-------------------

- Fixed writing of files in original encoding on python3, too. [andreparames]


6.13.2 (2017-11-27)
-------------------

- Fixed tests with mercurial 4.4+.  [maurits]

- Fixed writing of files in original encoding. [mgedmin]


6.13.1 (2017-11-13)
-------------------

- Add tag message formatting (option ``tag-message``). [htgoebel]


6.13.0 (2017-11-10)
-------------------

- Add support for signing tags (option ``tag-signing``). [htgoebel]


6.12.5 (2017-09-25)
-------------------

- Sorting uploadable filenames so that wheels are uploaded first. (For most
  filesystems this happened automatically, but the order on OSX' new
  filesystem is non-deterministic, so we added sorting.)
  [reinout]

- Release process will now fail when specified hooks cannot be imported.
  (`PR #236 <https://github.com/zestsoftware/zest.releaser/pulls/236>`_)


6.12.4 (2017-08-30)
-------------------

- Also support version in setup.cfg. [ewjoachim]


6.12.3 (2017-08-16)
-------------------

- Allows ``{version}`` format for ``tag-format``.
  [leorochael]


6.12.2 (2017-07-13)
-------------------

- Subversion fix: create tag of entire trunk or branch when not in repo root.
  If you have ``trunk/pkg1`` and ``trunk/pkg2`` and you make tag 1.0 in directory ``pkg1``,
  then until now we would create ``tags/1.0`` with the contents of directory ``pkg1``.
  Checking out the tag and changing to the ``pkg1`` directory then failed.
  We now make a tag of the entire trunk or branch, just like in the other version control systems.
  Fixes `issue #213 <https://github.com/zestsoftware/zest.releaser/issues/213>`_.
  [maurits]

- Do not needlessly run ``svn info``.  [maurits]


6.12.1 (2017-07-03)
-------------------

- Quote the path when making a git clone, to fix problems with spaces.  [halkeye]

- Fixed percentage signs in ``date-format`` in ``setup.cfg``.
  You need double percentages.  [mgedmin]


6.12 (2017-06-19)
-----------------

- Add date format in the config.  Default is ISO-8601 (%Y-%m-%d).
  Put ``date-format = format string`` in your ``~/.pypirc`` or ``setup.cfg``.
  [mgedmin]


6.11 (2017-06-09)
-----------------

- If the package wants to build universal wheels by setting
  ``[bdist_wheel] universal = 1``, then the default for
  ``create-wheel`` is now yes.


6.10 (2017-04-18)
-----------------

- Corner case fix: a top-level ``version = 1.0`` in your ``setup.py`` is now
  also allowed to be in uppercase, like ``VERSION = 1.0``.
  This fixes `issue 216
  <https://github.com/zestsoftware/zest.releaser/issues/216>`_.
  [reinout]


6.9 (2017-02-17)
----------------

- Add tag formatter in the config.  This is a formatter that changes the name of the tag.
  Default is the same as the version.
  Put ``tag-format = a string`` in your ``~/.pypirc`` or ``setup.cfg``.
  It needs to contain ``%(version)s``.
  [tcezard]


6.8.1 (2017-01-13)
------------------

- Catch error when uploading first package file in new PyPI project.
  This fixes `issue 206
  <https://github.com/zestsoftware/zest.releaser/issues/206>`_.
  [maurits]


6.8 (2016-12-30)
----------------

- Before retrying a ``twine`` command, reload the pypi config.  Then
  when the user fixes his account settings in ``~/.pypirc`` and
  retries, these changes take effect.  This used to work a while ago,
  but got broken.  [maurits]

- Added ``development-marker`` config option.  With this can override
  the default ``.dev0``.  [drucci]

- Added ``version-levels`` and ``less-zeroes`` options.
  This influences the suggested version.  [maurits]

- Allow ``.pypirc`` with just a ``pypi`` section.  Previously, we
  required either a ``[server-login]`` section with a ``username``
  option, or a ``[distutils]`` section with an ``index-servers`` option.
  Failing this, we gave a warning about a not properly configured
  file, and happily continued without uploading anything.  Now if
  there is something missing from the ``pypirc`` file, we give an
  error and explicitly ask if you want to continue without uploading.
  Fixes `issue #199 <https://github.com/zestsoftware/zest.releaser/issues/199>`_.

  Note for developers of extensions for ``zest.releaser``: this
  removes the ``is_old_pypi_config`` and ``is_new_pypi_config``
  methods, because they made no sense anymore.  If you were using
  these, see if you can use the ``distutils_server`` method instead.
  [maurits]

- Added ``push-changes`` config file option.  Default: yes.  When this
  is false, zest.releaser sets ``no`` as default answer for the
  question if you want to push the changes to the remote.
  [newlog]

- By default no longer register a new package, but only upload it.
  Registering a package is no longer needed on PyPI: uploading a new
  distribution takes care of this.  If you *do* want to register,
  maybe because a different package server requires it, then in your
  ``setup.cfg`` or ``~/.pypirc``, use the following::

    [zest.releaser]
    register = yes

  Fixes `issue 191 <https://github.com/zestsoftware/zest.releaser/issues/191>`_.
  [willowmck]


6.7.1 (2016-12-22)
------------------

- Create the list of distributions after the ``before_upload`` hook has fired.
  This allows the ``before_upload`` hook to create additional distributions,
  which will then be uploaded.  [t-8ch]


6.7 (2016-10-23)
----------------

- Use the intended API of twine.  This should work with twine 1.6.0
  and higher, including future versions.  [maurits]


6.6.5 (2016-09-12)
------------------

- Support and require twine 1.8.0 as minimum version.
  Fixes https://github.com/zestsoftware/zest.releaser/issues/183
  [maurits]

- Updated the documentation on uploading.  [mgedmin, maurits]

- Replaced http://zestreleaser.readthedocs.org with
  https://zestreleaser.readthedocs.io.  This is the new canonical
  domain since 28 April 2016.  [maurits]


6.6.4 (2016-02-24)
------------------

- Really create a shallow git clone when creating a distribution.
  See issue #169.
  [maurits]


6.6.3 (2016-02-24)
------------------

- Using a "shallow" git clone when creating a distribution. This speeds up
  releases, especially on big repositories.
  See issue #169.
  [gforcada]


6.6.2 (2016-02-11)
------------------

- Added ``no-input`` option also to global (.pypirc) options.
  Issue #164.
  [jcerjak]


6.6.1 (2016-02-02)
------------------

- Fixed version in changelog after bumpversion call.
  [maurits]


6.6.0 (2016-01-29)
------------------

- Added ``bumpversion`` command.  Options ``--feature`` and
  ``--breaking``.  Issue #160.  The exact behavior might change in
  future versions after more practical experience.  Try it out and
  report any issues you find.  [maurits]

- Fixed possible encoding problems when writing files.  This is
  especially for an ascii file to which we add non ascii characters,
  like in the ``addchangelogentry`` command.  [maurits]

- Added ``addchangelogentry`` command.  Issue #159.  [maurits]

- Moved ``_diff_and_commit``, ``_push`` and ``_grab_version`` to
  ``baserelease.py``, as the first was duplicated and the second and
  third may be handy for other code too.  ``_grab_version`` is the
  basic implementation, and is overridden in the prereleaser.  [maurits]

- Show changelog of current release before asking for the new version
  number.  Issue #155.  [maurits]

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

.. _twine: https://pypi.org/project/twine
