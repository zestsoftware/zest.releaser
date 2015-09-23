import codecs
import sys

from setuptools import find_packages
from setuptools import setup


version = '5.6'


def read(filename):
    try:
        with codecs.open(filename, encoding='utf-8') as f:
            return unicode(f.read())
    except NameError:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()



long_description = u'\n\n'.join([read('README.rst'),
                                 read('CREDITS.rst'),
                                 read('CHANGES.rst')])

if sys.version_info < (3,):
    long_description = long_description.encode('utf-8')


setup(name='zest.releaser',
      version=version,
      description="Software releasing made easy and repeatable",
      long_description=long_description,
      classifiers=[
          "Development Status :: 6 - Mature",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: Implementation :: CPython",
          "Programming Language :: Python :: Implementation :: PyPy",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords=['releasing', 'packaging', 'pypi'],
      author='Reinout van Rees',
      author_email='reinout@vanrees.org',
      url='http://zestreleaser.readthedocs.org',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zest'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'colorama',
          'six',
      ],
      extras_require={
          'recommended': [
              'chardet',
              'check-manifest',
              'pyroma',
              'readme >= 0.6',
              'wheel',
              'twine',
              ],
          'test': [
              'z3c.testsetup >= 0.8.4',
              'zope.testrunner',
              'wheel',
              ]},
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
              'preparedocs = ' +
              'zest.releaser.preparedocs:prepare_entrypoint_documentation',
              ],

          },
      )
