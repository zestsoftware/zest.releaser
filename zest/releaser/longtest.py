"""Do the checks and tasks that have to happen before doing a release.
"""
import logging
import os
import sys
import tempfile
import webbrowser

from zest.releaser import utils
from zest.releaser.utils import execute_command

logger = logging.getLogger(__name__)


def show_longdesc():
    filename1 = tempfile.mktemp()
    filename2 = tempfile.mktemp()
    filename2 = filename2 + '.html'
    # Note: for the setup.py call we use execute_command() from our
    # utils module. This makes sure the python path is set up right.
    # For the other calls we use os.system(), because that returns an
    # error code which we need.
    execute_command(utils.setup_py('--long-description > %s' %
                          filename1))
    error = os.system('rst2html.py %s > %s' % (filename1, filename2))
    if error:
        # On Linux it needs to be 'rst2html', without the '.py'
        error = os.system('rst2html %s > %s' % (filename1, filename2))
    if error:
        # Alternatively, zc.rst2 provides rst2 xyz.
        error = os.system('rst2 html %s > %s' % (filename1, filename2))
    if error:
        logging.error(
            'Error generating html. Please install docutils (or zc.rst2).')
        sys.exit(1)
    url = 'file://' + filename2
    logging.info("Opening %s in your webbrowser.", url)
    webbrowser.open(url)


def main():
    utils.configure_logging()
    show_longdesc()
