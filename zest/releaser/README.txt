Zest release scripts
====================


Summary: package releasing made easy
------------------------------------

* Updates the version number. 0.3 dev (current) to 0.3 (release) to 0.4 dev
  (new development version). Either in setup.py or in version.txt.

* Updates the history/changes file (logs the release date on release) and adds
  a new section for the upcoming changes (new development version).

* Tags the release in svn with the version number.

* Uploads a source release to pypi (if the package is available
  there).  It also checks out the tag in a temporary directory in case
  you need to modify it.

Note that zest.releaser isn't restricted to python packages. We use it
regularly to tag buildouts. You only need a ``version.txt`` in your svn
checkout.


Installation
------------

Just a simple ``easy_install zest.releaser`` is enough.

It gives you four commands to help in releasing python packages.  They must be
run in a subversion checkout.  These are the commands:

- **prerelease**: asks the user for a version number (defaults to the current
  version minus a 'dev' or so), updates the setup.py or version.txt and the
  HISTORY.txt/CHANGES.txt with this and offers to commit those changes to
  subversion.

- **release**: copies the the trunk or branch of the current checkout and
  creates a subversion tag of it.  Makes a checkout of the tag in a
  temporary directory.  Offers to register and upload a source dist
  of this package to PyPI (Python Package Index).  Note: if the package has
  not been registered yet, it will not do that for you.  You must register the
  package manually (``python setup.py register``) so this remains a conscious
  decision.  The main reason is that you want to avoid having to say: "Oops, I
  uploaded our client code to the internet; and this is the initial version
  with the plaintext root passwords."

- **postrelease**: asks the user for a version number (gives a sane default),
  adds a development marker to it, updates the setup.py or version.txt and the
  HISTORY.txt with this and offers to commit those changes to subversion.

- **fullrelease**: all of the above in order.

- **longtest**: small tool that renders a setup.py's long description
  and opens it in a web browser. This assumes an installed docutils
  (as it needs ``rst2html.py``).


Current assumptions
-------------------

zest.releaser originated at `Zest software <http://zestsoftware.nl>`_ so there
are some assumptions build-in that might or might not fit you.

- Your svn is structured with /trunk, /tags and optionally /branches.  Both a
  /trunk or a /branches/something checkout is ok.

- There's a version.txt or setup.py in your project. The version.txt has a
  single line with the version number (newline optional). The setup.py should
  have a single ``version = '0.3'`` line somewhere. zest.releaser only inserts
  such a line, though it keeps the existing indentation intact. But commas at
  the end or so: they're all zapped.  If you need something special, you can
  always do a ``version=version`` and put the actual version statement in a
  zest.releaser-friendly format near the top of the file. Reading (in Plone
  products) a version.txt into setup.py works great, too.

- The history file (either HISTORY.txt or CHANGES.txt) restriction is probably
  the most severe at the moment. zest.releaser searches for a restructuredtext
  header with parenthesis. So something like::

    Changelog for xyz
    =================

    0.3 (unreleased)
    ----------------

    - Did something

    0.2 (1972-12-25)
    ----------------

    - Reinout was born.

  That's just the style we started with.  Pretty clear and useful.  It also
  supports the current zopeskel style with ``0.3 - unreleased``.


Notes
-----

Note that there are alternative release scripts available, for instance
http://pypi.python.org/pypi/collective.releaser .

The svn source can be found at
https://svn.plone.org/svn/collective/zest.releaser/trunk .
