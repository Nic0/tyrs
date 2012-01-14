#!/usr/bin/python
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

import sys
import unittest
sys.path.append('../src/tyrs')
import random
from shorter.urlshorter  import UrlShorter
from shorter.bitly import BitLyUrlShorter 
#TODO this shortener has dependencies such as `apiclient` and `urllib3`
#from shorter.googl import GooglUrlShorter
#FIXME msud.pl raises 502 HTTP errors very often
#from shorter.msudpl import MsudplUrlShorter
from shorter.ur1ca import Ur1caUrlShorter

url_re = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

class TestShortener(unittest.TestCase):

    shorteners = [BitLyUrlShorter, Ur1caUrlShorter]
    
    def shortener_test(self, cls, url):
        """
        Receives a class descendant of `UrlShorter` and tests it with the
        given url.
        """
        assert issubclass(cls, UrlShorter)
        shortener = cls()
        result = shortener.do_shorter(url)
        self.assertRegexpMatches(result, url_re)

    def test_yet_in_base(self):
        url = 'http://www.nicosphere.net'
        for shortener in self.shorteners:
            self.shortener_test(shortener, url)

    def test_random_url(self):
        number = random.randint(10000, 100000)
        url = 'http://www.nicosphere{0}.net'.format(number)
        for shortener in self.shorteners:
            self.shortener_test(shortener, url)


if __name__ == '__main__':
    unittest.main()
