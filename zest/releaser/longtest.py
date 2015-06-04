"""Do the checks and tasks that have to happen before doing a release.
"""
from __future__ import unicode_literals

import logging
import sys
import tempfile
import webbrowser

try:
    from readme.rst import render
    HAVE_README = True
except ImportError:
    HAVE_README = False

from zest.releaser import utils
from zest.releaser.utils import _execute_command

logger = logging.getLogger(__name__)


def show_longdesc():
    if not HAVE_README:
        logging.error(
            "To check the long description, we need the 'readme' package. "
            "(It is included if you install `zest.releaser[recommended]`)")
        sys.exit(1)

    filename = tempfile.mktemp('html')
    # Note: for the setup.py call we use _execute_command() from our
    # utils module. This makes sure the python path is set up right.
    longdesc = _execute_command(utils.setup_py('--long-description'))
    html, rendered = render(longdesc)
    if not rendered:
        logging.error(
            'Error generating html. Invalid ReST.')
        sys.exit(1)

    with open(filename, 'wb') as fh:
        fh.write(html.encode('utf-8'))

    url = 'file://' + filename
    logging.info("Opening %s in your webbrowser.", url)
    webbrowser.open(url)


def main():
    utils.configure_logging()
    show_longdesc()
