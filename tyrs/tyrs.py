#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
   Tyrs

   @author:     Nicolas Paris <nicolas.caen@gmail.com>
   @version:    0.1.2-dev
   @date:       11/05/2011
   @licence:    GPLv3

'''

import config
import uiTyrs
import tweets
import time
import signal
import threading

def main():
    conf    = config.Config()
    api     = tweets.Tweets()
    api.authentification(conf)
    interface  = uiTyrs.uiTyrs(api, conf)

    update = UpdateThread(interface, conf)
    update.start()
    interface.handleKeybinding()
    update.stop()
    print 'Waiting for thread stoping...'

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
            if not self._stopevent.isSet():
                self.interface.updateHomeTimeline()
                self.interface.displayHomeTimeline()

    def stop (self):
        self._stopevent.set()

if __name__ == "__main__":
    main()
