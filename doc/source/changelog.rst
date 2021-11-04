.. include:: ../../CHANGES.rst

.. # Note: CHANGES.rst is the current changelog, the older entries are in here.

6.22.2 (2021-10-29)
-------------------

- Migrate to `travis-ci.com <https://travis-ci.com/github/zestsoftware/zest.releaser>`_.
  [maurits]


6.22.1 (2020-09-22)
-------------------

- When replacing new version in ``__version__ = "1.0"``, keep the existing quote style.
  We always replaced double with single quotes, but now we keep them.
  [graingert]


6.22.0 (2020-09-03)
-------------------

- Fixed deadlock when communicating with git-lfs, or anything else that gives back lots of output.
  [mcdeck]

- Fixed TypeError setting unicode in environment on Python 2.7 on Windows.
  [mcdeck]


6.21.1 (2020-08-07)
-------------------

- Fixed uploading to multiple servers if we do not want to upload to the first server.
  Fixes `issue #357 <https://github.com/zestsoftware/zest.releaser/issues/357>`_.
  [maurits]


6.21.0 (2020-07-01)
-------------------

- Added support for Twine environment variables.
  Especially, setting ``TWINE_REPOSITORY`` and ``TWINE_REPOSITORY_URL`` had no effect previously.
  Fixes `issue #353 <https://github.com/zestsoftware/zest.releaser/issues/353>`_.
  [mctwynne]


6.20.1 (2020-02-21)
-------------------

- Added ``Dockerfile`` for much easier testing. See `the developer
  documentation
  <https://zestreleaser.readthedocs.io/en/latest/developing.html>`_. Previously,
  getting the tests to run reliably locally was hard, now it is easy.
  [Behoston]


6.20.0 (2020-01-07)
-------------------

- Zest.releaser now sets an environment variable ``ZESTRELEASER`` so that
  tools that we call on the command line can detect us. Don't depend on the
  variable's textual content, just on the variable's name.


6.19.1 (2019-09-03)
-------------------

- Percent signs (%) don't crash addchangelogentry anymore.


6.19.0 (2019-06-03)
-------------------

- Do not go to the root of the repo by default.
  When you were not in the root of a repo, ``zest.releaser`` already asked if you wanted to go there.
  The default answer has now changed from yes to no.
  This might help when releasing from monorepos.
  Issue `#326 <https://github.com/zestsoftware/zest.releaser/issues/326>`_.  [maurits]


6.18.2 (2019-04-10)
-------------------

- Remove nothing_changed_yet line from history lines in unreleased section. [kleschenko]


6.18.1 (2019-04-04)
-------------------

- Document that we only support underline-style headings for markdown.
  Fixes `issue 317 <https://github.com/zestsoftware/zest.releaser/issues/317>`_.
  [reinout]

- Using simply ``git ls-files`` to list files in a git repo instead of an
  older much longer command. (Suggestion by @mgedmin).
  [reinout]


6.18.0 (2019-04-03)
-------------------

- Calling twine in a more generic way to let it automatically do the right
  thing. This saves us a lot of code and lets twine do what it's good at.
  [htgoebel,reinout]


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

.. _twine: https://pypi.org/project/twine


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
  https://zestreleaser.readthedocs.io/en/latest/uploading.html .
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
  `zestreleaser.readthedocs.io <https://zestreleaser.readthedocs.io>`_.
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


3.22 (2011-05-05)
-----------------

- Allow specifying a tag on the command line when using lasttaglog or
  lasttagdiff, to show the log or diff since that tag instead of the
  latest.  Useful when you are on a branch and the last tag was from
  trunk.
  [maurits]


3.21 (2011-04-20)
-----------------

- Added lasttaglog command that list the log since the last tag.
  [maurits]

- Fix Mercurial (hg) support. As spreaded_internal should be set
  to False (as it happens with git)
  [erico_andrei]

- Accept a twiggle (or whatever '~' is called) when searching for
  headers in a changelog; seen in some packages (at least
  zopeskel.dexterity).
  [maurits]


3.20 (2011-01-25)
-----------------

- Also allowing CHANGES.rst and CHANGES.markdown in addition to
  CHANGES.txt.


3.19 (2011-01-24)
-----------------

- No longer refuse to register and upload a package on pypi if it is
  not there yet, forcing people to do this manually the first time.
  Instead, we ask the question and simply have 'No' as the default
  answer.  If you specify an answer, we require exactly typing 'yes'
  or 'no'.  The idea is still to avoid making it too easy to release
  an internal package on pypi by accident.  [maurits]


3.18 (2010-12-08)
-----------------

- Added ``--non-interactive--`` option to the ``svn diff`` command used in
  lasttagdiff.  This makes it usable in cronjobs and post-commit hooks.
  Fixes https://bugs.launchpad.net/zest.releaser/+bug/687530


3.17 (2010-11-17)
-----------------

- When the package that is being released neither has a setup.py nor a
  setup.cfg, use No as default answer for creating a checkout of the
  tag.
  [maurits]


3.16 (2010-11-15)
-----------------

- For (pypi) output, also show the first few lines instead of only the
  last few.
  [maurits]

- See if pypirc or setup.cfg has a [zest.releaser] section with option
  release = yes/no.  During the release stage, this influences the
  default answer when asked if you want to make a checkout of the tag.
  The default when not set, is 'yes'.  You may want to set this to
  'no' if most of the time you only make releaser of internal packages
  for customers and only need the tag.
  [maurits]

- Specify bazaar (bzr) tag numbers using the 'tag' revision specifier
  (like 'tag:0.1') instead of only the tag number (0.1) to add
  compatibility with earlier bzr versions (tested with 2.0.2).
  [maurits]


3.15 (2010-09-10)
-----------------

- Read pypi config not only from the .pypirc file, but also from the
  setup.cfg file of the package.  Patch by Erico Andrei.
  [maurits]


3.14 (2010-08-26)
-----------------

- experimental support for git svn tagging, fully test-covered
  [chaoflow]

- fail if no tag was created, not test-covered
  [chaoflow]

- svn available_tags method: intercept 'Repository moved' note in svn
  info and stop processing then.
  [maurits]


3.13 (2010-08-16)
-----------------

- Fixed check that tested whether a package was already available on
  pypi, as the pypi implementation changed slightly.  We now just
  check for a 404 status.  Patch by Wolfgang Schnerring.
  [maurits]


3.12 (2010-07-22)
-----------------

- Added extra entry point for the release step: ``after_checkout``.
  When this is run, the middle entry point has been handled, the tag
  has been made, a checkout of that tag has been made and we are now
  in that checkout directory.  Idea: Jan-Wijbrand Kolman.
  [maurits]

- Fix: in the zest.releaser.releaser.after entry point data, pass the
  'tagdir' value (if a checkout has been made).  Patch by Wolfgang
  Schnerring, thanks!
  [maurits]

- Fixed tests to also pass with slightly newer git.
  [maurits]


3.11 (2010-06-25)
-----------------

- Small tweak: allowing zc.rst2's "rst2 html" in addition to docutils' own
  "rst2html".


3.10 (2010-06-15)
-----------------

- Fix : when running 'release' with python2.6 against a private egg server,
  the distutils 'register' command would run against PyPI
  while 'upload' command would run against private server.
  (-r option needs to be stated twice)
  [gotcha]


3.9 (2010-06-11)
----------------

- Again at the end of a fullrelease report the location of the
  directory containing the checkout of the tag, if it has been made.
  [maurits]


3.8 (2010-05-28)
----------------

- Also allowing ``CHANGES`` in addition to ``HISTORY.txt`` and ``CHANGES.txt``
  as a history filename.  Keeps several Django packages happy.


3.7 (2010-05-07)
----------------

- Added support for bzr.  Fixes
  https://bugs.launchpad.net/zest.releaser/+bug/490816  [menesis]


3.6 (2010-04-13)
----------------

- A ``version='1.0',`` string inside the ``setup()`` call no longer has
  non-pep8 spaces around the ``=``.  Fixes
  https://bugs.launchpad.net/zest.releaser/+bug/562122  [reinout]

- Got rid of ugly setup.py hack with UltraMagicString that was meant
  to avoid encoding errors when registering this package at pypi but
  which was not working for python2.4 (at least with collective.dist).
  Only ascii is allowed in the long_description if you want to avoid
  problems at one point or another.
  [maurits]


3.5 (2010-02-26)
----------------

- Treat CHANGES.txt and HISTORY.txt the same: the first that is found
  in a directory is chosen for changing, instead of first looking
  everywhere for a HISTORY.txt and then for a CHANGES.txt.
  [maurits]


3.4 (2010-02-02)
----------------

- Always build zip files if using python2.4 [do3cc]

- bugfix: added 'spreaded_internal' property to BaseVersionControl
  objects, so filefind() does not exclude a directory just because
  there is no '.git' folder in it. It still excludes directory where
  there is no '.svn' folder in SVN repositories. [vincent]


3.3 (2009-12-29)
----------------

- Fixed test failures when run on a computer with a new style pypi
  config.  We now always use an old style config when running the
  tests.
  [maurits]

- Fixed the release command for hg 1.1 (e.g. Ubuntu 9.04).
  [maurits]


3.2 (2009-12-22)
----------------

- Replaced commands.getoutput() with a system() function grabbed from buildout
  on suggestion by Adam Groszer.  Goal: make zest.releaser work also on
  windows.

- Improved entry point documentation.

- Added launchpad bugtracker at https://bugs.launchpad.net/zest.releaser (and
  pointing at that in the documentation).


3.1 (2009-11-27)
----------------

- Added documentation for entry points.  [reinout]


3.0 (2009-11-27)
----------------

- Added support for extension by means of entry points.  There is no
  documentation that advertises it yet as I want to treat it as experimental
  till I've used it a few times.  [reinout]


2.12 (2009-11-26)
-----------------

- Fixed mercurial sdist creation.  [reinout]

- A missing history file does not result anymore in a keyerror in prerelease.
  [reinout]

- Added lots of test output normalization so that errors aren't hidden by
  the large number of ``...`` in the doctests.  [reinout]


2.11 (2009-11-25)
-----------------

- Added /tag besides /tags for subversion [gotcha]

- Fixed tests failures. [gotcha]


2.10 (2009-10-22)
-----------------

- Added support for git.  [reinout]

- Lots of internal refactoring and small fixes.  [reinout]

- Started tests.  zest.releaser went from 0 to 94% coverage.  [reinout]


2.9.3 (2009-09-22)
------------------

- Uploading to multiple package indexes should now work in python2.6
  (though ironically it now does not work for me on python2.4, but that
  has nothing to do with zest.releaser.)  Added documentation for this.
  [maurits]

- Make sure the next version suggestion for 1.0rc6 is 1.0rc7.
  [maurits]

- In subversion, first try to get the package from the setup.py before
  falling back to the svn info, just like for mercurial.  This fixes
  the problem that e.g. Products.feedfeeder was not recognized as
  being on pypi as the svn directory name was feedfeeder.
  [maurits]


2.9.2 (2009-09-17)
------------------

- Umlauts in a changelog don't break the logger anymore when using python2.6.2
  when the umlauts turn up in the diff.  This is due to a 2.6.2 regression
  bug, see http://bugs.python.org/issue5170.  Should be fixed in 2.6.3 when it
  comes out.  [reinout]

- (Release 2.9 and 2.9.1 are unreleased because of a setuptools bug with,
  sigh, non-ascii characters which made a dirty setup.py hack necessary).
  [reinout]


2.8 (2009-08-27)
----------------

- Fixed the release command when used in a french environment.
  In French "svn info" returns 'URL :', not 'URL:'.
  [vincentfretin]


2.7 (2009-07-08)
----------------

- Before asking setup.py for its version or name, first run egg_info,
  as that may get rid of some warnings that otherwise end up in the
  extracted version or name, like UserWarnings.
  [maurits]


2.6 (2009-05-25)
----------------

- Small change: the questions don't print a newline anymore after the question
  (and before the user pressed enter).  This makes it clearer if enter has
  been pressed yet.  Suggestion by jkolman.  [reinout]


2.5 (2009-05-20)
----------------

- Revert to previous behaviour: when a package has not been released
  yet on pypi, decline to register it: the first time should be
  deliberate and manual, to avoid accidentally uploading client
  packages to pypi.
  [maurits]


2.4 (2009-05-15)
----------------

- Factored release.py out into a new pypi.py, solving a few possible
  problems with missing or misconfigured .pypirc files.  [maurits]


2.3 (2009-05-11)
----------------

- Fixed release script when the .pypirc file does not contain a
  distutils section or that section does not contain a index-servers
  option.  [maurits]


2.2 (2009-05-11)
----------------

- postrelease: suggestion for next version after 1.1.19 is not
  1.1.110, but 1.1.20.  [maurits]

- Make it work with collective.dist (mregister/mupload) [WouterVH]
  see http://plone.org/documentation/tutorial/how-to-upload-your-package-to-plone.org/installing-collective.dist


2.1 (2009-04-09)
----------------

- Fix lasttagdiff command to work with Mercurial by truncating the '+'
  character from the revision id, since that only indicates uncommitted
  changes exist.

- Make sure we find package/name/HISTORY.txt before we find
  docs/HISTORY.txt.  [maurits]

- Fixed checking for self.internal_filename: we would incorrectly
  check ('.', 's', 'v', 'n') instead of '.svn'.  [maurits]


2.0 (2009-04-01)
----------------

- Added tag_url method to get lasttagdiff (and zest.stabilizer)
  working again.  [maurits]

- Merged kteague-multi-vcs branch with, woohoo, mercurial support!  [reinout]

- Mercurial support by Kevin Teague.  [kteague]

- ``postrelease`` put a space in the new version number in
  ``setup.py`` (between version number and ``dev``). Removed this
  space as it is not necessary (in best case). [icemac]


1.13 (2009-03-17)
-----------------

- Also looking for ``CHANGES`` in addition to ``HISTORY.txt`` and
  ``CHANGES.txt`` as some packages use that convention.  [reinout]

- Added ``lasttagdiff`` command that shows the diff between the last release
  and the currently committed trunk.  Handy for checking whether the changelog
  is up to date.  [reinout]


1.12 (2009-03-17)
-----------------

- When doing a fullrelease and if the release step made a checkout of the tag
  into an temp directory, that temp directory is again printed after
  fullrelease finishes. Otherwise you've got to do a lot of scrolling.
  [reinout]


1.11 (2009-03-04)
-----------------

- When the found history file contains no version headings, look for a
  second history file: more than once I have the standard
  docs/HISTORY.txt that paster creates and I just add a pointer there
  to the real package/name/HISTORY.txt.  [maurits]


1.10 (2009-02-25)
-----------------

- A ``    version = '1.0',`` in setup.py is now also rewritten
  correctly.  Previously just a ``version = '1.0'`` would be injected,
  so without indentation and comma.  [reinout]

- Ask before checking out the tag. Sometimes the checkout is huge and
  you know you don't want it. You don't get asked for a pypi upload,
  though if you don't check out the tag.  [reinout]


1.9 (2009-02-24)
----------------

- 'release' now also makes a tag checkout in a temporary directory.
  [Reinout]

- Made 'longtest' work on Linux as there the command is 'rst2html' and
  apparently on the Mac it is 'rst2html.py'.  [maurits]


1.8 (2009-02-23)
----------------

- Added 'longtest' command that renders a setup.py's long description
  and opens it in a web browser.  [reinout]


1.7 (2009-02-16)
----------------

- Supporting alternative history version header format: 'version - date'.
  [reinout]


1.6 (2009-02-14)
----------------

- Patch by Michael Howitz: sys.executable is used instead of a string that
  doesn't work on every system.  [reinout]


1.5 (2009-02-11)
----------------

- Changed y/n into Y/n, so defaulting to 'yes'.  [reinout]

- Improved the documentation.  [reinout]

- When a yes/no question is asked, do not treat 'no' as the default
  but explicitly ask for an input -- it was too easy to press enter
  and wrongly expect 'yes' as default.  [maurits]


1.4 (2008-10-23)
----------------

- Fixed missing import of utils.  [maurits]


1.3 (2008-10-23)
----------------

- Moved stabilize script to zest.stabilizer so that zest.releaser is just for
  releasing individual packages. Nice, tidy, reusable.  [reinout]

- Allowing '-v' option on all commands: it gives you debug-level logging.
  [reinout]


1.2 (2008-10-16)
----------------

- We now prefer the version from setup.py over any version.txt file
  found.  When getting or changing the version we get/change the
  setup.py version when it differs from the found version.txt version.
  [maurits]


1.1 (2008-10-15)
----------------

- Cleaned out zest-specific stuff. Cleaned up 'release'. [reinout]


1.0 (2008-10-15)
----------------

- Stabilize looks up the most recent tag of our development packages and uses
  gp.svndevelop to allow svn checkouts as development eggs. [reinout]

- Do not look for version.txt in directories that are not handled by
  subversion.  Use case: Products.feedfeeder, which has a buildout.cfg
  and so can have a parts directory with lots of version.txt files...
  [maurits]


0.9 (2008-10-02)
----------------

- release: offer to register and upload the egg to the cheese shop.
  After that you still have the option to upload to our own tgz
  server.  [maurits]

- postrelease: for the suggestion of a new version simply try add 1 to
  the last character in the version; the previous logic failed for
  example for '1.0b3'.  [maurits]

- prerelease: ask user to enter next version (give him a suggestion).
  Handy when you want to change '1.0b3 dev' into '1.0'.  [maurits]

- Started 'stabilize'. [reinout]


0.8 (2008-09-26)
----------------

- fullrelease: change back to the original directory after each
  pre/actual/post release step.  [maurits]

- release: switch back to original directory when ready to fix 'commit
  to tag' error.  [maurits]

- prerelease: quit when no version is found.  [maurits]

- Reverted sleeping fix from 0.7 as it did not work.  [maurits]


0.7 (2008-09-26)
----------------

- fullrelease: hopefully fix a 'commit on tag' bug by sleeping three
  seconds before doing the post release.  [maurits]


0.6 (2008-09-26)
----------------

- Added fullrelease script that does a prerelease, actual release and
  post release in one go.  [maurits]


0.5 (2008-09-26)
----------------

- Factored part of prerelease.check_version() out into
  utils.cleanup_version().  We now use that while setting the version
  in the history during postrelease.  [maurits]

- Add newline at the end of the generated version.txt.  [maurits]


0.4 (2008-09-26)
----------------

- Made the logging userfriendly.


0.3 (2008-09-26)
----------------

- Postrelease: Better injection of history. Various other robustness fixes.


0.2 (2008-09-26)
----------------

- postrelease: added suggestion for new version (a plain enter is enough to
  accept it). [reinout]

- prerelease: ask before changing version + solidified regex for heading
  detection. [reinout]

- prerelease: detect non-development versions better and change them.
  [maurits]

- prerelease: made the commit message read: 'Preparing release xxx'.
  [maurits]

- postrelease: made the new version something like '1.0 dev'.
  [maurits]

- postrelease: we now add some lines to the history now.  [maurits]

- prerelease: try changing the version to a non-development version,
  stripping off something like '(...)'.  [maurits]

- release: Refactored so release.py has the 'main' function required
  by setup.py.  [maurits]


0.1 (2008-09-24)
----------------

- Got a basic version of the prerelease script working (version check, history
  file updating, committing). [reinout]

- Started by copying the guidelines script. [reinout]
