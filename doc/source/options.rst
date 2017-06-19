Options
=======

Zest.releaser tries not too burden you with lots of command line
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

The ``bumpversion`` command accepts two mutually exclusive options:

- With ``--feature`` we update the minor version.

- With option ``--breaking`` we update the major version.


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

For yes/no options, you can use no/false/off/0 or yes/true/on/1 as
answers; upper, lower or mixed case are all fine.

Various options change the default answer of a question.
So if you want to use the ``--no-input`` command line option
or want to press Enter a couple of times without thinking too much,
see if you can tweak the default answers by setting one of these options

We have these options:

release = yes / no
    Default: yes.  When this is false, zest.releaser sets ``no`` as
    default answer for the question if you want to create a checkout
    of the tag.

create-wheel = yes / no
    Default: no.  Set to yes if you want zest.releaser to create
    Python wheels.  You need to install the ``wheel`` package for this
    to work.

    If the package is a universal wheel, indicated by having
    ``universal = 1`` in the ``[bdist_wheel]`` section of
    ``setup.cfg``, then the default for this value is yes.

extra-message = [ci skip]
    Extra message to add to each commit (prerelease, postrelease).

no-input = yes / no
    Default: no.  Set this to yes to accept default answers for all
    questions.

register = yes / no
    Default: no.  Set this to yes to register a package before uploading.
    On the official Python Package Index registering a package is no longer needed,
    and may even fail.

push-changes = yes / no
    Default: yes.  When this is false, zest.releaser sets ``no`` as
    default answer for the question if you want to push the changes to
    the remote.

less-zeroes = yes / no
    Default: no.
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
    Default: ``%(version)s``
    This is a formatter that changes the name of the tag.
    It needs to contain ``%(version)s``

date-format = a string
    Default: ``%Y-%m-%d``
    This is the format string for the release date to be mentioned in the
    changelog.



Per project options
-------------------

You can change some settings per project by adding instructions for
zest.releaser in a ``setup.cfg`` file.  This will only work for a
Python package.

These are the same options as the global ones.  If you set an option
locally in a project, this will override the global option.
