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
import sys
sys.path.append('../src/tyrs')
#import gettext
#gettext.install('tyrs', unicode=1)
#import src.utils as utils
import utils

class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_cut_attag(self):
        nick = '@mynick'
        result = utils.cut_attag(nick)
        self.assertEqual(result, 'mynick')

    def test_get_source(self):
        source = '<a href="http://tyrs.nicosphere.net/" rel="nofollow">tyrs</a>'
        result = utils.get_source(source)
        self.assertEqual(result, 'tyrs')

    def test_get_exact_nick(self):
        nick = ['@mynick', '@mynick,', '@mynick!!', 'mynick,']
        for n in nick:
            result = utils.get_exact_nick(n)
            self.assertEqual(result, 'mynick')

if __name__ == '__main__':
    unittest.main ()
