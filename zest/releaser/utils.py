# Small utility methods.
import logging
import os
import re
import sys
import urllib
from commands import getoutput

logger = logging.getLogger('utils')

WRONG_IN_VERSION = ['svn', 'dev', '(']

def loglevel():
    """Return DEBUG when -v is specified, INFO otherwise"""
    if len(sys.argv) > 1:
        if '-v' in sys.argv:
            return logging.DEBUG
    return logging.INFO


def strip_version(version):
    """Strip the version of all whitespace."""
    return version.strip().replace(' ', '')


def ask(question, default=True):
    """Ask the question in y/n form and return True/False.

    If you don't want a default 'yes', set default to None (or to False if you
    want a default 'no').

    """
    while True:
        yn = 'y/n'
        if default is True:
            yn = 'Y/n'
        if default is False:
            yn = 'y/N'
        print question + " (%s)?" % yn
        input = raw_input()
        if not input:
            if default is not None:
                return default
            print 'Please explicitly answer y/n'
            continue
        return 'y' in input.lower()


def fix_rst_heading(heading, below):
    """If the 'below' line looks like a reST line, give it the correct length.

    This allows for different characters being used as header lines.
    """
    if len(below) == 0:
        return below
    first = below[0]
    if first not in '-=`~':
        return below
    below = first * len(heading)
    return below


def cleanup_version(version):
    """Check if the version looks like a development version."""
    for w in WRONG_IN_VERSION:
        if version.find(w) != -1:
            logger.debug("Version indicates development: %s.", version)
            version = version[:version.find(w)].strip()
            logger.debug("Removing debug indicators: %r", version)
    return version


def extract_headings_from_history(history_lines):
    """Return list of dicts with version-like headers.

    We check for patterns like '2.10 (unreleased)', so with either
    'unreleased' or a date between parenthesis as that's the format we're
    using. Just fix up your first heading and you should be set.

    As an alternative, we support an alternative format used by some
    zope/plone paster templates: '2.10 - unreleased'

    """
    pattern = re.compile(r"""
    (?P<version>.+)  # Version string
    \(               # Opening (
    (?P<date>.+)     # Date
    \)               # Closing )
    \W*$             # Possible whitespace at end of line.
    """, re.VERBOSE)
    alt_pattern = re.compile(r"""
    ^                # Start of line
    (?P<version>.+)  # Version string
    \ -\             # space dash space
    (?P<date>.+)     # Date
    \W*$             # Possible whitespace at end of line.
    """, re.VERBOSE)
    headings = []
    line_number = 0
    for line in history_lines:
        match = pattern.search(line)
        alt_match = alt_pattern.search(line)
        if match:
            result = {'line': line_number,
                      'version': match.group('version').strip(),
                      'date': match.group('date'.strip())}
            headings.append(result)
            logger.debug("Found heading: %r", result)
        if alt_match:
            result = {'line': line_number,
                      'version': alt_match.group('version').strip(),
                      'date': alt_match.group('date'.strip())}
            headings.append(result)
            logger.debug("Found alternative heading: %r", result)
        line_number += 1
    return headings


def svn_info():
    """Return svn url"""
    our_info = getoutput('svn info')
    url = [line for line in our_info.split('\n')
           if 'URL:' in line][0]
    return url.replace('URL:', '').strip()


def base_from_svn():
    base = svn_info()
    for remove in ['trunk', 'tags', 'branches']:
        base = base.split(remove)[0]
    logger.debug("Base url is %s", base)
    return base


def extract_name_and_base(url):
    """Return name and base svn url from svn url."""
    base = url
    for remove in ['trunk', 'tags', 'branches']:
        base = base.split(remove)[0]
    logger.debug("Base url is %s", base)
    parts = base.split('/')
    parts = [part for part in parts if part]
    name = parts[-1]
    logger.debug("Name is %s", name)
    return name, base


def available_tags():
    """Return available tags."""
    base = base_from_svn()
    tag_info = getoutput('svn list %stags' % base)
    if "non-existent in that revision" in tag_info:
        print "tags dir does not exist at %s" % base + 'tags'
        if ask("Shall I create it"):
            cmd = 'svn mkdir %stags -m "Creating tags directory."' % (base)
            logger.info("Running %r", cmd)
            print getoutput(cmd)
            tag_info = getoutput('svn list %stags' % base)
        else:
            sys.exit(0)
    if 'Could not resolve hostname' in tag_info:
        logger.error('Network problem: %s', tag_info)
        sys.exit()
    tags = [line.replace('/', '') for line in tag_info.split('\n')]
    logger.debug("Available tags: %r", tags)
    return tags


def name_from_svn():
    base = base_from_svn()
    parts = base.split('/')
    parts = [p for p in parts if p]
    return parts[-1]


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

