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
import utils
import config
import locale
import argparse
from update import *
import curses.wrapper
from tweets import Tweets
import keyBinding as keys
from container import Container
from uiTyrs import uiTyrs as ui

locale.setlocale(locale.LC_ALL, '')
container = Container()

def arguments ():

    parser = argparse.ArgumentParser('Tyrs: a twitter client writen in python with curses.')
    parser.add_argument('-a', '--account', help='Use another account, store in a different file.')
    parser.add_argument('-c', '--config', help='Use another configuration file.')
    parser.add_argument('-g', '--generate-config', help='Generate a default configuration file.')
    args = parser.parse_args()
    return args

def main(scr):

    utils.setConsoleTitle()
    initTyrs()
    print 'Waiting for thread stopping...'
    return 0

def initTyrs ():
    initConf()
    initApi()
    initUi()
    initThread()

def initConf ():
    global container
    conf = config.Config(arguments())
    container.add('conf', conf)

def initApi ():
    api     = Tweets(container)
    container.add('api', api)
    api.authentification()

def initUi ():
    interface = ui(container)
    container.add ('ui', interface)

def initThread ():
    update = UpdateThread(container)
    update.start()
    keybinding = keys.KeyBinding(container)
    keybinding.handleKeyBinding()
    update.stop()
    container['ui'].tearDown()

def start ():
    curses.wrapper(main)

if __name__ == "__main__":
    start()
