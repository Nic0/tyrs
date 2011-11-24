#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2011 Nicolas Paris <nicolas.caen@gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
   Tyrs

   @author:     Nicolas Paris <nicolas.caen@gmail.com>
   @version:    0.6.0-dev
   @date:       06/11/2011
   @licence:    GPLv3

'''

import sys
import utils
import config
import locale
import tweets
import argparse
import gettext
from urllib2 import URLError
from timeline import Timeline
from container import Container
from interface import Interface

locale.setlocale(locale.LC_ALL, '')
container =  Container()

def arguments():
    '''
    Parse all arguments from the CLI
    '''
    parser = argparse.ArgumentParser(
            'Tyrs: a twitter client writen in python with curses.')
    parser.add_argument('-a', '--account',
            help='Use another account, store in a different file.')
    parser.add_argument('-c', '--config',
            help='Use another configuration file.')
    parser.add_argument('-g', '--generate-config',
            help='Generate a default configuration file.')
    args = parser.parse_args()
    return args

def main():

    utils.set_console_title()
    init_conf()
    init_tyrs()

def init_tyrs():
    init_timelines()
    init_api()
    init_interface()

def init_conf():
    conf = config.Config(arguments())
    container.add('conf', conf)


def init_api():
    api = tweets.Tweets()
    container.add('api', api)
    try:
        api.authentication()
    except URLError, e:
        print 'error:%s' % e
        sys.exit(1)

def init_interface():
    user_interface = Interface()
    container.add('interface', user_interface)

def init_timelines():
    buffers = (
        'home', 'mentions', 'direct', 'search',
        'user', 'favorite', 'thread', 'user_retweet'
    )
    timelines = {}
    for buff in buffers:
        timelines[buff] = Timeline()
    container.add('timelines', timelines)
    container.add('buffers', buffers)

if __name__ == "__main__":
    gettext.install('tyrs', unicode=1)
    main()
