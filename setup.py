from setuptools import setup, find_packages
import os

version = '2.3'

setup(name='zest.releaser',
      version=version,
      description="Scripts to help with releasing software with Zest's conventions",
      long_description=(open(os.path.join('zest',
                                          'releaser',
                                          'README.txt')).read() +
                        '\n\n' +
                        open(os.path.join('zest',
                                          'releaser',
                                          'TODO.txt')).read() +
                        '\n\n' +
                        open(os.path.join('zest',
                                          'releaser',
                                          'CREDITS.txt')).read() +
                        '\n\n' +
                        open(os.path.join('zest',
                                          'releaser',
                                          'HISTORY.txt')).read()),
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
    'console_scripts': ['release = zest.releaser.release:main',
                        'prerelease = zest.releaser.prerelease:main',
                        'postrelease = zest.releaser.postrelease:main',
                        'fullrelease = zest.releaser.fullrelease:main',
                        'longtest = zest.releaser.longtest:main',
                        'lasttagdiff = zest.releaser.lasttagdiff:main'],
    },
      )
