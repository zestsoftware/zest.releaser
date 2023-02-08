from setuptools import find_packages
from setuptools import setup


setup(
    packages=find_packages(),
    namespace_packages=["zest"],
    include_package_data=True,
    zip_safe=False,
)
