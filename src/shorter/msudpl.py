# -*- coding: utf-8 -*-
# Copyright © 2011 Nicolas Paris <nicolas.caen@gmail.com>
# Copyright © 2011 Natal Ngétal <hobbestig@cpan.org>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import urllib
from urlshorter import UrlShorter

class MsudplUrlShorter(UrlShorter):
    def __init__(self):
        self.base = "http://msud.pl"
        self.pt   = re.compile('<p>Whouah ! This a very beautiful url :\) <a href="(.*?)">')
        self.pt_yet_in_base   = re.compile('and whouah! It\'s very beautiful <a href="(.*?)">')

    def do_shorter(self, longurl):
        values = {'submit' : 'Generate my sexy url', 'sexy_url': longurl}

        data = urllib.urlencode(values)
        resp = self._get_request(self.base, data)
        short = self.pt.findall(resp)
        if len(short) == 0:
            short = self.pt_yet_in_base.findall(resp)

        if len(short) > 0:
            return self.base + '/' + short[0]
