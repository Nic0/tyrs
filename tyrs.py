#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

##
#   Author:     Nicolas Paris <nicolas.caen@gmail.com>
#   Version:    0.01
#   Licence:    GPLv3
#

# custum import
import config
import uiTyrs
import tweets

def main():
    conf = config.Config()
    api = tweets.Tweets()
    api.authentification(conf)
    screen = uiTyrs.uiTyrs(api, conf)
    screen.displayHomeTimeline()
    return 0

if __name__ == "__main__":
    main()
