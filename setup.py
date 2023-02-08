from setuptools import find_packages
from setuptools import setup

import codecs
import sys


def read(filename):
    try:
        with codecs.open(filename, encoding="utf-8") as f:
            return f.read()
    except NameError:
        with open(filename, encoding="utf-8") as f:
            return f.read()


long_description = "\n\n".join(
    [read("README.rst"), read("CREDITS.rst"), read("CHANGES.rst")]
)

if sys.version_info < (3,):
    long_description = long_description.encode("utf-8")


setup(
    long_description=long_description,
    packages=find_packages(exclude=["ez_setup"]),
    namespace_packages=["zest"],
    include_package_data=True,
    zip_safe=False,
)
