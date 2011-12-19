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
from completion import Completion

class TestCompletion(unittest.TestCase):

    def test_class(self):
        nicks = Completion()
        self.assertIsInstance(nicks, Completion)


    def test_add(self):
        nicks = Completion()
        nicks.add('coin')
        self.assertEqual(1, len(nicks))
        nicks.add('pan')
        self.assertEqual(2, len(nicks))

    def test_add_existing(self, ):
        nicks = Completion()
        nicks.add('coin')
        nicks.add('coin')
        self.assertEqual(1, len(nicks))

    def test_return_completion(self):
        nicks = Completion()
        nicks.add('coincoin')
        nicks.add('cooooooo')
        result = nicks.complete('coi')
        self.assertEqual('coincoin', result)
        result = nicks.complete('pan')
        self.assertIsNone(result)
        result = nicks.complete('co')
        self.assertIsNone(result)

    def test_return_text_completed(self):
        nicks = Completion()
        nicks.add('coin')
        nicks.add('pan')
        text = "foo bar @co"
        result = nicks.text_complete(text)
        self.assertEqual(result, 'in')

    def test_return_text_completed_failed(self):
        nicks = Completion()
        nicks.add('coin')
        nicks.add('pan')
        text = ['foo bar co', 'foo @co bar']
        for t in text:
            result =  nicks.text_complete(t)
            self.assertEqual(result, t)

if __name__ == '__main__':
    unittest.main ()
