#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from distutils.core import setup
try:    
    from DistUtilsExtra.command import *
except ImportError:
    print 'The installation require python-distutils-extra (apt-get install \
    python-distutils-extra'
try:
    import setuptools
except ImportError:
    print 'The installation require setuptools, please install it \
    (python-setuptools or python-distribute).'
    sys.exit(0)

setup(name='tyrs',
      version='0.1',
      description='Twitter and Identica client using curses',
      long_description=
      '''TODO''',

      author='Nicolas Paris',
      author_email='nicolas.caen@gmail.com',
      license='GPLv3',
      url='http://tyrs.nicosphere.net',
      install_requires=['python-twitter>=0.8.2' 'argsparse'],
      data_files= [
          ('/usr/man/man1', ['doc/tyrs.1.gz']),
      ],
      packages=['tyrs'],
      scripts=['scripts/tyrs'],

      cmdclass = { "build" :  build_extra.build_extra,
                   "build_i18n" :  build_i18n.build_i18n,
                 }
    )
