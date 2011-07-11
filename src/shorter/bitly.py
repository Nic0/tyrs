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

import urllib2
try:
    import json
except:
    import simplejson as json

from urlshorter import UrlShorter

APIKEY = 'apiKey=R_f806c2011339080ea0b623959bb8ecff'
VERION = 'version=2.0.1'
LOGIN  = 'login=tyrs'

class BitLyUrlShorter(UrlShorter):

    def __init__(self):
        self.base = 'http://api.bit.ly/shorten?%s&%s&%s&longUrl=%s'

    def do_shorter(self, url):
        long_url = self._quote_url(url)
        request = self.base % (VERION, LOGIN, APIKEY, long_url)
        response = json.loads(urllib2.urlopen(request).read())
        return response['results'][url]['shortUrl']
