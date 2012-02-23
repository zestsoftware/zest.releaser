from setuptools import setup, find_packages
import codecs
import os

version = '3.31'


def read(filename):
    filename = os.path.join('zest', 'releaser', filename)
    return unicode(codecs.open(filename, encoding='utf-8').read())


def read_from_here(filename):
    return unicode(codecs.open(filename, encoding='utf-8').read())


long_description = '\n\n'.join([read('README.txt'),
                                read('entrypoints.txt'),
                                read('TODO.txt'),
                                read('CREDITS.txt'),
                                read_from_here('CHANGES.txt')])

setup(name='zest.releaser',
      version=version,
      description="Software releasing made easy and repeatable",
      long_description=long_description,
      classifiers=[
        "Development Status :: 6 - Mature",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Reinout van Rees',
      author_email='reinout@vanrees.org',
      url='http://pypi.python.org/pypi/zest.releaser',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zest'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      extras_require={
          'test': ['z3c.testsetup']},
      entry_points={
          'console_scripts': [
              'release = zest.releaser.release:main',
              'prerelease = zest.releaser.prerelease:main',
              'postrelease = zest.releaser.postrelease:main',
              'fullrelease = zest.releaser.fullrelease:main',
              'longtest = zest.releaser.longtest:main',
              'lasttagdiff = zest.releaser.lasttagdiff:main',
              'lasttaglog = zest.releaser.lasttaglog:main',
              ],
          # The datachecks are implemented as entry points to be able to check
          # our entry point implementation.
          'zest.releaser.prereleaser.middle': [
              'datacheck = zest.releaser.prerelease:datacheck',
              ],
          'zest.releaser.releaser.middle': [
              'datacheck = zest.releaser.release:datacheck',
              ],
          'zest.releaser.postreleaser.middle': [
              'datacheck = zest.releaser.postrelease:datacheck',
              ],
          # Documentation generation
          'zest.releaser.prereleaser.before': [
              'datacheck = zest.releaser.utils:prepare_documentation_entrypoint',
              ],

          },
      )
