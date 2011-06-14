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

class Help(object):

    y = 2
    col = [2, 25, 30]

    def __init__ (self):
        self.interface = tyrs.container['interface']
        self.conf = tyrs.container['conf']
        self.max = self.interface.screen.getmaxyx()
        self.display_help_screen()

    def display_help_screen (self):
        self.interface.refresh_token = True
        self.interface.screen.erase()

        self.display_header()
        # Navigation
        self.display_division(_('Navigation'))
        self.display_help_item('up', _('Moves up'))
        self.display_help_item('down', _('Moves down'))
        self.display_help_item('back_on_top', _('Move back on top'))
        self.display_help_item('back_on_bottom', _('Move to the bottom of the screen'))
        # Timelines
        self.display_division(_('Timelines'))
        self.display_help_item('left', _('Moves left in timelines'))
        self.display_help_item('right', _('Moves right in timelines'))
        self.display_help_item('update', _('Refresh the current timeline'))
        self.display_help_item('clear', _('Clear, and leave the last tweet in your timeline'))
        self.display_help_item('home', _('Moves to the home timeline'))
        self.display_help_item('mentions', _('Moves to the mentions timeline'))
        self.display_help_item('getDM', _('Moves to the direct message timeline'))
        self.display_help_item('search', _('Ask for a term to search and move to his timeline'))
        self.display_help_item('search_user', _('Retrieve someone public timeline'))
        self.display_help_item('search_myself', _('Retrieve your public timeline'))
        # Tweets
        self.display_division(_('Tweets'))
        self.display_help_item('tweet', _('Send a tweet'))
        self.display_help_item('retweet', _('Retweet the selected tweet'))
        self.display_help_item('retweet_and_edit', _('Retweet with response the selected tweet'))
        self.display_help_item('reply', _('Reply to the selected tweet'))
        self.display_help_item('sendDM', _('Send a direct message'))
        self.display_help_item('delete', _('Delete the selected tweet, must be your tweet'))
        # Follow/Unfollow
        self.display_division('Follow/Unfollow')
        self.display_help_item('follow_selected', _('Follow the selected twitter'))
        self.display_help_item('unfollow_selected', _('Unfollow the selected twitter'))
        self.display_help_item('follow', _('Follow a twitter'))
        self.display_help_item('unfollow', _('Unfollow a twitter'))
        # Others
        self.display_division(_('Others'))
        self.display_help_item('quit', _('Leave Tyrs'))
        self.display_help_item('openurl', _('Open an url with your browser'))
        self.display_help_item('redraw', _('Force to redraw the screen'))

        self.interface.screen.refresh()
        self.interface.screen.getch()
        self.interface.screen.erase()

        self.interface.refresh_token = False

    def display_division(self, title):
        self.increase(2)
        color = curses.color_pair(5)
        title = '-- ' + title + ' --'
        self.interface.screen.addstr(self.y, self.col[0],
                title.encode(self.interface.charset), color)
        self.increase(1)

    def display_header(self):
        scr = self.interface.screen
        color = curses.color_pair(5)
        scr.addstr(self.y, self.col[0],
                _('Name').encode(self.interface.charset), color)
        scr.addstr(self.y, self.col[1], _('Key').encode(self.interface.charset), color)
        scr.addstr(self.y, self.col[2],
                _('Description').encode(self.interface.charset), color)

    def display_help_item(self, key, description):
        scr = self.interface.screen
        color = self.interface.get_color('help')
        scr.addstr(self.y, self.col[0], key, color)
        scr.addstr(self.y, self.col[1], chr(self.conf.keys[key]), color)
        scr.addstr(self.y, self.col[2], description.encode(self.interface.charset), color)
        self.increase(1)

    def increase(self, incr):
        '''This make sure there some space left on the screen.'''
        if self.y + incr >= self.max[0]:
            self.interface.screen.refresh()
            self.interface.screen.getch()
            self.y = 2
            self.interface.screen.erase()
            self.display_header()
            self.increase(2)
        else:
            self.y += incr
