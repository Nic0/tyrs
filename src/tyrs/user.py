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
from utils import encode

class User(object):

    def __init__(self, user):
        self.interface = tyrs.container['interface']
        self.user = user
        self.interface.refresh_token = True
        self._init_screen()
        self._display_header()
        self._display_info()
        self.screen.getch()
        self.screen.erase()
        self.interface.refresh_token = False

    def _init_screen(self):
        maxyx = self.interface.screen.getmaxyx()
        self.screen = self.interface.screen.subwin(30, 80, 3, 10)
        self.screen.border(0)
        self.screen.refresh()

    def _display_header(self):
        self.screen.addstr(2, 10, '%s -- %s' % (self.user.screen_name,
            encode(self.user.name)))

    def _display_info(self):
        info = {
            'location': encode(self.user.location),
            'description': encode(self.user.description),
            'url': encode(self.user.url),
            'time zone': encode(self.user.time_zone),
            'status': self.user.status,
            'friends': self.user.friends_count,
            'follower': self.user.followers_count,
            'tweets': self.user.statuses_count,
            'verified': self.user.verified,
            'created at': self.user.created_at,
            }
        i=0
        for item in info:
            self.screen.addstr(4+i, 5, '%s' % item)
            self.screen.addstr(4+i, 20, '%s' % info[item])
            i += 1


