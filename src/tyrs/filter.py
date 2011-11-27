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

import re
import tyrs
from utils import get_urls

class FilterStatus(object):

    def __init__(self):
        self.conf = tyrs.container['conf']

    def filter_status(self, status):
        self.setup_exception()
        try:
            if self.conf.filter['activate']:
                self.status = status
                if self.filter_without_url():
                    if self.filter_without_myself():
                        if self.filter_exception():
                            return True
            return False
        except:
            return False

    def filter_without_url(self):
        urls = get_urls(self.status.text)
        if len(urls) == 0:
            return True
        return False

    def filter_without_myself(self):
        if self.conf.filter['myself']:
            return True
        if self.conf.my_nick in self.status.text:
            return False
        else:
            return True


    def filter_exception(self):
        nick = self.status.user.screen_name
        if self.conf.filter['behavior'] == 'all':
            if not nick in self.exception:
                return True
        else:
            if nick in self.exception:
                return True
        return False

    def setup_exception(self):
        self.exception = self.conf.filter['except']
        self.exception.append(self.conf.my_nick)
