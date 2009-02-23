"""Do the checks and tasks that have to happen before doing a release.
"""
import logging
import sys
import webbrowser
import tempfile
from commands import getoutput
import os

import utils

logger = logging.getLogger('longtest')


def show_longdesc():
    filename1 = tempfile.mktemp()
    filename2 = tempfile.mktemp()
    filename2 = filename2 + '.html'
    os.system('%s setup.py --long-description > %s' % (sys.executable, filename1))
    os.system('rst2html.py %s > %s' % (filename1, filename2))
    webbrowser.open(filename2)

def main():
    logging.basicConfig(level=utils.loglevel(),
                        format="%(levelname)s: %(message)s")
    show_longdesc()
