"""Do the checks and tasks that have to happen before doing a release.
"""
try:
    from docutils.core import publish_string
    HAVE_DOCUTILS = True
except ImportError:
    HAVE_DOCUTILS = False
import logging
import sys
import tempfile
import webbrowser

from zest.releaser import utils
from zest.releaser.utils import _execute_command

logger = logging.getLogger(__name__)


def show_longdesc():
    if not HAVE_DOCUTILS:
        # Stupid docutils throws SystemExit
        logging.error(
            'Error generating html. Please install docutils (or zc.rst2).')
        sys.exit(1)

    filename = tempfile.mktemp(u'.html')
    # Note: for the setup.py call we use execute_command() from our
    # utils module. This makes sure the python path is set up right.
    # For the other calls we use os.system(), because that returns an
    # error code which we need.
    longdesc = _execute_command(utils.setup_py([u'--long-description']))
    try:
        rst = publish_string(
            source=longdesc,
            writer_name='html',
            enable_exit_status=False)
    except SystemExit:
        # Stupid docutils throws SystemExit
        logging.error(
            'Error generating html. Invalid ReST.')
        raise

    with open(filename, 'w') as fh:
        fh.write(rst)
    url = u'file://' + filename
    logging.info(u"Opening {0} in your webbrowser.".format(url))
    webbrowser.open(url)


def main():
    utils.configure_logging()
    show_longdesc()
