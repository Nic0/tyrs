# -*- coding: utf-8 -*-
'''
   @module   utils 
   @author   Nicolas Paris <nicolas.caen@gmail.com>
   @license  GPLv3
'''

def set_console_title():
    try:
        sys.stdout.write("\x1b]2;Tyrs\x07")
    except:
        pass

