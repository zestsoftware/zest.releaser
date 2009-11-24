import z3c.testsetup


import re
from zope.testing import renormalizing
checker = renormalizing.RENormalizing([
    # .pypirc seems to be case insensitive
    (re.compile('[Pp][Yy][Pp][Ii]'), 'pypi'),
    ])


test_suite = z3c.testsetup.register_all_tests('zest.releaser', checker=checker)
