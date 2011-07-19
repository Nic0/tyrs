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
        self.interface.screen.timeout(-1)
        self.display_help_screen()
        self.interface.screen.timeout(500)

    def display_help_screen (self):
        self.interface.refresh_token = True
        self.interface.screen.erase()

        self.display_header()
        # Navigation
        self.display_division(_('Navigation'))
        self.display_help_item('up', _('Go up one tweet'))
        self.display_help_item('down', _('Go down one tweet'))
        self.display_help_item('back_on_top', _('Go to top of screen'))
        self.display_help_item('back_on_bottom', _('Go to bottom of screen'))
        # Timelines
        self.display_division(_('Timelines'))
        self.display_help_item('left', _('Go left on the timeline\'s bar'))
        self.display_help_item('right', _('Go right on the timeline\'s bar'))
        self.display_help_item('update', _('Refresh current timeline'))
        self.display_help_item('clear', _('Clear all but last tweet in timeline'))
        self.display_help_item('home', _('Go to home timeline'))
        self.display_help_item('mentions', _('Go to mentions timeline'))
        self.display_help_item('getDM', _('Go to direct message timeline'))
        self.display_help_item('search', _('Search for term and show resulting timeline'))
        self.display_help_item('search_user', _('Show somebody\'s public timeline'))
        self.display_help_item('search_myself', _('Show your public timeline'))
        # Tweets
        self.display_division(_('Tweets'))
        self.display_help_item('tweet', _('Send a tweet'))
        self.display_help_item('retweet', _('Retweet selected tweet'))
        self.display_help_item('retweet_and_edit', _('Retweet selected tweet, but edit first'))
        self.display_help_item('reply', _('Reply to selected tweet'))
        self.display_help_item('sendDM', _('Send direct message'))
        self.display_help_item('delete', _('Delete selected tweet (must be yours)'))
        # Follow/Unfollow
        self.display_division('Follow/Unfollow')
        self.display_help_item('follow_selected', _('Follow selected twitter'))
        self.display_help_item('unfollow_selected', _('Unfollow selected twitter'))
        self.display_help_item('follow', _('Follow a twitter'))
        self.display_help_item('unfollow', _('Unfollow a twitter'))

        # Favorite
        self.display_division('Favorite')
        self.display_help_item('fav', _('Bookmark selected tweet'))
        self.display_help_item('get_fav', _('Go to favorite timeline'))
        self.display_help_item('delete_fav', _('Delete an favorite tweet'))

        # Others
        self.display_division(_('Others'))
        self.display_help_item('quit', _('Leave Tyrs'))
        self.display_help_item('openurl', _('Open URL in browser'))
        self.display_help_item('open_image', _('Open image in browser'))
        self.display_help_item('redraw', _('Redraw the screen'))
        self.display_help_item('thread', _('Open thread seltected'))

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
