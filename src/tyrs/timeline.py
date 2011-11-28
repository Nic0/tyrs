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

import urwid
from widget import StatusWidget
from filter import FilterStatus

class Timeline(object):

    def __init__(self):
        self.statuses = []
        self.walker = []
        self.unread = 0
        self.count = 0
        self.last_read = 0
        self.current = 0
        self.first = 0
        self.last = 0
        self.page = 1
        self.filter = FilterStatus()
        self.timeline = urwid.ListBox(urwid.SimpleListWalker([]))

    def append_new_statuses(self, retreive):
        retreive = self.filter_statuses(retreive)

        if retreive:
            items = []
            if len(self.walker) == 0:
                for i, status in enumerate(retreive):
                    items.append(StatusWidget(status.id, status))
                    self.walker = urwid.SimpleListWalker(items)
                    self.timeline = urwid.ListBox(self.walker)
            else:
                import tyrs
                self.interface = tyrs.container['interface']
                size = self.interface.loop.screen_size
                on_top = 'top' in self.timeline.ends_visible(size)
                focus_status, pos = self.walker.get_focus()
                for i, status in enumerate(retreive):
                    while status.id != self.walker[0+i].id:
                        self.walker.insert(i, StatusWidget(status.id, status))
                        if on_top:
                            self.timeline.set_focus(0)
                        self.timeline.set_focus(pos+i+1)
                    self.walker[i] = StatusWidget(status.id, status)

    def filter_statuses(self, statuses):
        filters = []
        for i, status in enumerate(statuses):
            if self.filter.filter_status(status):
                filters.append(i)
        filters.reverse()
        for f in filters:
            del statuses[f]

        return statuses

    def update_counter(self):
        self.count_statuses()
        self.count_unread()

    def append_old_statuses(self, statuses):
        if statuses == []:
            pass
        else:
            self.statuses += statuses
            self.count_statuses()
            self.count_unread()

    def count_statuses(self):
        try:
            self.count = len(self.walker)
        except TypeError:
            self.count = 0

    def count_unread(self):
        try:
            self.unread = 0
            for i in range(len(self.walker)):
                if self.walker[i].id == self.last_read:
                    break
                self.unread += 1
        except TypeError:
            self.unread = 0

    def reset(self):
        self.first = 0
        self.unread = 0

    def empty(self):
        self.__init__()

    def all_read(self):
        if self.count > 0:
            self.last_read = self.walker[0].id
