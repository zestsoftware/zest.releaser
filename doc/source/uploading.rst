Uploading to pypi (or custom servers)
=======================================

When the (full)release command tries to upload your package to a pypi server,
zest.releaser basically executes the command ``python setup.py sdist`` and does a
``twine upload``.  The twine command replaces the less safe
``python setup.py sdist upload``.

For safety reasons zest.releaser will *only* offer to upload your package to
https://pypi.python.org when the package is already registered there.  If this
is not the case yet, you get a confirmation question whether you want to
register a new package with ``twine register``.

If the upload or register command fails, you probably need to configure
your PyPI configuration file. And of course you need to have
``setuptools`` and ``twine`` installed, but that is done automatically
when installing ``zest.releaser``.


PyPI configuration file (``~/.pypirc``)
---------------------------------------

For uploads to PyPI to work you will need a ``.pypirc`` file in your home directory that
has your pypi login credentials.  This may contain alternative servers too::

  [distutils]
  index-servers =
    pypi
    warehouse
    local

  [pypi]
  # default repository is pypi.python.org
  username:maurits
  password:secret

  [warehouse]
  # This is the successor for PyPI, which you can/should already use.
  repository:https://upload.pypi.org/legacy/
  username:maurits
  password:secret

  [local]
  repository:http://localhost:8080/test/products/
  username:maurits
  password:secret
  # You may need to specify the realm, which is the domain the
  # server sends back when you do a challenge:
  #realm:Zope

See the `Python Packaging User Guide`_ for more info.

.. _`Python Packaging User Guide`: https://packaging.python.org/en/latest/distributing.html#uploading-your-project-to-pypi for more info.

When all this is configured correctly, zest.releaser will first upload
to the official PyPI (if the package is registered there already).
Then it will offer to upload to the other index servers that you have
specified in ``.pypirc``.

Note that since version 3.15, zest.releaser also looks for this information in
the ``setup.cfg`` if your package has that file.  One way to use this, is to
restrict the servers that zest.releaser will ask you to upload to.  If you have
defined 40 index-servers in your pypirc but you have the following in your
setup.cfg, you will not be asked to upload to any server::

  [distutils]
  index-servers =

Note that after creating the tag we still ask you if you want to checkout that
tag for tweaks or pypi/distutils server upload.  We could add some extra
checks to see if that is really needed, but someone who does not have
index-servers listed, may still want to use an entry point like
`gocept.zestreleaser.customupload
<http://pypi.python.org/pypi/gocept.zestreleaser.customupload>`_ to do
uploading, or do some manual steps first before uploading.

Since version 6.8, zest.releaser by default no longer *registers* a new package, but only uploads it.
This is usually good.
See `Registering a package`_ for an explanation.

Some people will hardly ever want to do a release on PyPI but in 99 out of 100
cases only want to create a tag.  They won't like the default answer of 'yes'
to that question of whether to create a checkout of the tag.  So since version
3.16 you can influence this default answer.  You can add some lines to the
``.pypirc`` file in your home directory to change the default answer for all
packages, or change it for individual packages in their ``setup.cfg`` file.
The lines are this::

  [zest.releaser]
  release = no

You can use no/false/off/0 or yes/true/on/1 as answers; upper, lower or mixed
case are all fine.


Uploading with twine
--------------------

Since version 6.0, we always use twine_ for uploading to the Python
Package Index, because it is safer: it uses ``https`` for uploading.
Since version 4.0 we already prefered it if it was available, but it
is now a core dependency, installed automatically.

.. _twine: https://pypi.python.org/pypi/twine

Since version 6.6.6 we use it in a way that should work with ``twine``
1.6.0 and higher, including future versions.


Uploading wheels
----------------

First, you should install the ``zest.releaser[recommended]`` extra, or
run ``pip install wheel`` yourself next to ``zest.releaser``.  Then
create or edit ``setup.cfg`` in your project (or globally in your
``~/.pypirc``) and add this to create and upload a wheel to upload to
PyPI::

  [zest.releaser]
  create-wheel = yes

See http://pythonwheels.com for deciding whether this is a good idea
for your package.  Briefly, if it is a pure Python 2 *or* pure Python
3 package: just do it.


Registering a package
---------------------

Registering a package does two things:

- It claims a package name on your behalf, so that you can upload a file to it.
- If you already registered the package previously, it updates the general package information.
  So every time you make a new release, you should register the package.

Well, that used to be the case, but things have changed.

Since version 6.8, zest.releaser by default no longer *registers* a package, but only uploads it.
This is because for the standard Python Package Index (PyPI),
registering a package is no longer needed: this is done automatically
when uploading a distribution for a package.  In fact, trying to
register may *fail*.  See this `issue <https://github.com/zestsoftware/zest.releaser/issues/191>`_.

But you may be using your own package server, and registering
may be wanted or even required there.  In this case
you will need to turn on the register function.
In your ``setup.cfg`` or ``~/.pypirc``, use the following to ensure that
register is called on the package server::

  [zest.releaser]
  register = yes

If you have specified multiple package servers, this option is used
for all of them.  There is no way to register and upload to server A,
and only upload to server B.


Adding extra text to a commit message
-------------------------------------

``zest.releaser`` makes commits in the prerelease and postrelease
phase.  Something like ``Preparing release 1.0`` and ``Back to
development: 1.1``.  You can add extra text to these messages by
configuration in your ``setup.cfg`` or global ``~/.pypirc``.  One use
case for this is telling Travis to skip Continuous Integration builds::

  [zest.releaser]
  extra-message = [ci skip]


Signing your commits or tags with git
-------------------------------------

If you are using git, maybe you want to sign your commits, or more likely your tags, with your gpg key.
``zest.releaser`` does not do anything special for this: it just calls the normal ``git commit`` or ``git tag``.
So if you want to sign anything, you should set this up in your ``git`` configuration, so it works outside of ``zest.releaser`` as well.
Run these commands to configure gpg signing for git::

  git config commit.gpgsign true
  git config tag.gpgsign true


Including all files in your release
-----------------------------------

By default, only the Python files and a ``README.txt`` are included (by
setuptools) when you make a release. So you miss out on your changelog, json
files, stylesheets and so on. There are two strategies to include those other
files:

- Add a ``MANIFEST.in`` file in the same directory as your ``setup.py`` that
  lists the files you want to include. Don't worry, wildcards are
  allowed. Actually, zest.releaser will suggest a sample ``MANIFEST.in`` for
  you if you don't already have it. The default is often good enough.

- Setuptools *can* detect which files are included in your version control
  system (svn, git, etc.) which it'll then automatically include.

The last approch has a problem: not every version control system is supported
out of the box. So you might need to install extra packages to get it to
work. So: use a ``MANIFEST.in`` file to spare you the trouble. If not, here
are some extra packages:

- setuptools-git (Setuptools plugin for finding files under Git
  version control)

- setuptools_hg (Setuptools plugin for finding files under Mercurial
  version control)

- setuptools_bzr (Setuptools plugin for finding files under Bazaar
  version control)

- setuptools_subversion (Setuptools plugin for finding files under
  Subversion version control.)  You probably need this when you
  upgrade to the recent subversion 1.7.  If you suddenly start missing
  files in the sdists you upload to PyPI you definitely need it.
  Alternatively: set up a proper MANIFEST.in as that method works with
  any version control system.

In general, if you are missing files in the uploaded package, the best
is to put a proper ``MANIFEST.in`` file next to your ``setup.py``.
See `zest.pocompile`_ for an example.

.. _`zest.pocompile`: http://pypi.python.org/pypi/zest.pocompile


Running automatically without input
-----------------------------------

Sometimes you want to run zest.releaser without hitting ``<enter>`` all the
time. You might want to run zest.releaser from your automatic test
environment, for instance. For that, there's the ``--no-input`` commandline
option. Pass that and all defaults will be accepted automatically.

This means your version number and so must be OK. If you want to have a
different version number from the one in your ``setup.py``, you'll need to
change it yourself by hand. And the next version number will be chosen
automatically, too. So ``1.2`` will become ``1.3``. This won't detect that you
might want to do a ``1.3`` after a ``1.2.1`` bugfix release, but we cannot
perform feats of magic in zest.releaser :-)

In case you always want to accept the defaults, a setting in your
``setup.cfg`` is available::

    [zest.releaser]
    no-input = yes

An important reminder: if you want to make sure you never upload anything
automatically to the python package index, include the ``release = no``
setting in ``setup.cfg``::

    [zest.releaser]
    no-input = yes
    release = no
