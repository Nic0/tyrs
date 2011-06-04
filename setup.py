#!/usr/bin/env python
# -*- coding:utf-8 -*-

from distutils.core import setup
import setuptools

setup(name='tyrs',
      version='0.1',
      description='Twitter and Identica client using curses',
      long_description=
      '''TODO''',

      author='Nicolas Paris',
      author_email='nicolas.caen@gmail.com',
      license='GPLv3',
      url='http://tyrs.nicosphere.net',
      install_requires=['twitter'],
      data_files= [('/usr/man/man1', ['doc/tyrs.1.gz'])],
      packages=['tyrs'],
      scripts=['scripts/tyrs'],
    )
