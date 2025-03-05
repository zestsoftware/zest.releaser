Options
=======

Zest.releaser tries not to burden you with lots of command line
options.  Instead, it asks questions while doing its job.  But in some
cases, a command line option makes sense.

Related: you can change some settings globally in your ``~/.pypirc``
file or per project in a ``setup.cfg`` file.  This is only for Python
packages.


Command line options
--------------------

These command line options are supported by the release commands
(``fullrelease``, ``prerelease``, ``release``, ``postrelease``)
and by the ``addchangelogentry`` command.

-v, --verbose
    Run in verbose mode, printing a bit more, mostly only interesting
    for debugging.

-h, --help
    Display help text

--no-input
    Don't ask questions, just use the default values.  If you are very
    sure that all will be fine when you answer all questions with the
    default answer, and you do not want to press Enter several times,
    you can use this option.  The default answers (sometimes yes,
    sometimes no, sometimes a version number) are probably sane
    and safe.  But do not blame us if this does something you do not
    want. :-)

The ``addchangelogentry`` command requires the text you want to add as
argument.  For example::

  $ addchangelogentry "Fixed bug."

Or on multiple lines::

  $ addchangelogentry "Fixed bug.

  This was difficult."

The ``bumpversion`` and ``postrelease`` commands accept some mutually exclusive options:

- With ``--feature`` we update the minor version.

- With ``--breaking`` we update the major version.

- With ``--final`` we remove alpha / beta / rc markers from the version.


Global options
--------------

You can configure zest.releaser for all projects by editing the
``.pypirc`` file in your home directory.  This is the same file that
needs to contain your PyPI credentials if you want to release to the
Python Packaging Index.  See the topic on Uploading.  This also has
more info on most options.

Lots of things may be in this file, but zest.releaser looks for a
``zest.releaser`` section, like this::

  [zest.releaser]
  some-option = some value

For true/false options, you can use no/false/off/0 or yes/true/on/1 as
answers; upper, lower or mixed case are all fine.

Various options change the default answer of a question.
So if you want to use the ``--no-input`` command line option
or want to press Enter a couple of times without thinking too much,
see if you can tweak the default answers by setting one of these options

We have these options:

release = true / false
    Default: true.  When this is false, zest.releaser sets ``false`` as
    default answer for the question if you want to create a checkout
    of the tag.

upload-pypi = true / false
    Default: true. Normally you won't use this setting. Only if you want to make a
    release without actually uploading it, set it to false. (Note that you still need
    release=true).

create-wheel = true / false
    Default: true. Set to false if you do not want zest.releaser to create Python wheels.

extra-message = [ci skip]
    Extra message to add to each commit (prerelease, postrelease).

prefix-message = [TAG]
    Prefix message to add at the beginning of each commit (prerelease, postrelease).

no-input = true / false
    Default: false.  Set this to true to accept default answers for all
    questions.

register = true / false
    Default: false.  Set this to true to register a package before uploading.
    On the official Python Package Index registering a package is no longer needed,
    and may even fail.

push-changes = true / false
    Default: true.  When this is false, zest.releaser sets ``false`` as
    default answer for the question if you want to push the changes to
    the remote.

less-zeroes = true / false
    Default: false.
    This influences the version suggested by the bumpversion command.
    When set to true:

    - Instead of 1.3.0 we will suggest 1.3.
    - Instead of 2.0.0 we will suggest 2.0.

version-levels = a number
    Default: 0.
    This influences the version suggested by the postrelease and bumpversion commands.
    The default of zero means: no preference, so use the length of the current number.

    This means when suggesting a next version after 1.2:

    - with 0 we will suggest 1.3: no change in length
    - with 1 we will still suggest 1.3, as we will not
      use this to remove numbers, only to add them
    - with 2 we will suggest 1.3
    - with 3 we will suggest 1.2.1

    If the current version number has more levels, we keep them.
    So with ``version-levels=1`` the next version for 1.2.3.4 will be 1.2.3.5.

development-marker = a string
    Default: ``.dev0``
    This is the development marker.
    This is what gets appended to the version in postrelease.

tag-format = a string
    Default: ``{version}``
    This is a formatter that changes the name of the tag.
    It needs to contain ``{version}``.
    For backward compatibility, it can contain ``%(version)s`` instead.

tag-message = a string
    Default: ``Tagging {version}``
    This formatter defines the commit message passed to the ``tag``
    command of the VCS.
    It must contain ``{version}``.

tag-signing = true / false
    Default: false.
    When set to true, tags are signed using the signing feature of the
    respective vcs. Currently tag-signing is only supported for git.
    Note: When you enable it, everyone releasing the project is
    required to have git tag signing set up correctly.

date-format = a string
    Default: ``%%Y-%%m-%%d``
    This is the format string for the release date to be mentioned in the
    changelog.

    Note: the % signs should be doubled for compatibility with other tools
    (i.e. pip) that parse setup.cfg using the interpolating ConfigParser.

history-file = a string
    Default: empty
    Usually zest.releaser can find the correct history or changelog file on its own.
    But sometimes it may not find anything, or it finds multiple files and selects the wrong one.
    Then you can set a path here.

history_format = a string
  Default: empty.
  Set this to ``md`` to handle changelog entries in Markdown.

run-pre-commit = true / false
    Default: false.
    New in version 7.3.0.
    When set to true, pre commit hooks are run.
    This may interfere with releasing when they fail.


Per project options
-------------------

You can change some settings per project by adding instructions for
zest.releaser in a ``setup.cfg`` file.  This will only work for a
Python package.

These are the same options as the global ones.  If you set an option
locally in a project, this will override the global option.

You can also set these options in a ``pyproject.toml`` file. If you do
so, instead of having a ``[zest.releaser]`` section, you should use a
``[tool.zest-releaser]`` section. For true/false options in a
``pyproject.toml``, you must use lowercase true or false; for string
options like ``extra-message`` or ``prefix-message``, you should put
the value between double quotes, like this::

  [tool.zest-releaser]
  create-wheel = false
  extra-message = "[ci skip]"
