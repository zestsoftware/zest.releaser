from .utils import extract_zestreleaser_configparser
from configparser import ConfigParser
from configparser import NoOptionError
from configparser import NoSectionError

import logging
import os
import sys


try:
    # Python 3.11+
    import tomllib
except ImportError:
    # Python 3.10-
    import tomli as tomllib

DIST_CONFIG_FILE = ".pypirc"
SETUP_CONFIG_FILE = "setup.cfg"
PYPROJECTTOML_CONFIG_FILE = "pyproject.toml"
DEFAULT_REPOSITORY = "https://upload.pypi.org/legacy/"

logger = logging.getLogger(__name__)


class BaseConfig:
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
        """Get a text from the config."""
        result = default
        if self.config is not None:
            try:
                result = self.config.get(section, key, raw=raw)
            except (NoSectionError, NoOptionError, ValueError):
                return result
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
        self.config = ConfigParser(interpolation=None)
        self.config.read(self.config_filename)

    def has_bad_commands(self):
        if self.config is None:
            return False
        if not self.config.has_section("egg_info"):
            # bail out early as the main section is not there
            return False
        bad = False
        # Check 1.
        if self.config.has_option("egg_info", "tag_build"):
            # Might still be empty.
            value = self._get_text("egg_info", "tag_build")
            if value:
                logger.warning(
                    "%s has [egg_info] tag_build set to '%s'",
                    self.config_filename,
                    value,
                )
                bad = True
        # Check 2.
        if self.config.has_option("egg_info", "tag_svn_revision"):
            if self.config.getboolean("egg_info", "tag_svn_revision"):
                value = self._get_text("egg_info", "tag_svn_revision")
                logger.warning(
                    "%s has [egg_info] tag_svn_revision set to '%s'",
                    self.config_filename,
                    value,
                )
                bad = True
        return bad

    def fix_config(self):
        if not self.has_bad_commands():
            logger.warning("Cannot fix already fine %s.", self.config_filename)
            return
        if self.config.has_option("egg_info", "tag_build"):
            self.config.set("egg_info", "tag_build", "")
        if self.config.has_option("egg_info", "tag_svn_revision"):
            self.config.set("egg_info", "tag_svn_revision", "false")
        new_setup = open(self.config_filename, "w")
        try:
            self.config.write(new_setup)
        finally:
            new_setup.close()
        logger.info("New setup.cfg contents:")
        with open(self.config_filename) as config_file:
            print("".join(config_file.readlines()))

    def zest_releaser_config(self):
        return extract_zestreleaser_configparser(self.config, self.config_filename)


class PypiConfig(BaseConfig):
    """Wrapper around the pypi config file.

    Contains functions which return information about
    the pypi configuration.
    """

    def __init__(
        self, config_filename=DIST_CONFIG_FILE, omit_package_config_in_test=False
    ):
        """Grab the PyPI configuration.

        This is .pypirc in the home directory.  It is overridable for
        test purposes.

        We usually load PyPI config from setup.cfg as well.
        This can be switched off with omit_package_config_in_test=True.
        """
        self.config_filename = config_filename
        self.omit_package_config_in_test = omit_package_config_in_test
        self.reload()

    def reload(self):
        """Load the config.

        Do the initial load of the config.

        Or reload it in case of problems: this is needed when a pypi
        upload fails, you edit the .pypirc file to fix the account
        settings, and tell release to retry the command.
        """
        self._read_configfile()

    def zest_releaser_config(self):
        return extract_zestreleaser_configparser(self.config, self.config_filename)

    def _read_configfile(self):
        """Read the PyPI config file and store it (when valid).

        Possibly combine it with setup.cfg.
        This may override global .pypirc settings.
        """
        config_filename = self.config_filename
        if not os.path.exists(config_filename) and not os.path.isabs(config_filename):
            # When filename is .pypirc, we look in ~/.pypirc
            config_filename = os.path.join(os.path.expanduser("~"), config_filename)
        if not os.path.exists(config_filename):
            self.config = None
            return
        self.config = ConfigParser(interpolation=None)
        self.config.read(config_filename)
        if not self.omit_package_config_in_test:
            self.config.read(SETUP_CONFIG_FILE)

    def twine_repository(self):
        """Gets the repository from Twine environment variables."""
        return os.getenv("TWINE_REPOSITORY")

    def twine_repository_url(self):
        """Gets the repository URL from Twine environment variables."""
        return os.getenv("TWINE_REPOSITORY_URL")

    def is_pypi_configured(self):
        """Determine if we're configured to publish to 1+ PyPi server.

        PyPi is considered to be 'configued' if the TWINE_REPOSITORY_URL is set,
        or if we have a config which contains at least 1 PyPi server.
        """
        servers = len(self.distutils_servers()) > 0
        twine_url = self.twine_repository_url() is not None
        return any((servers, twine_url))

    def distutils_servers(self):
        """Return a list of known distutils servers.

        If the config has an old pypi config, remove the default pypi
        server from the list.
        """
        twine_repository = self.twine_repository()

        if twine_repository and self.config:
            # If there is no section we can't upload there
            if self.config.has_section(twine_repository):
                return [twine_repository]
            else:
                return []

        # If we don't have a config we can't continue
        if not self.config:
            return []

        try:
            index_servers = self._get_text(
                "distutils", "index-servers", default=""
            ).split()
        except (NoSectionError, NoOptionError):
            index_servers = []
        if not index_servers:
            # If no distutils index-servers have been given, 'pypi' should be
            # the default.  This is what twine does.
            if self.config.has_option("server-login", "username"):
                # We have a username, so upload to pypi should work fine, even
                # when no explicit pypi section is in the file.
                return ["pypi"]
            # https://github.com/zestsoftware/zest.releaser/issues/199
            index_servers = ["pypi"]
        # The servers all need to have a section in the config file.
        return [server for server in index_servers if self.config.has_section(server)]


class PyprojectTomlConfig(BaseConfig):
    """Wrapper around the pyproject.toml file if available.

    This is for optional zest.releaser-specific settings::

        [tool.zest-releaser]
        python-file-with-version = "reinout/maurits.py"


    """

    config_filename = PYPROJECTTOML_CONFIG_FILE

    def __init__(self):
        """Grab the configuration (overridable for test purposes)"""
        # If there is a pyproject.toml in the package, parse it
        if not os.path.exists(self.config_filename):
            self.config = None
            return
        with open(self.config_filename, "rb") as tomlconfig:
            self.config = tomllib.load(tomlconfig)

    def zest_releaser_config(self):
        if self.config is None:
            return None
        try:
            result = self.config["tool"]["zest-releaser"]
        except KeyError:
            logger.debug(
                f"No [tool.zest-releaser] section found in the {self.config_filename}"
            )
            return None
        return result


class ZestReleaserConfig:
    hooks_filename = None

    def load_configs(self, pypirc_config_filename=DIST_CONFIG_FILE):
        """Load configs from several files.

        The order is this:

        - ~/.pypirc
        - setup.cfg
        - pyproject.toml

        A later config file overwrites keys from an earlier config file.
        I think this order makes the most sense.
        Example: extra-message = [ci skip]
        What I expect, is:

        * Most packages won't have this setting.
        * If you make releases for lots of packages, you probably set this in
          your global ~/.pypirc.
        * A few individual packages will explicitly set this.
          They will expect this to have the effect that the extra message is
          added to commits, regardless of who makes a release.
          So this individual package setting should win.
        * Finally, pyproject.toml is newer than setup.cfg, so it makes sense
          that this file has the last say.
        """
        setup_config = SetupConfig()
        pypi_config = PypiConfig(config_filename=pypirc_config_filename)
        pyproject_config = PyprojectTomlConfig()
        combined_config = {}
        config_files = [pypi_config]
        if not self.omit_package_config_in_test:
            config_files.extend([setup_config, pyproject_config])
        for config in config_files:
            if config.zest_releaser_config() is not None:
                zest_config = config.zest_releaser_config()
                assert isinstance(zest_config, dict)
                combined_config.update(zest_config)

                # store which config file contained entrypoint hooks
                if any(
                    [
                        x
                        for x in zest_config.keys()
                        if x.lower().startswith(
                            ("prereleaser.", "releaser.", "postreleaser.")
                        )
                    ]
                ):
                    self.hooks_filename = config.config_filename
        self.config = combined_config

    def __init__(
        self, pypirc_config_filename=DIST_CONFIG_FILE, omit_package_config_in_test=False
    ):
        self.omit_package_config_in_test = omit_package_config_in_test
        self.load_configs(pypirc_config_filename=pypirc_config_filename)

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

        Either in your ~/.pypirc or in a setup.cfg or pyproject.toml in a specific
        package, add this when you want the default answer to this
        question to be 'no':

        [zest.releaser]
        release = no

        The default when this option has not been set is True.

        Standard config rules apply, so you can use upper or lower or
        mixed case and specify 0, false, no or off for boolean False,
        and 1, on, true or yes for boolean True.
        """
        return self.config.get("release", True)

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
        return self.config.get("extra-message")

    def prefix_message(self):
        """Return extra text to be added before the commit message.

        This can for example be used follow internal policies on commit messages.

        Enable this mode by adding a ``prefix-message`` option, either in the
        package you want to release, or in your ~/.pypirc::

            [zest.releaser]
            prefix-message = [TAG]
        """
        return self.config.get("prefix-message")

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
        # we were using an underscore at first
        result = self.config.get("history_file")
        # but if they're both defined, the hyphenated key takes precedence
        result = self.config.get("history-file", result)
        return result

    def python_file_with_version(self):
        """Return Python filename with ``__version__`` marker, if configured.

        Enable this by adding a ``python-file-with-version`` option::

            [zest-releaser]
            python-file-with-version = reinout/maurits.py

        Return None when nothing has been configured.

        """
        return self.config.get("python-file-with-version")

    def history_format(self):
        """Return the format to be used for Changelog files.

        Configure this by adding an ``history_format`` option, either in the
        package you want to release, or in your ~/.pypirc, and using ``rst`` for
        Restructured Text and ``md`` for Markdown::

            [zest.releaser]
            history_format = md
        """
        return self.config.get("history_format", "")

    def create_wheel(self):
        """Should we create a Python wheel for this package?

        This is next to the standard source distribution that we always create
        when releasing a Python package.

        Changed in version 8.0.0a2: we ALWAYS create a wheel,
        unless this is explicitly switched off.

        To switch this OFF, either in your ~/.pypirc or in a setup.cfg in
        a specific package, add this:

        [zest.releaser]
        create-wheel = no
        """
        return self.config.get("create-wheel", True)

    def upload_pypi(self):
        """Should we upload the package to Pypi?

        [Configure this mode by adding a ``upload-pypi`` option::

            [zest.releaser]
            upload-pypi = no

        The default when this option has not been set is True.

        """
        return self.config.get("upload-pypi", True)

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
        return self.config.get("register", False)

    def no_input(self):
        """Return whether the user wants to run in no-input mode.

        Enable this mode by adding a ``no-input`` option::

            [zest.releaser]
            no-input = yes

        The default when this option has not been set is False.
        """
        return self.config.get("no-input", False)

    def development_marker(self):
        """Return development marker to be appended in postrelease.

        Override the default ``.dev0`` in ~/.pypirc or setup.cfg using
        a ``development-marker`` option::

            [zest.releaser]
            development-marker = .dev1

        Returns default of ``.dev0`` when nothing has been configured.
        """
        return self.config.get("development-marker", ".dev0")

    def push_changes(self):
        """Return whether the user wants to push the changes to the remote.

        Configure this mode by adding a ``push-changes`` option::

            [zest.releaser]
            push-changes = no

        The default when this option has not been set is True.
        """
        return self.config.get("push-changes", True)

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
        return self.config.get("less-zeroes", False)

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
        result = self.config.get("version-levels", default)
        if result < 0:
            return default
        return result

    _tag_format_deprecated_message = "\n".join(
        line.strip()
        for line in """
    `tag-format` contains deprecated `%%(version)s` format. Please change to:

    [zest.releaser]
    tag-format = %s
    """.strip().splitlines()
    )

    def tag_format(self, version):
        """Return the formatted tag that should be used in the release.

        Configure it in ~/.pypirc or setup.cfg using a ``tag-format`` option::

            [zest.releaser]
            tag-format = v{version}

        ``tag-format`` must contain exactly one formatting instruction: for the
        ``version`` key.

        Accepts also ``%(version)s`` format for backward compatibility.

        The default format, when nothing has been configured, is ``{version}``.
        """
        default_fmt = "{version}"
        fmt = self.config.get("tag-format", default_fmt)
        if "{version}" in fmt:
            return fmt.format(version=version)
        # BBB:
        if "%(version)s" in fmt:
            proposed_fmt = fmt.replace("%(version)s", "{version}")
            print(self._tag_format_deprecated_message % proposed_fmt)
            return fmt % {"version": version}
        print("{version} needs to be part of 'tag-format': %s" % fmt)
        sys.exit(1)

    def tag_message(self, version):
        """Return the commit message to be used when tagging.

        Configure it in ~/.pypirc or setup.cfg using a ``tag-message``
        option::

            [zest.releaser]
            tag-message = Creating v{version} tag.

        ``tag-message`` must contain exactly one formatting
        instruction: for the ``version`` key.

        The default format is ``Tagging {version}``.
        """
        default_fmt = "Tagging {version}"
        fmt = self.config.get("tag-message", default_fmt)
        if "{version}" not in fmt:
            print("{version} needs to be part of 'tag-message': '%s'" % fmt)
            sys.exit(1)
        return fmt.format(version=version)

    def tag_signing(self):
        """Return whether the tag should be signed.

        Configure it in ~/.pypirc or setup.cfg using a ``tag-signing`` option::

            [zest.releaser]
            tag-signing = yes

        ``tag-signing`` must contain exactly one word which will be
        converted to a boolean. Currently are accepted (case
        insensitively): 0, false, no, off for False, and 1, true, yes,
        on for True).

        The default when this option has not been set is False.

        """
        return self.config.get("tag-signing", False)

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
        default = "%Y-%m-%d"
        try:
            result = self.config["date-format"].replace("%%", "%")
        except (KeyError, ValueError):
            return default
        return result

    def run_pre_commit(self):
        """Return whether we should run pre commit hooks.

        At least in git you have pre commit hooks.
        These may interfere with releasing:
        zest.releaser changes your setup.py, a pre commit hook
        runs black or isort and gives an error, so the commit is cancelled.
        By default (since version 7.3.0) we do not run pre commit hooks.

        Configure it in ~/.pypirc or setup.cfg using a ``tag-signing`` option::

            [zest.releaser]
            run-pre-commit = yes

        ``run-pre-commit`` must contain exactly one word which will be
        converted to a boolean. Currently are accepted (case
        insensitively): 0, false, no, off for False, and 1, true, yes,
        on for True).

        The default when this option has not been set is False.

        """
        return self.config.get("run-pre-commit", False)
