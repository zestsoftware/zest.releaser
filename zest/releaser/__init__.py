from colorama import init
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version


# Initialize colorized output.  Set it to reset after each print, so
# for example a foreground color does not linger into the next print.
# Note that the colorama docs say you should call `deinit` at exit,
# but it looks like it already does that itself.
init(autoreset=True)

# Depending on which Python and setuptools version you use, and whether you use
# an editable install or install from sdist or wheel, or with pip or Buildout,
# there may be problems getting our own version.  Let's not break on that.
try:
    __version__ = version("zest.releaser")
except PackageNotFoundError:
    try:
        __version__ = version("zest-releaser")
    except PackageNotFoundError:
        __version__ = "unknown"
