#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
   Tyrs

   @author:     Nicolas Paris <nicolas.caen@gmail.com>
   @version:    0.3.1-dev
   @date:       05/06/2011
   @licence:    GPLv3

'''
import utils
import config
import locale
import tweets
import argparse
import curses.wrapper
from keys import Keys
from update import UpdateThread 
from container import Container
from interface import Interface

locale.setlocale(locale.LC_ALL, '')
container =  Container()

def arguments ():
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

def main(scr):

    utils.set_console_title()
    init_tyrs()
    print 'Waiting for thread stopping...'
    return 0

def init_tyrs ():
    init_conf()
    init_api()
    init_inteface()
    init_thread()

def init_conf ():
    conf = config.Config(arguments())
    container.add('conf', conf)

def init_api ():
    api = tweets.Tweets()
    container.add('api', api)
    api.authentification()

def init_inteface ():
    user_interface = Interface()
    container.add ('interface', user_interface)

def init_thread ():
    update = UpdateThread()
    update.start()
    init_keys()
    update.stop()
    container['interface'].tear_down()

def init_keys ():
    Keys().handleKeyBinding()

def start ():
    curses.wrapper(main)

if __name__ == "__main__":
    start()
