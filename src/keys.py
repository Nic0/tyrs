# -*- coding: utf-8 -*-
# Copyright © 2011 Nicolas Paris <nicolas.caen@gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import tyrs
import curses
from help import Help
from utils import open_image

class Keys(object):
    '''
    This class handle the main keysbinding, as the main method contain every
    keybinding, every case match a key to a method call, there is no logical
    here
    '''
    def __init__(self):
        self.conf       = tyrs.container['conf']
        self.interface  = tyrs.container['interface']
        self.api        = tyrs.container['api']

    def handleKeyBinding(self):
        '''Should have all keybinding handle here'''
        while True:

            if self.interface.resize_event:
                self.interface.handle_resize_event()
                self.interface.erase_flash_message()
                self.interface.display_timeline()

            ch = self.interface.screen.getch()

            # DOWN
            if ch == self.conf.keys['down'] or ch == curses.KEY_DOWN:
                self.interface.move_down()
            # UP
            elif ch == self.conf.keys['up'] or ch == curses.KEY_UP:
                self.interface.move_up()
            # LEFT
            elif ch == self.conf.keys['left'] or ch == curses.KEY_LEFT:
                self.interface.navigate_buffer(-1)
            # RIGHT
            elif ch == self.conf.keys['right'] or ch == curses.KEY_RIGHT:
                self.interface.navigate_buffer(+1)
            # TWEET
            elif ch == self.conf.keys['tweet']:
                self.api.tweet()
            # RETWEET
            elif ch == self.conf.keys['retweet']:
                self.api.retweet()
            # RETWEET AND EDIT
            elif ch == self.conf.keys['retweet_and_edit']:
                self.api.retweet_and_edit()
            # DELETE TwEET
            elif ch == self.conf.keys['delete']:
                self.api.destroy()
            # MENTIONS
            elif ch == self.conf.keys['mentions']:
                self.interface.change_buffer('mentions')
            # HOME TIMELINE
            elif ch == self.conf.keys['home']:
                self.interface.change_buffer('home')
            # CLEAR
            elif ch == self.conf.keys['clear']:
                self.interface.clear_statuses()
            # UPDATE
            elif ch == self.conf.keys['update']:
                self.api.update_timeline(self.interface.buffer)
            # FOLLOW SELECTED
            elif ch == self.conf.keys['follow_selected']:
                self.api.follow_selected()
            # UNFOLLOW SELECTED
            elif ch == self.conf.keys['unfollow_selected']:
                self.api.unfollow_selected()
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
                self.interface.back_on_top()
            # BACK ON BOTTOM
            elif ch == self.conf.keys['back_on_bottom']:
                self.interface.back_on_bottom()
            # REPLY
            elif ch == self.conf.keys['reply']:
                self.api.reply()
            # GET DIRECT MESSAGE
            elif ch == self.conf.keys['getDM']:
                self.interface.change_buffer('direct')
            # SEND DIRECT MESSAGE
            elif ch == self.conf.keys['sendDM']:
                self.api.direct_message()
            # SEARCH
            elif ch == self.conf.keys['search']:
                self.api.search()
            # SEARCH USER
            elif ch == self.conf.keys['search_user']:
                self.api.find_public_timeline()
            # SEARCH MYSELF
            elif ch == self.conf.keys['search_myself']:
                self.api.my_public_timeline()
            elif ch == self.conf.keys['search_current_user']:
                self.api.find_current_public_timeline()
            # Redraw screen
            elif ch == self.conf.keys['redraw']:
                self.interface.display_redraw_screen()
            # Help
            elif ch == ord('?'):
                Help()
            # Create favorite
            elif ch == self.conf.keys['fav']:
                self.api.set_favorite()
            # Get favorite
            elif ch == self.conf.keys['get_fav']:
                self.api.get_favorites()
            # Destroy favorite
            elif ch == self.conf.keys['delete_fav']:
                self.api.destroy_favorite()
            # Thread
            elif ch == self.conf.keys['thread']:
                self.api.get_thread()
            # Open image
            elif ch == self.conf.keys['open_image']:
                open_image(self.interface.current_status().user)
            # User info
            elif ch == ord('i'):
                self.interface.current_user_info()
            elif ch == self.conf.keys['waterline']:
                self.interface.update_last_read_home()
                self.interface.back_on_top()
            # QUIT
            elif ch == self.conf.keys['quit']:
                self.interface.stoped = True
                break
            else:
                continue

            self.interface.erase_flash_message()
            self.interface.display_timeline()
