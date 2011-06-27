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

class FilterStatus(object):

    def __init__(self):
        self.conf = tyrs.container['conf']

    def filter_status(self, status):
        if self.conf.filter['activate']:
            if self.filter_without_url(status):
                if self.filter_without_myself(status):
                    return True
                    #if self.filter_exception(status):
                        #return True
        return False

    def filter_without_url(self, status):
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', status.text)
        if len(urls) == 0:
            return True
        return False

    def filter_without_myself(self, status):
        if self.conf.filter['myself']:
            if self.conf.my_nick in status.text:
                return True
        return False

    def filter_exception(self, status):
        pass
