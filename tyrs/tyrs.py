#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
   Tyrs

   @author:     Nicolas Paris <nicolas.caen@gmail.com>
   @version:    0.3.1-dev
   @date:       05/06/2011
   @licence:    GPLv3

'''
import sys
import config
from uiTyrs import uiTyrs as ui
import argparse
import keyBinding as keys
from tweets import Tweets
from container import Container
from update import *
import utils
import curses.wrapper

import locale
locale.setlocale(locale.LC_ALL, '')

def arguments ():

    parser = argparse.ArgumentParser('Tyrs: a twitter client writen in python with curses.')
    parser.add_argument('-a', '--account', help='Use another account, store in a different file.')
    parser.add_argument('-c', '--config', help='Use another configuration file.')
    parser.add_argument('-g', '--generate-config', help='Generate a default configuration file.')
    args = parser.parse_args()
    return args

container = Container()
conf = config.Config(arguments())
container.add('conf', conf)

def setTitle ():
    try:
        sys.stdout.write("\x1b]2;Tyrs\x07")
    except:
        pass

def main(scr):

    utils.setConsoleTitle()
    api     = Tweets(container)
    container.add('api', api)
    api.authentification()
    interface  = ui(container)
    container.add('ui', interface)
    update = UpdateThread(container)
    update.start()
    keybinding = keys.KeyBinding(container)
    keybinding.handleKeyBinding()
    update.stop()
    interface.tearDown()
    print 'Waiting for thread stopping...'
    return 0

def start ():
    curses.wrapper(main)

if __name__ == "__main__":
    start()
