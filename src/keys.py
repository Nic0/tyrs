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
import urwid
from help import Help
from utils import open_image

class Keys(object):

    __metaclass__ = urwid.signals.MetaSignals
    signals = ['help_done']
    '''
    This class handle the main keysbinding, as the main method contain every
    keybinding, every case match a key to a method call, there is no logical
    here
    '''
    def __init__(self):
        self.conf       = tyrs.container['conf']
        self.interface  = tyrs.container['interface']
        self.api        = tyrs.container['api']

    def keystroke (self, ch):
        if not self.interface.help:
# Quit
            if ch == self.conf.keys['quit']:
                self.interface.stoped = True
                raise urwid.ExitMainLoop()
# Right
            elif ch == self.conf.keys['right'] or ch == 'right':
                self.interface.navigate_buffer(+1)
# left
            elif ch == self.conf.keys['left'] or ch == 'left':
                self.interface.navigate_buffer(-1)
# Update
            elif ch == self.conf.keys['update']:
                self.api.update_timeline(self.interface.buffer)
# Tweet
            elif ch == self.conf.keys['tweet']:
                self.interface.edit_status('tweet')
# Reply
            elif ch == self.conf.keys['reply']:
                self.interface.reply()
# Retweet
            elif ch == self.conf.keys['retweet']:
                self.api.retweet()
# Retweet and Edit
            elif ch == self.conf.keys['retweet_and_edit']:
                self.api.retweet_and_edit()
# Delete
            elif ch == self.conf.keys['delete']:
                self.api.destroy()
# Mention timeline
            elif ch == self.conf.keys['mentions']:
                self.interface.change_buffer('mentions')
# Home Timeline
            elif ch == self.conf.keys['home']:
                self.interface.change_buffer('home')
# Direct Message Timeline
            elif ch == self.conf.keys['getDM']:
                self.interface.change_buffer('direct')
# Clear statuses
            elif ch == self.conf.keys['clear']:
                self.interface.clear_statuses()
# Follow Selected
            elif ch == self.conf.keys['follow_selected']:
                self.api.follow_selected()
# Unfollow Selected
            elif ch == self.conf.keys['unfollow_selected']:
                self.api.unfollow_selected()
# Follow
            elif ch == self.conf.keys['follow']:
                self.interface.edit_status('follow')
# Unfollow
            elif ch == self.conf.keys['unfollow']:
                self.interface.edit_status('follow')
# Open URL
            elif ch == self.conf.keys['openurl']:
                self.interface.openurl()
# Search
            elif ch == self.conf.keys['search']:
                self.interface.edit_status('search')
# Search User
            elif ch == self.conf.keys['search_user']:
                self.interface.edit_status('public')
# Search Myself
            elif ch == self.conf.keys['search_myself']:
                self.api.my_public_timeline()
# Search Current User
            elif ch == self.conf.keys['search_current_user']:
                self.api.find_current_public_timeline()
# Send Direct Message
#FIXME
            #elif ch == self.conf.keys['sendDM']:
                #self.api.direct_message()
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
            elif ch == 'i':
                self.interface.current_user_info()
# Waterline
            elif ch == self.conf.keys['waterline']:
                self.interface.update_last_read_home()
# Back on Top
            elif ch == self.conf.keys['back_on_top']:
                self.interface.back_on_top()
# Back on Bottom
            elif ch == self.conf.keys['back_on_bottom']:
                self.interface.back_on_bottom()
# Help
            elif ch == '?':
                self.interface.display_help()

            self.interface.display_timeline()
        
        else:
            if ch in ('q', 'Q', 'esc'):
                urwid.emit_signal(self, 'help_done')

