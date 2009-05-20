import logging
import os
import urllib

from ConfigParser import ConfigParser
from ConfigParser import NoSectionError
from ConfigParser import NoOptionError

try:
    from collective.dist import mupload
    mupload # Make pyflakes happy.
    collective_dist = True
except ImportError:
    collective_dist = False

index_servers = []
DIST_CONFIG_FILE = '.pypirc'

logger = logging.getLogger('pypi')


def package_in_pypi(package):
    """Check whether the package is registered on pypi"""
    url = 'http://pypi.python.org/simple/%s' % package
    result = urllib.urlopen(url).read().strip()
    if package in result:
        # Some link with the package name is present. If the package doesn't
        # exist on pypi, the result would be 'Not Found'.
        return True
    else:
        logger.debug("Package not found on pypi: %r", result)
        return False


def has_old_pypi_config(config):
    try:
        config.get('server-login', 'username')
    except (NoSectionError, NoOptionError):
        return False
    return True


def has_new_pypi_config(config):
    if not collective_dist:
        return False
    try:
        new = config.get('distutils', 'index-servers')
    except (NoSectionError, NoOptionError):
        return False
    return True


def get_pypi_config():
    rc = os.path.join(os.path.expanduser('~'), DIST_CONFIG_FILE)
    if not os.path.exists(rc):
        return None
    config = ConfigParser()
    config.read(rc)

    old = has_old_pypi_config(config)
    new = has_new_pypi_config(config)

    if not old and not new:
        return None
    return config


def get_distutils_servers(config):
    """Get a list of known distutils servers for use with collective.dist.

    If the config has an old pypi config, remove the default pypi
    server from the list.
    """
    if not collective_dist:
        return []
    try:
        raw_index_servers = config.get('distutils', 'index-servers')
    except (NoSectionError, NoOptionError):
        return []
    IGNORE_SERVERS = ['']
    if has_old_pypi_config(config):
        # We have already asked about uploading to pypi using the
        # normal upload.
        IGNORE_SERVERS.append('pypi')
    index_servers = [
        server.strip() for server in raw_index_servers.split('\n')
        if server.strip() not in IGNORE_SERVERS]
    return index_servers
