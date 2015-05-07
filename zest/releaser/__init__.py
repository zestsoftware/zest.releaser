import pkg_resources
from colorama import init

# Initialize colorized output.  Set it to reset after each print, so
# for example a foreground color does not linger into the next print.
# Note that the colorama docs say you should call `deinit` at exit,
# but it looks like it already does that itself.
init(autoreset=True)

__version__ = pkg_resources.get_distribution("zest.releaser").version
