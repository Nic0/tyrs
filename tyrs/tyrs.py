#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

##
#       Tyrs
#
#   Author:     Nicolas Paris <nicolas.caen@gmail.com>
#   Version:    0.0.1
#   Licence:    GPLv3
#

import config
import uiTyrs
import tweets
import time
import threading

def main():
    conf    = config.Config()
    api     = tweets.Tweets()
    api.authentification(conf)
    interface  = uiTyrs.uiTyrs(api, conf)
    interface.updateHomeTimeline()
    interface.displayHomeTimeline()

    update = UpdateThread(interface, conf)
    update.start()

    interface.handleKeybinding()
    update.stop()

    interface.tearDown()

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
            self.interface.updateHomeTimeline()
            self.interface.displayHomeTimeline()

    def stop (self):
        self._stopevent.set()

if __name__ == "__main__":
    main()
