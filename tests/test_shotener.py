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

import unittest
import random
from shorter.msudpl import MsudplUrlShorter

class TestShortener(unittest.TestCase):

    def test_msudpl_yet_in_base(self):
        url_re = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        shortener = MsudplUrlShorter()
        result = shortener.do_shorter('http://www.nicosphere.net')
        self.assertRegexpMatches(result, url_re)

    def test_msudpl_random_url(self):
        url_re = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        shortener = MsudplUrlShorter()
        number = random.randint(10000, 100000)
        result = shortener.do_shorter('http://www.nicosphere{}.net'.format(number))
        self.assertRegexpMatches(result, url_re)

if __name__ == '__main__':
    unittest.main()
