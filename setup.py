from setuptools import setup, find_packages
import codecs
import os

version = '2.12'


# Adapted from
# http://stackoverflow.com/questions/1162338/whats-the-right-way-to-use-unicode-metadata-in-setup-py
class UltraMagicString(object):
    # Catch-22:
    # - if I return Unicode, python setup.py --long-description as well
    #   as python setup.py upload fail with a UnicodeEncodeError
    # - if I return UTF-8 string, python setup.py sdist register
    #   fails with an UnicodeDecodeError

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def __unicode__(self):
        return self.value.decode('utf-8')

    def __add__(self, other):
        return UltraMagicString(self.value + str(other))

    def split(self, *args, **kw):
        return self.value.split(*args, **kw)


def read(filename):
    filename = os.path.join('zest', 'releaser', filename)
    return unicode(codecs.open(filename, encoding='utf-8').read())


def read_from_here(filename):
    return unicode(codecs.open(filename, encoding='utf-8').read())


long_description = u'\n\n'.join([read('README.txt'),
                                 read('TODO.txt'),
                                 read('CREDITS.txt'),
                                 read_from_here('CHANGES.txt')])


setup(name='zest.releaser',
      version=version,
      description="Software releasing made easy and repeatable",
      long_description=UltraMagicString(long_description.encode('utf-8')),
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
      extras_require={
          'test': ['z3c.testsetup']},
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
