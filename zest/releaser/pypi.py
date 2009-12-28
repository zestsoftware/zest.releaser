import logging
import os
import sys

from ConfigParser import ConfigParser
from ConfigParser import NoSectionError
from ConfigParser import NoOptionError

try:
    from collective.dist import mupload
except ImportError:
    mupload = None

DIST_CONFIG_FILE = '.pypirc'

logger = logging.getLogger('pypi')


def collective_dist_available():
    """Return whether collective.dist is available"""
    if mupload is not None:
        return True
    return False


def new_distutils_available():
    """Return whether a recent enough python is available for multiple pypi"""
    if sys.version_info[:2] >= (2, 6):
        # 2.6 (or higher) does not need collective.dist: distutils includes
        # the needed functionality.
        return True
    return False


def multiple_pypi_support():
    """Return whether we can upload to multiple pypi servers"""
    if collective_dist_available() or new_distutils_available():
        return True
    return False


class PypiConfig(object):
    """Wrapper around the pypi config file"""

    def __init__(self, config_filename=DIST_CONFIG_FILE):
        """Grab the configuration (overridable for test purposes)"""
        self.config_filename = config_filename
        self._read_configfile()

    def _read_configfile(self):
        """Read the config file and store it (when valid)"""
        rc = self.config_filename
        if not os.path.isabs(rc):
            rc = os.path.join(os.path.expanduser('~'), self.config_filename)
        if not os.path.exists(rc):
            self.config = None
            return
        self.config = ConfigParser()
        self.config.read(rc)
        if (not self.is_old_pypi_config() and
            not self.is_new_pypi_config()):
            # Safety valve
            self.config = None

    def is_old_pypi_config(self):
        if self.config == None:
            return False
        try:
            self.config.get('server-login', 'username')
        except (NoSectionError, NoOptionError):
            return False
        return True

    def is_new_pypi_config(self):
        if not multiple_pypi_support():
            return False
        try:
            new = self.config.get('distutils', 'index-servers')
        except (NoSectionError, NoOptionError):
            return False
        return True

    def distutils_servers(self):
        """Return a list of known distutils servers for collective.dist.

        If the config has an old pypi config, remove the default pypi
        server from the list.
        """
        if not multiple_pypi_support():
            return []
        try:
            raw_index_servers = self.config.get('distutils', 'index-servers')
        except (NoSectionError, NoOptionError):
            return []
        ignore_servers = ['']
        if self.is_old_pypi_config():
            # We have already asked about uploading to pypi using the normal
            # upload.
            ignore_servers.append('pypi')
            # Yes, you can even have an old pypi config with a
            # [distutils] server list.
        index_servers = [
            server.strip() for server in raw_index_servers.split('\n')
            if server.strip() not in ignore_servers]
        return index_servers
