Assumptions
===========

Zest.releaser originated at `Zest software <https://zestsoftware.nl>`_ so there
are some assumptions build-in that might or might not fit you.  Lots of people
are using it in various companies and open source projects, so it'll probably
fit :-)

- If you are using svn, your svn is structured with /trunk, /tags (or
  /tag) and optionally /branches (or /branch).  Both a /trunk or a
  /branches/something checkout is ok.

- We absolutely need a version. There's a ``version.txt`` or ``setup.py`` in
  your project. The ``version.txt`` has a single line with the version number
  (newline optional). The ``setup.py`` should have a single ``version =
  '0.3'`` line somewhere. You can also have it in the actual ``setup()`` call,
  on its own line still, as `` version = '0.3',``. Indentation and the comma
  are preserved.  If you need something special, you can always do a
  ``version=version`` and put the actual version statement in a
  zest.releaser-friendly format near the top of the file. Reading (in Plone
  products) a version.txt into setup.py works great, too.

- The history/changes file restriction is probably the most severe at the
  moment. zest.releaser searches for a restructuredtext header with
  parenthesis. So something like::

    Changelog for xyz
    =================

    0.3 (unreleased)
    ----------------

    - Did something

    0.2 (1972-12-25)
    ----------------

    - Reinout was born.

  That's just the style we started with.  Pretty clear and useful.
