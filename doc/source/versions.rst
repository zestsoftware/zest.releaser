Version handling
================

Where does the version come from?
---------------------------------

A version number is essentially what zest.releaser cannot do without. A
version number can come from four different locations:

- The ``setup.py`` file. Two styles are supported::

    version = '1.0'

    def setup(
        version=version,
        name='...

  and also::

    def setup(
        version='1.0',
        name='...

- The ``setup.cfg`` file. zest.releaser will look for something like::

    [metadata]
    name = ...
    version = 1.0

- If no ``setup.py`` is found, zest.releaser looks for a ``version.txt``
  file. It should contain just a version number (a newline at the end is OK).

  Originally the ``version.txt`` was only meant to support really old and
  ancient `Plone <http://plone.org>`_ packages, but it turned out to be quite
  useful for non-Python packages, too. A completely static website, for
  instance, that you *do* want to release and that you *do* want a changelog
  for.

- A ``__version__`` attribute in a Python file. You need to tell zest.releaser
  *which* Python file by adding (or updating) the ``setup.cfg`` file next to
  the ``setup.py``. You need a ``[zest.releaser]`` header and a
  ``python-file-with-version`` option::

    [zest.releaser]
    python-file-with-version = mypackage/__init__.py

  Because you need to configure this explicitly, this option takes precedence
  over any ``setup.py`` or ``version.txt`` file.


Where is the version number being set?
--------------------------------------

Of those four locations where the version can come from, only the first one
found is also set to the new value again. Zest.releaser assumes that there's
only *one* location.

`According to PEP 396
<http://www.python.org/dev/peps/pep-0396/#specification>`_, the version should
have **one** source and all the others should be derived from it.


Using the version number in ``setup.py`` or ``setup.cfg`` as ``__version__``
----------------------------------------------------------------------------

Here are opinionated suggestions from the zest.releaser main authors about how
to use the version information. For some other ideas, see the `zest.releaser
issue 37 <https://github.com/zestsoftware/zest.releaser/issues/37>`_
discussion.

- The version in the ``setup.py`` is the real version.

- Add a ``__version__`` attribute in your main module. Often this will be an
  ``__init__.py``. Set this version attribute with ``pkg_resources``, which is
  automatically installed as part of setuptools/distribute. Here's `the code
  <https://github.com/zestsoftware/zest.releaser/blob/master/zest/releaser/__init__.py>`_
  from ``zest/releaser/__init__.py``::

      import pkg_resources

      __version__ = pkg_resources.get_distribution("zest.releaser").version

  This way you can do::

      >>> import zest.releaser
      >>> zest.releaser.__version__
      '3.44'

- If you use `Sphinx <http://sphinx.pocoo.org/>`_ for generating your
  documentation, use the same ``pkg_resources`` trick to set the version and
  release in your Sphinx's ``conf.py``. See `zest.releaser's conf.py
  <https://github.com/zestsoftware/zest.releaser/blob/master/doc/source/conf.py>`_.
