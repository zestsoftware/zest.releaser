# -*- coding: utf-8 -*-
from zest.releaser import utils
import logging
import os
import pkg_resources
import toml

# towncrier might become a conditional dependency of zest.releaser,
# for example in the recommended list.
# If we split this into a separate package, it should be a hard dependency.
try:
    pkg_resources.get_distribution('towncrier')
except pkg_resources.DistributionNotFound:
    HAS_TOWNCRIER = False
else:
    HAS_TOWNCRIER = True


logger = logging.getLogger('towncrier_hooks')
TOWNCRIER_MARKER = '_towncrier_applicable'
TOWNCRIER_CONFIG_FILE = 'pyproject.toml'


def load_config():
    fn = os.path.join(TOWNCRIER_CONFIG_FILE)
    if not os.path.exists(fn):
        return
    with open(fn, 'r') as conffile:
        config = toml.load(conffile)
    if 'tool' not in config:
        return
    config = config['tool']
    if 'towncrier' not in config:
        return
    config = config['towncrier']
    # Currently we need 'package' in the config.
    if 'package' not in config:
        logger.error(
            "The [tool.towncrier] section of %s "
            "has no required 'package' key.", TOWNCRIER_CONFIG_FILE)
        return
    return True


def _check_towncrier():
    # First check if the towncrier tool is available.
    # towncrier might be on the PATH but not importable or the other way around.
    # So could be tricky to know for sure that it is available.
    # Maybe call 'towncrier --help' and see if that gives an error.
    if not HAS_TOWNCRIER:
        return False
    # Read pyproject.toml with the toml package.
    if not load_config():
        return False
    return True


def check_towncrier(data):
    if TOWNCRIER_MARKER in data:
        # We have already been called.
        return data[TOWNCRIER_MARKER]
    if not data['update_history']:
        # Someone has instructed zest.releaser to not update the history,
        # and it was not us, because our marker was not set,
        # so we should not update the history either.
        logger.debug(
            'update_history is already False, so towncrier will not be run.')
        data[TOWNCRIER_MARKER] = False
        return False
    # Check if towncrier should be applied.
    result = _check_towncrier()
    if result:
        logger.debug('towncrier should be applied.')
        # zest.releaser should not update the history.
        # towncrier will do that.
        data['update_history'] = False
    else:
        logger.debug('towncrier cannot be applied.')
    data[TOWNCRIER_MARKER] = result
    return result


def call_towncrier(data):
    """Entrypoint: run towncrier when applicable."""
    if not check_towncrier(data):
        return
    cmd = ['towncrier', '--version', data['new_version'], '--yes']
    # We would like to pass ['--package' 'package name'] as well,
    # but that is not yet in a release of towncrier.
    logger.info(
        'Running command to update news: %s', utils.format_command(cmd))
    print(utils.execute_command(cmd))
    # towncrier stages the changes with git,
    # which BTW means that our plugin requires git.
    logger.info('The staged git changes are:')
    print(utils.execute_command(['git', 'diff', '--cached']))
    logger.info(
        'towncrier has finished updating the history file '
        'and has staged the above changes in git.')
