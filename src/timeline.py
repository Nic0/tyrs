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

from filter import FilterStatus

class Timeline(object):

    def __init__(self):
        self.statuses = []
        self.unread = 0
        self.count = 0
        self.last_read = 0
        self.current = 0
        self.first = 0
        self.last = 0
        self.page = 1
        self.filter = FilterStatus()

    def append_new_statuses(self, retreive):
        if not retreive:
            pass
        retreive = self.filter_statuses(retreive)
        # Fresh new start.
        if self.statuses == []:
            self.statuses = retreive
            self.update_counter()
        # This mean there is no new status, we just leave then.
        elif retreive[0].id == self.statuses[0].id:
            pass
        # We may just don't have tweets, in case for DM for example
        elif len(retreive) == 0:
            pass
        # Finally, we append tweets
        else:
            for i in range(len(retreive)):
                if retreive[i].id == self.statuses[0].id:
                    self.statuses = retreive[:i] + self.statuses
                    self.current += len(retreive[:i])
            self.update_counter()

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
            self.count = len(self.statuses)
        except TypeError:
            self.count = 0
            
    def count_unread(self):
        try:
            self.unread = 0
            for i in range(len(self.statuses)):
                if self.statuses[i].id == self.last_read:
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
            self.last_read = self.statuses[0].id
