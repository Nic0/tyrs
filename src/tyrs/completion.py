# -*- coding:utf-8 -*-
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

class Completion (object):

    def __init__(self):
        self.nicks = []

    def add(self, nick):
        if nick not in self.nicks:
            self.nicks.append(nick)

    def __repr__(self):
        return str(self.nicks)

    def __len__(self):
        return len(self.nicks)

    def complete(self, word):
        nick = []
        for n in self.nicks:
            if word in n:
                nick.append(n)
        if len(nick) is 1:
            return nick[0]
        else:
            return None

    def text_complete(self, text):
        """Return the text to insert"""
        t = text.split(' ')
        last = t[-1]
        if last[0] is '@':
            nick = self.complete(last[1:])
            if nick:
                return nick[len(last)-1:]
        return None
