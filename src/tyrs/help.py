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

def help_bar():
    conf = tyrs.container['conf']
    if conf.params['help']:
        return urwid.AttrWrap(urwid.Columns([
            urwid.Text(['help:', ('help_key', ' ? ')]),
            urwid.Text(['up:', ('help_key', ' %s ' % conf.keys['up'])]),
            urwid.Text(['down:', ('help_key', ' %s ' % conf.keys['down'])]),
            urwid.Text(['tweet:', ('help_key', ' %s ' % conf.keys['tweet'])]),
            ('fixed', 12, urwid.Text(['retweet:', ('help_key', ' %s ' %
                                                   conf.keys['retweet'])])),
            urwid.Text(['reply:', ('help_key', ' %s ' % conf.keys['reply'])]),
            urwid.Text(['quit:', ('help_key', ' %s ' % conf.keys['quit'])]),
        ]), 'help_bar')
    else:
        return None

class Help(urwid.WidgetWrap):

    col = [20, 7]

    def __init__ (self):
        self.interface = tyrs.container['interface']
        self.conf = tyrs.container['conf']
        self.items = []
        w = urwid.AttrWrap(self.display_help_screen(), 'body')
        self.__super.__init__(w)

    def display_help_screen (self):

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
        self.display_help_item('waterline', _('Move the waterline to the top'))
        self.display_help_item('openurl', _('Open URL in browser'))
        self.display_help_item('open_image', _('Open image in browser'))
        self.display_help_item('redraw', _('Redraw the screen'))
        self.display_help_item('thread', _('Open thread seltected'))
        return urwid.ListBox(urwid.SimpleListWalker(self.items))


    def display_division(self, title):
        self.items.append(urwid.Divider(' '))
        self.items.append(urwid.Padding(urwid.AttrWrap(urwid.Text(title), 'focus'), left=4))
        self.items.append(urwid.Divider(' '))

    def display_header(self):
        self.items.append( urwid.Columns([
            ('fixed', self.col[0], urwid.Text('  Name')),
            ('fixed', self.col[1], urwid.Text('Key')),
            urwid.Text('Description')
        ]))

    def display_help_item(self, key, description):
        self.items.append( urwid.Columns([
            ('fixed', self.col[0], urwid.Text('  '+key)),
            ('fixed', self.col[1], urwid.Text(self.conf.keys[key])),
            urwid.Text(description)
        ]))
