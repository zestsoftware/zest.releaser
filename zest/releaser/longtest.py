"""Do the checks and tasks that have to happen before doing a release.
"""

from zest.releaser import choose
from zest.releaser import utils
from zest.releaser.utils import _execute_command

import logging
import os
import readme_renderer
import sys
import tempfile
import webbrowser


HTML_PREFIX = """<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  </head>
  <body>"""
HTML_POSTFIX = """
  </body>
</html>"""


readme_renderer  # noqa, indicating it as a dependency
logger = logging.getLogger(__name__)


def show_longdesc():
    vcs = choose.version_control()
    name = vcs.name

    # Corner case. importlib.metadata wants to be next to the egg-info. Which
    # doesn't play nice if the egg-info is in a src/ dir, which is a
    # relatively common occurrence.
    if os.path.exists(f"src/{name}.egg-info"):
        logger.info("egg-info dir found in src/ dir, chdir'ing to src first")
        os.chdir("src")

    filename = tempfile.mktemp(".html")
    html = _execute_command(
        [
            sys.executable,
            "-m",
            "readme_renderer",
            "--package",
            name,
        ]
    )

    if "<html" not in html[:20]:
        # Add a html declaration including utf-8 indicator
        html = HTML_PREFIX + html + HTML_POSTFIX

    with open(filename, "wb") as fh:
        fh.write(html.encode("utf-8"))

    url = "file://" + filename
    logging.info("Opening %s in your webbrowser.", url)
    webbrowser.open(url)


def main():
    parser = utils.base_option_parser()
    parser.add_argument(
        "--headless",
        action="store_true",
        dest="headless",
        default=False,
        help="Deprecated",
    )
    options = utils.parse_options(parser)
    utils.configure_logging()
    if options.headless:
        logger.error("--headless is deprecated, for real checks use 'twine check'.")
        sys.exit(1)
    show_longdesc()
