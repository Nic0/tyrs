#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

##
#       Tyrs
#
#   Author:     Nicolas Paris <nicolas.caen@gmail.com>
#   Version:    0.01
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

    #while True:
        #update = threading.Timer(2.0, coin)
        #update.start()
        #time.sleep(2.0)

    interface.handleKeybinding()

    return 0

#def coin():
    #print 'coin'

if __name__ == "__main__":
    main()
