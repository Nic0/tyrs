# -*- coding:utf-8 -*-
'''
@module     keys
@author     Nicolas Paris <nicolas.caen@gmail.com
@licence    GPLv3
'''

import tyrs
import curses
from help import Help

class Keys:
    '''
    This class handle the main keysbinding, as the main method contain every
    keybinding, every case match a key to a method call, there is no logical
    here
    '''
    def __init__ (self):
        self.conf = tyrs.container['conf']
        self.interface = tyrs.container['interface']
        self.api = tyrs.container['api']

    def handleKeyBinding (self):
        '''Should have all keybinding handle here'''
        while True:

            ch = self.interface.screen.getch()

            if self.interface.resize_event:
                self.interface.resizeEvent()

            # Down and Up key must act as a menu, and should navigate
            # throught every tweets like an item.
            #

            # DOWN
            if ch == self.conf.keys['down'] or ch == curses.KEY_DOWN:
                self.interface.moveDown()
            # UP
            elif ch == self.conf.keys['up'] or ch == curses.KEY_UP:
                self.interface.moveUp()
            # LEFT
            elif ch == self.conf.keys['left'] or ch == curses.KEY_LEFT:
                self.interface.navigateBuffer(-1)
            # RIGHT
            elif ch == self.conf.keys['right'] or ch == curses.KEY_RIGHT:
                self.interface.navigateBuffer(+1)
            # TWEET
            elif ch == self.conf.keys['tweet']:
                self.api.tweet(None)
            # RETWEET
            elif ch == self.conf.keys['retweet']:
                self.api.retweet()
            # RETWEET AND EDIT
            elif ch == self.conf.keys['retweet_and_edit']:
                self.api.retweetAndEdit()
            # DELETE TwEET
            elif ch == self.conf.keys['delete']:
                self.api.delete()
            # MENTIONS
            elif ch == self.conf.keys['mentions']:
                self.interface.changeBuffer('mentions')
            # HOME TIMELINE
            elif ch == self.conf.keys['home']:
                self.interface.changeBuffer('home')
            # CLEAR
            elif ch == self.conf.keys['clear']:
                self.interface.clearStatuses()
            # UPDATE
            elif ch == self.conf.keys['update']:
                self.interface.updateTimeline(self.interface.buffer)
            # FOLLOW SELECTED
            elif ch == self.conf.keys['follow_selected']:
                self.api.followSelected()
            # UNFOLLOW SELECTED
            elif ch == self.conf.keys['unfollow_selected']:
                self.api.unfollowSelected()
            # FOLLOW
            elif ch == self.conf.keys['follow']:
                self.api.follow()
            # UNFOLLOW
            elif ch == self.conf.keys['unfollow']:
                self.api.unfollow()
            # OPENURL
            elif ch == self.conf.keys['openurl']:
                self.interface.openurl()
            # BACK ON TOP
            elif ch == self.conf.keys['back_on_top']:
                self.interface.changeBuffer(self.interface.buffer)
            # BACK ON BOTTOM
            elif ch == self.conf.keys['back_on_bottom']:
                self.interface.backOnBottom()
            # REPLY
            elif ch == self.conf.keys['reply']:
                self.api.reply()
            # GET DIRECT MESSAGE
            elif ch == self.conf.keys['getDM']:
                self.interface.changeBuffer('direct')
            # SEND DIRECT MESSAGE
            elif ch == self.conf.keys['sendDM']:
                self.api.sendDirectMessage()
            # SEARCH
            elif ch == self.conf.keys['search']:
                self.api.search()
            # SEARCH USER
            elif ch == self.conf.keys['search_user']:
                self.api.userTimeline()
            # SEARCH MYSELF
            elif ch == self.conf.keys['search_myself']:
                self.api.userTimeline(True)
            # Redraw screen
            elif ch == self.conf.keys['redraw']:
                self.interface.displayRedrawScreen()
            # Help
            elif ch == ord('?'):
                Help()
            # Create favorite
            elif ch == self.conf.keys['fav']:
                self.api.setFavorite()
            # Get favorite
            elif ch == self.conf.keys['get_fav']:
                self.api.getFavorites()
            # Destroy favorite
            elif ch == self.conf.keys['delete_fav']:
                self.api.destroyFavorite()
            # QUIT
            # 27 corresponding to the ESC, couldn't find a KEY_* corresponding
            elif ch == self.conf.keys['quit'] or ch == 27:
                break

            self.interface.displayTimeline()
