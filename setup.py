from setuptools import setup, find_packages
import codecs
import os

version = '2.9.2dev'


def read(filename):
    filename = os.path.join('zest', 'releaser', filename)
    return unicode(codecs.open(filename, encoding='utf-8').read())


long_description = u'\n\n'.join([read('README.txt'),
                                 read('TODO.txt'),
                                 read('CREDITS.txt'),
                                 read('HISTORY.txt')])


setup(name='zest.releaser',
      version=version,
      description="Scripts to help with releasing software with Zest's conventions",
      long_description=long_description.encode('utf-8'),
      classifiers=[
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
      entry_points={
          'console_scripts': [
              'release = zest.releaser.release:main',
              'prerelease = zest.releaser.prerelease:main',
              'postrelease = zest.releaser.postrelease:main',
              'fullrelease = zest.releaser.fullrelease:main',
              'longtest = zest.releaser.longtest:main',
              'lasttagdiff = zest.releaser.lasttagdiff:main'],
          },
      )
