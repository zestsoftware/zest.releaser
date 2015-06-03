"""Do the checks and tasks that have to happen before doing a release.
"""
try:
    from readme.rst import render
    HAVE_README = True
except ImportError:
    HAVE_README = False
import logging
import sys
import tempfile
import webbrowser

from zest.releaser import utils
from zest.releaser.utils import _execute_command

logger = logging.getLogger(__name__)


def show_longdesc():
    if not HAVE_README:
        logging.error(u'Error generating html. Please install `readme`.')
        sys.exit(1)

    filename = tempfile.mktemp(u'.html')
    # Note: for the setup.py call we use execute_command() from our
    # utils module. This makes sure the python path is set up right.
    longdesc = _execute_command(utils.setup_py([u'--long-description']))
    html, rendered = render(longdesc)
    if not rendered:
        # Stupid docutils throws SystemExit
        logging.error('Error generating html. Invalid ReST.')
        raise RuntimeError("Invalid markup which will not be rendered on "
                           "PyPI.")

    with open(filename, 'w') as fh:
        fh.write(html)
    url = u'file://' + filename
    logging.info(u"Opening {0} in your webbrowser.".format(url))
    webbrowser.open(url)


def main():
    utils.configure_logging()
    show_longdesc()
