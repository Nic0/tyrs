#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
from distutils.core import setup

try:
    import setuptools
except ImportError:
    print 'The installation require setuptools, please install it \
    (python-setuptools or python-distribute)'

try:
    from DistUtilsExtra.command import *
except ImportError:
    print 'The installation require python-distutils-extra (apt-get install python-distutils-extra)' 
    print 'Or'
    print 'pip install http://launchpad.net/python-distutils-extra/trunk/2.28/+download/python-distutils-extra-2.28.tar.gz'

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='tyrs',
      version='0.5.0',
      description='Twitter and Identica client using curses',
      author='Nicolas Paris',
      author_email='nicolas.caen@gmail.com',
      url='http://tyrs.nicosphere.net',
      license='GPLv3',
      long_description=read('README.md'),
      install_requires=['python-twitter>=0.8.2', 'argparse', 'httplib2==0.6.0'],
      packages=['src', 'src.shorter'],
      scripts=['tyrs'],
      platforms=['linux'],
      classifiers = [
          'Development Status :: 4 - Beta',
          'Environment :: Console :: Curses',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2',
      ],
      cmdclass = { "build" : build_extra.build_extra,
                   "build_i18n" : build_i18n.build_i18n,
                 }
    )
