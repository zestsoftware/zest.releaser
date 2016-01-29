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

We have these options:

release = yes / no
    Default: yes.  When this is false, zest.releaser sets ``no`` as
    default answer for the question if you want to create a checkout
    of the tag.

create-wheel = yes / no
    Default: no.  Set to yes if you want zest.releaser to create
    Python wheels.  You need to install the ``wheel`` package for this
    to work.

extra-message = [ci skip]
    Extra message to add to each commit (prerelease, postrelease).

no-input = yes / no
    Default: no.  Set this to yes to accept default answers for all
    questions.


Per project options
-------------------

You can change some settings per project by adding instructions for
zest.releaser in a ``setup.cfg`` file.  This will only work for a
Python package.

These are the same options as the global ones.  If you set an option
locally in a project, this will override the global option.
