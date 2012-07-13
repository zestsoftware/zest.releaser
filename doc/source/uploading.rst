Uploading to pypi (or custom servers)
#####################################

Like noted earlier, for safety reasons zest.releaser will only offer to upload
your package to http://pypi.python.org when the package is already registered
there.  If this is not the case yet, you can go to the directory where
zest.releaser put the checkout (or make a fresh checkout yourself.  Then with
the python version of your choice do::

  python setup.py register sdist --formats=zip upload

For this to work you will need a ``.pypirc`` file in your home directory that
has your pypi login credentials like this::

  [server-login]
  username:maurits
  password:secret

Since python 2.6, or in earlier python versions with collective.dist, you can
specify multiple indexes for uploading your package in ``.pypirc``::

  [distutils]
  index-servers =
    pypi
    local

  [pypi]
  #pypi.python.org
  username:maurits
  password:secret

  [local]
  repository:http://localhost:8080/test/products/
  username:maurits
  password:secret
  # You may need to specify the realm, which is the domain the
  # server sends back when you do a challenge:
  #realm:Zope

See http://pypi.python.org/pypi/collective.dist for more info.

When all this is configured correctly, zest.releaser will first reregister and
upload at the official pypi (if the package is registered there already).
Then it will offer to upload to the other index servers that you have
specified in ``.pypirc``.

Note that since version 3.15, zest.releaser also looks for this information in
the setup.cfg if your package has that file.  One way to use this, is to
restrict the servers that zest.releaser will ask you upload to.  If you have
defined 40 index-servers in your pypirc but you have the following in your
setup.cfg, you will not be asked to upload to any server::

  [distutils]
  index-servers =

Note that after creating the tag we still ask you if you want to checkout that
tag for tweaks or pypi/distutils server upload.  We could add some extra
checks to see if that is really needed, but someone who does not have
index-servers listed, may still want to use an entry point like
`gocept.zestreleaser.customupload
<http://pypi.python.org/pypi/gocept.zestreleaser.customupload>`_ to do
uploading, or do some manual steps first before uploading.

Some people will hardly ever want to do a release on PyPI but in 99 out of 100
cases only want to create a tag.  They won't like the default answer of 'yes'
to that question of whether to create a checkout of the tag.  So since version
3.16 you can influence this default answer.  You can add some lines to the
``.pypirc`` file in your home directory to change the default answer for all
packages, or change it for individual packages in their ``setup.cfg`` file.
The lines are this::

  [zest.releaser]
  release = no

You can use no/false/off/0 or yes/true/on/1 as answers; upper, lower or mixed
case are all fine.
