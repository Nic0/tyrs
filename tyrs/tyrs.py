#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
   Tyrs

   @author:     Nicolas Paris <nicolas.caen@gmail.com>
   @version:    0.2.0-dev
   @date:       20/05/2011
   @licence:    GPLv3

'''

import config
import uiTyrs
import tweets
import argparse
import threading
import keyBinding as keys
import curses.wrapper

import locale
locale.setlocale(locale.LC_ALL, '')

def arguments ():

    parser = argparse.ArgumentParser('Tyrs: a twitter client writen in python with curses')
    parser.add_argument('-a', '--account', help='Use another account, store in a different file')
    parser.add_argument('-c', '--config', help='Use another configuration file')
    args = parser.parse_args()
    return args

conf = config.Config(arguments())

def main(scr):


    api     = tweets.Tweets()
    api.authentification(conf)
    interface  = uiTyrs.uiTyrs(api, conf)

    update = UpdateThread(interface, conf)
    #refresh = RefreshThread(interface, conf)
    update.start()
    #refresh.start()
    keybinding = keys.KeyBinding(interface, conf, api)
    keybinding.handleKeyBinding()
    update.stop()
    #refresh.stop()
    interface.tearDown()
    print 'Waiting for thread stopping...'
    return 0

class UpdateThread (threading.Thread):

    def __init__ (self, interface, conf):
        self.interface = interface
        self.conf = conf
        threading.Thread.__init__(self, target=self.run)
        self._stopevent = threading.Event()


    def run (self):
        while not self._stopevent.isSet():
            self._stopevent.wait(self.conf.params_refresh * 60.0)
            if not self._stopevent.isSet():
                self.interface.updateHomeTimeline()
                self.interface.displayHomeTimeline()

    def stop (self):
        self._stopevent.set()

class RefreshThread (threading.Thread):

    def __init__ (self, interface, conf):
        self.interface = interface
        self.conf = conf
        threading.Thread.__init__(self, target=self.run)
        self._stopevent = threading.Event()


    def run (self):
        while not self._stopevent.isSet():
            self._stopevent.wait(2.0)
            if not self._stopevent.isSet():
                self.interface.updateHomeTimeline()
                self.interface.displayHomeTimeline()

    def stop (self):
        self._stopevent.set()

def start ():
    curses.wrapper(main)

if __name__ == "__main__":
    start()
