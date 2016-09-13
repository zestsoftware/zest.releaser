from __future__ import unicode_literals

import codecs
import logging
import os

import pkg_resources
from six.moves.configparser import ConfigParser
from six.moves.configparser import NoSectionError
from six.moves.configparser import NoOptionError

try:
    pkg_resources.get_distribution('wheel')
except pkg_resources.DistributionNotFound:
    USE_WHEEL = False
else:
    USE_WHEEL = True
DIST_CONFIG_FILE = '.pypirc'
SETUP_CONFIG_FILE = 'setup.cfg'
DEFAULT_REPOSITORY = "https://upload.pypi.org/legacy/"

logger = logging.getLogger(__name__)


class SetupConfig(object):
    """Wrapper around the setup.cfg file if available.

    One reason is to cleanup setup.cfg from these settings::

        [egg_info]
        tag_build = dev
        tag_svn_revision = true

    Another is for optional zest.releaser-specific settings::

        [zest.releaser]
        python-file-with-version = reinout/maurits.py


    """

    config_filename = SETUP_CONFIG_FILE

    def __init__(self):
        """Grab the configuration (overridable for test purposes)"""
        # If there is a setup.cfg in the package, parse it
        if not os.path.exists(self.config_filename):
            self.config = None
            return
        self.config = ConfigParser()
        with codecs.open(self.config_filename, 'r', 'utf8') as fp:
            self.config.readfp(fp)

    def has_bad_commands(self):
        if self.config is None:
            return False
        if not self.config.has_section('egg_info'):
            # bail out early as the main section is not there
            return False
        bad = False
        # Check 1.
        if self.config.has_option('egg_info', 'tag_build'):
            # Might still be empty.
            value = self.config.get('egg_info', 'tag_build')
            if value:
                logger.warn("%s has [egg_info] tag_build set to %r",
                            self.config_filename, value)
                bad = True
        # Check 2.
        if self.config.has_option('egg_info', 'tag_svn_revision'):
            if self.config.getboolean('egg_info', 'tag_svn_revision'):
                value = self.config.get('egg_info', 'tag_svn_revision')
                logger.warn("%s has [egg_info] tag_svn_revision set to %r",
                            self.config_filename, value)
                bad = True
        return bad

    def fix_config(self):
        if not self.has_bad_commands():
            logger.warn("Cannot fix already fine %s.", self.config_filename)
            return
        if self.config.has_option('egg_info', 'tag_build'):
            self.config.set('egg_info', 'tag_build', '')
        if self.config.has_option('egg_info', 'tag_svn_revision'):
            self.config.set('egg_info', 'tag_svn_revision', 'false')
        new_setup = open(self.config_filename, 'w')
        try:
            self.config.write(new_setup)
        finally:
            new_setup.close()
        logger.info("New setup.cfg contents:")
        print(''.join(open(self.config_filename).readlines()))

    def python_file_with_version(self):
        """Return Python filename with ``__version__`` marker, if configured.

        Enable this by adding a ``python-file-with-version`` option::

            [zest.releaser]
            python-file-with-version = reinout/maurits.py

        Return None when nothing has been configured.

        """
        default = None
        if self.config is None:
            return default
        try:
            result = self.config.get(
                'zest.releaser',
                'python-file-with-version')
        except (NoSectionError, NoOptionError, ValueError):
            return default
        return result


class PypiConfig(object):
    """Wrapper around the pypi config file"""

    def __init__(self, config_filename=DIST_CONFIG_FILE, use_setup_cfg=True):
        """Grab the PyPI configuration.

        This is .pypirc in the home directory.  It is overridable for
        test purposes.

        If there is a setup.cfg file in the current directory, we read
        it too.
        """
        self.config_filename = config_filename
        self._read_configfile(use_setup_cfg=use_setup_cfg)

    def _read_configfile(self, use_setup_cfg=True):
        """Read the PyPI config file and store it (when valid).

        Usually read the setup.cfg too.
        """
        rc = self.config_filename
        if not os.path.isabs(rc):
            rc = os.path.join(os.path.expanduser('~'), self.config_filename)
        filenames = [rc]
        if use_setup_cfg:
            # If there is a setup.cfg in the package, parse it
            filenames.append('setup.cfg')
        files = [f for f in filenames if os.path.exists(f)]
        if not files:
            self.config = None
            return
        self.config = ConfigParser()
        for filename in files:
            with codecs.open(filename, 'r', 'utf8') as fp:
                self.config.readfp(fp)

    def is_pypi_configured(self):
        # Do we have configuration for releasing to at least one
        # pypi-compatible server?
        if self.config is None:
            return False
        if self.is_old_pypi_config():
            return True
        if self.is_new_pypi_config() and len(self.distutils_servers()) > 0:
            return True
        return False

    def is_old_pypi_config(self):
        if self.config is None:
            return False
        try:
            self.config.get('server-login', 'username')
        except (NoSectionError, NoOptionError):
            return False
        return True

    def is_new_pypi_config(self):
        try:
            self.config.get('distutils', 'index-servers')
        except (NoSectionError, NoOptionError):
            return False
        return True

    def get_server_config(self, server):
        """Get url, username, password for server.
        """
        repository_url = DEFAULT_REPOSITORY
        username = None
        password = None
        if self.config.has_section(server):
            if self.config.has_option(server, 'repository'):
                repository_url = self.config.get(server, 'repository')
            if self.config.has_option(server, 'username'):
                username = self.config.get(server, 'username')
            if self.config.has_option(server, 'password'):
                password = self.config.get(server, 'password')
        if not username and self.config.has_option('server-login', 'username'):
            username = self.config.get('server-login', 'username')
        if not password and self.config.has_option('server-login', 'password'):
            password = self.config.get('server-login', 'password')
        return {
            'repository_url': repository_url,
            'username': username,
            'password': password,
        }

    def distutils_servers(self):
        """Return a list of known distutils servers.

        If the config has an old pypi config, remove the default pypi
        server from the list.
        """
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

    def want_release(self):
        """Does the user normally want to release this package.

        Some colleagues find it irritating to have to remember to
        answer the question "Check out the tag (for tweaks or
        pypi/distutils server upload)" with the non-default 'no' when
        in 99 percent of the cases they just make a release specific
        for a customer, so they always answer 'no' here.  This is
        where an extra config option comes in handy: you can influence
        the default answer so you can just keep hitting 'Enter' until
        zest.releaser is done.

        Either in your ~/.pypirc or in a setup.cfg in a specific
        package, add this when you want the default answer to this
        question to be 'no':

        [zest.releaser]
        release = no

        The default when this option has not been set is True.

        Standard config rules apply, so you can use upper or lower or
        mixed case and specify 0, false, no or off for boolean False,
        and 1, on, true or yes for boolean True.
        """
        default = True
        if self.config is None:
            return default
        try:
            result = self.config.getboolean('zest.releaser', 'release')
        except (NoSectionError, NoOptionError, ValueError):
            return default
        return result

    def extra_message(self):
        """Return extra text to be added to commit messages.

        This can for example be used to skip CI builds.  This at least
        works for Travis.  See
        http://docs.travis-ci.com/user/how-to-skip-a-build/

        Enable this mode by adding a ``extra-message`` option, either in the
        package you want to release, or in your ~/.pypirc::

            [zest.releaser]
            extra-message = [ci skip]
        """
        default = ''
        if self.config is None:
            return default
        try:
            result = self.config.get('zest.releaser', 'extra-message')
        except (NoSectionError, NoOptionError, ValueError):
            return default
        return result

    def create_wheel(self):
        """Should we create a Python wheel for this package?

        Either in your ~/.pypirc or in a setup.cfg in a specific
        package, add this when you want to create a Python wheel, next
        to a standard sdist:

        [zest.releaser]
        create-wheel = yes

        """
        if not USE_WHEEL:
            # If the wheel package is not available, we obviously
            # cannot create wheels.
            return False
        default = False
        if self.config is None:
            return default
        try:
            result = self.config.getboolean('zest.releaser', 'create-wheel')
        except (NoSectionError, NoOptionError, ValueError):
            return default
        return result

    def no_input(self):
        """Return whether the user wants to run in no-input mode.

        Enable this mode by adding a ``no-input`` option::

            [zest.releaser]
            no-input = yes

        The default when this option has not been set is False.

        Standard config rules apply, so you can use upper or lower or
        mixed case and specify 0, false, no or off for boolean False,
        and 1, on, true or yes for boolean True.
        """
        default = False
        if self.config is None:
            return default
        try:
            result = self.config.getboolean('zest.releaser', 'no-input')
        except (NoSectionError, NoOptionError, ValueError):
            return default
        return result
