from __future__ import unicode_literals

import logging
import os
import sys

import pkg_resources
from six import text_type
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


class BaseConfig(object):
    """Base config class with a few helper methods."""

    def __init__(self):
        self.config = None

    def _get_boolean(self, section, key, default=False):
        """Get a boolean from the config.

        Standard config rules apply, so you can use upper or lower or
        mixed case and specify 0, false, no or off for boolean False,
        and 1, on, true or yes for boolean True.
        """
        result = default
        if self.config is not None:
            try:
                result = self.config.getboolean(section, key)
            except (NoSectionError, NoOptionError, ValueError):
                return result
        return result

    def _get_text(self, section, key, default=None, raw=False):
        """Get a text from the config.

        We want unicode, also on Python 2.
        In Python 3 this is already the case.
        """
        result = default
        if self.config is not None:
            try:
                result = self.config.get(section, key, raw=raw)
            except (NoSectionError, NoOptionError, ValueError):
                return result
            if not isinstance(result, text_type):
                result = result.decode('utf-8')
        return result


class SetupConfig(BaseConfig):
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
        self.config.read(self.config_filename)

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
            value = self._get_text('egg_info', 'tag_build')
            if value:
                logger.warning("%s has [egg_info] tag_build set to '%s'",
                               self.config_filename, value)
                bad = True
        # Check 2.
        if self.config.has_option('egg_info', 'tag_svn_revision'):
            if self.config.getboolean('egg_info', 'tag_svn_revision'):
                value = self._get_text('egg_info', 'tag_svn_revision')
                logger.warning("%s has [egg_info] tag_svn_revision set to '%s'",
                               self.config_filename, value)
                bad = True
        return bad

    def fix_config(self):
        if not self.has_bad_commands():
            logger.warning("Cannot fix already fine %s.", self.config_filename)
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
        with open(self.config_filename) as config_file:
            print(''.join(config_file.readlines()))

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
            result = self._get_text(
                'zest.releaser',
                'python-file-with-version',
                default=default)
        except (NoSectionError, NoOptionError, ValueError):
            return default
        return result


class PypiConfig(BaseConfig):
    """Wrapper around the pypi config file"""

    def __init__(self, config_filename=DIST_CONFIG_FILE, use_setup_cfg=True):
        """Grab the PyPI configuration.

        This is .pypirc in the home directory.  It is overridable for
        test purposes.

        If there is a setup.cfg file in the current directory, we read
        it too.
        """
        self.config_filename = config_filename
        self.use_setup_cfg = use_setup_cfg
        self.reload()

    def reload(self):
        """Load the config.

        Do the initial load of the config.

        Or reload it in case of problems: this is needed when a pypi
        upload fails, you edit the .pypirc file to fix the account
        settings, and tell release to retry the command.
        """
        self._read_configfile(use_setup_cfg=self.use_setup_cfg)

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
        self.config.read(files)

    def is_pypi_configured(self):
        # Do we have configuration for releasing to at least one
        # pypi-compatible server?
        if self.config is None:
            return False
        return len(self.distutils_servers()) > 0

    def get_server_config(self, server):
        """Get url, username, password for server.
        """
        repository_url = DEFAULT_REPOSITORY
        username = None
        password = None
        if self.config.has_section(server):
            if self.config.has_option(server, 'repository'):
                repository_url = self._get_text(server, 'repository')
            if self.config.has_option(server, 'username'):
                username = self._get_text(server, 'username')
            if self.config.has_option(server, 'password'):
                password = self._get_text(server, 'password', raw=True)
        if not username and self.config.has_option('server-login', 'username'):
            username = self._get_text('server-login', 'username')
        if not password and self.config.has_option('server-login', 'password'):
            password = self._get_text('server-login', 'password', raw=True)
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
            index_servers = self._get_text(
                'distutils', 'index-servers', default='').split()
        except (NoSectionError, NoOptionError):
            index_servers = []
        if not index_servers:
            # If no distutils index-servers have been given, 'pypi' should be
            # the default.  This is what twine does.
            if self.config.has_option('server-login', 'username'):
                # We have a username, so upload to pypi should work fine, even
                # when no explicit pypi section is in the file.
                return ['pypi']
            # https://github.com/zestsoftware/zest.releaser/issues/199
            index_servers = ['pypi']
        # The servers all need to have a section in the config file.
        return [server for server in index_servers
                if self.config.has_section(server)]

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
        return self._get_boolean('zest.releaser', 'release', default=True)

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
            result = self._get_text(
                'zest.releaser', 'extra-message', default=default)
        except (NoSectionError, NoOptionError, ValueError):
            return default
        return result

    def history_file(self):
        """Return path of history file.

        Usually zest.releaser can find the correct one on its own.
        But sometimes it may not find anything, or it finds multiple
        and selects the wrong one.

        Configure this by adding a ``history-file`` option, either in the
        package you want to release, or in your ~/.pypirc::

            [zest.releaser]
            history-file = deep/down/historie.doc
        """
        default = ''
        if self.config is None:
            return default
        marker = object()
        try:
            result = self._get_text(
                'zest.releaser', 'history-file', default=marker)
        except (NoSectionError, NoOptionError, ValueError):
            return default
        if result == marker:
            # We were reading an underscore instead of a dash at first.
            try:
                result = self._get_text(
                    'zest.releaser', 'history_file', default=default)
            except (NoSectionError, NoOptionError, ValueError):
                return default
        return result

    def encoding(self):
        """Return encoding to use for text files.

        Mostly the changelog and if needed `setup.py`.

        The encoding cannot always be determined correctly.
        This setting is a way to fix that.
        See https://github.com/zestsoftware/zest.releaser/issues/264

        Configure this by adding an ``encoding`` option, either in the
        package you want to release, or in your ~/.pypirc::

            [zest.releaser]
            encoding = utf-8
        """
        default = ''
        if self.config is None:
            return default
        try:
            result = self._get_text(
                'zest.releaser', 'encoding', default=default, raw=True)
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

        If there is no setting for ``create-wheel``, then if there is a
        ``[bdist_wheel]`` section, it is treated as if
        ``create-wheel`` was true.  We used to look at the value of
        the ``universal`` option, but that no longer matters.
        This will still create a wheel:

        [bdist_wheel]
        universal = 0

        See https://github.com/zestsoftware/zest.releaser/issues/315
        """
        if not USE_WHEEL:
            # If the wheel package is not available, we obviously
            # cannot create wheels.
            return False
        create_setting = self._get_boolean(
            'zest.releaser', 'create-wheel', None)
        if create_setting is not None:
            # User specified this setting, it overrides
            # inferring from bdist_wheel
            return create_setting
        # No zest.releaser setting, are they asking for a universal wheel?
        # Then they want wheels in general.
        return self.config.has_section('bdist_wheel')

    def register_package(self):
        """Should we try to register this package with a package server?

        For the standard Python Package Index (PyPI), registering a
        package is no longer needed: this is done automatically when
        uploading a distribution for a package.  In fact, trying to
        register may fail.  See
        https://github.com/zestsoftware/zest.releaser/issues/191
        So by default zest.releaser will no longer register a package.

        But you may be using your own package server, and registering
        may be wanted or even required there.  In this case
        you will need to turn on the register function.
        In your setup.cfg or ~/.pypirc, use the following to ensure that
        register is called on the package server:

        [zest.releaser]
        register = yes

        Note that if you have specified multiple package servers, this
        option is used for all of them.  There is no way to register and
        upload to server A, and only upload to server B.
        """
        return self._get_boolean('zest.releaser', 'register')

    def no_input(self):
        """Return whether the user wants to run in no-input mode.

        Enable this mode by adding a ``no-input`` option::

            [zest.releaser]
            no-input = yes

        The default when this option has not been set is False.
        """
        return self._get_boolean('zest.releaser', 'no-input')

    def development_marker(self):
        """Return development marker to be appended in postrelease.

        Override the default ``.dev0`` in ~/.pypirc or setup.cfg using
        a ``development-marker`` option::

            [zest.releaser]
            development-marker = .dev1

        Returns default of ``.dev0`` when nothing has been configured.
        """
        default = '.dev0'
        if self.config is None:
            return default
        try:
            result = self._get_text(
                'zest.releaser', 'development-marker', default=default)
        except (NoSectionError, NoOptionError, ValueError):
            return default
        return result

    def push_changes(self):
        """Return whether the user wants to push the changes to the remote.

        Configure this mode by adding a ``push-changes`` option::

            [zest.releaser]
            push-changes = no

        The default when this option has not been set is True.
        """
        return self._get_boolean('zest.releaser', 'push-changes', default=True)

    def less_zeroes(self):
        """Return whether the user prefers less zeroes at the end of a version.

        Configure this mode by adding a ``less-zeroes`` option::

            [zest.releaser]
            less-zeroes = yes

        The default when this option has not been set is False.

        When set to true:
        - Instead of 1.3.0 we will suggest 1.3.
        - Instead of 2.0.0 we will suggest 2.0.

        This only makes sense for the bumpversion command.
        In the postrelease command we read this option too,
        but with the current logic it has no effect there.
        """
        return self._get_boolean('zest.releaser', 'less-zeroes')

    def version_levels(self):
        """How many levels does the user prefer in a version number?

        Configure this mode by adding a ``version-levels`` option::

            [zest.releaser]
            version-levels = 3

        The default when this option has not been set is 0, which means:
        no preference, so use the length of the current number.

        This means when suggesting a next version after 1.2:
        - with levels=0 we will suggest 1.3: no change
        - with levels=1 we will still suggest 1.3, as we will not
          use this to remove numbers, only to add them
        - with levels=2 we will suggest 1.3
        - with levels=3 we will suggest 1.2.1

        If the current version number has more levels, we keep them.
        So next version for 1.2.3.4 with levels=1 is 1.2.3.5.

        Tweaking version-levels and less-zeroes should give you the
        version number strategy that you prefer.
        """
        default = 0
        if self.config is None:
            return default
        try:
            result = self.config.getint('zest.releaser', 'version-levels')
        except (NoSectionError, NoOptionError, ValueError):
            return default
        if result < 0:
            return default
        return result

    _tag_format_deprecated_message = "\n".join(line.strip() for line in """
    `tag-format` contains deprecated `%%(version)s` format. Please change to:

    [zest.releaser]
    tag-format = %s
    """.strip().splitlines())

    def tag_format(self, version):
        """Return the formatted tag that should be used in the release.

        Configure it in ~/.pypirc or setup.cfg using a ``tag-format`` option::

            [zest.releaser]
            tag-format = v{version}

        ``tag-format`` must contain exaclty one formatting instruction: for the
        ``version`` key.

        Accepts also ``%(version)s`` format for backward compatibility.

        The default format, when nothing has been configured, is ``{version}``.
        """
        fmt = '{version}'
        if self.config is not None:
            try:
                fmt = self._get_text(
                    'zest.releaser', 'tag-format', default=fmt, raw=True)
            except (NoSectionError, NoOptionError, ValueError):
                pass
        if '{version}' in fmt:
            return fmt.format(version=version)
        # BBB:
        if '%(version)s' in fmt:
            proposed_fmt = fmt.replace("%(version)s", "{version}")
            print(self._tag_format_deprecated_message % proposed_fmt)
            return fmt % {'version': version}
        print("{version} needs to be part of 'tag-format': %s" % fmt)
        sys.exit(1)

    def tag_message(self, version):
        """Return the commit message to be used when tagging.

        Configure it in ~/.pypirc or setup.cfg using a ``tag-message``
        option::

            [zest.releaser]
            tag-message = Creating v{version} tag.

        ``tag-message`` must contain exaclty one formatting
        instruction: for the ``version`` key.

        The default format is ``Tagging {version}``.
        """
        fmt = 'Tagging {version}'
        if self.config:
            try:
                fmt = self._get_text(
                    'zest.releaser', 'tag-message', default=fmt, raw=True)
            except (NoSectionError, NoOptionError, ValueError):
                pass
        if '{version}' not in fmt:
            print("{version} needs to be part of 'tag-message': '%s'" % fmt)
            sys.exit(1)
        return fmt.format(version=version)

    def tag_signing(self):
        """Return whether the tag should be signed.

        Configure it in ~/.pypirc or setup.cfg using a ``tag-signing`` option::

            [zest.releaser]
            tag-signing = yes

        ``tag-signing`` must contain exaclty one word which will be
        converted to a boolean. Currently are accepted (case
        insensitively): 0, false, no, off for False, and 1, true, yes,
        on for True).

        The default when this option has not been set is False.

        """
        return self._get_boolean('zest.releaser', 'tag-signing', default=False)

    def date_format(self):
        """Return the string format for the date used in the changelog.

        Override the default ``%Y-%m-%d`` in ~/.pypirc or setup.cfg using
        a ``date-format`` option::

            [zest.releaser]
            date-format = %%B %%e, %%Y

        Note: the % signs should be doubled for compatibility with other tools
        (i.e. pip) that parse setup.cfg using the interpolating ConfigParser.

        Returns default of ``%Y-%m-%d`` when nothing has been configured.
        """
        default = '%Y-%m-%d'
        if self.config is None:
            return default
        try:
            result = self._get_text(
                'zest.releaser', 'date-format', default=default
            ).replace('%%', '%')
        except (NoSectionError, NoOptionError, ValueError):
            return default
        return result
