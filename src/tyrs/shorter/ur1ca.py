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
import urllib
from urlshorter import UrlShorter

class Ur1caUrlShorter(UrlShorter):
    def __init__(self):
        self.base = "http://ur1.ca"
        self.pt = re.compile('<p class="success">Your ur1 is: <a href="(.*?)">')

    def do_shorter(self, longurl):
        values = {'submit' : 'Make it an ur1!', 'longurl' : longurl}

        data = urllib.urlencode(values)
        resp = self._get_request(self.base, data)
        short = self.pt.findall(resp)

        if len(short) > 0:
            return short[0]
