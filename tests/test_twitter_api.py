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
sys.path.append('../tyrs')
from time import gmtime, strftime
import tyrs.tyrs as tyrs
import tyrs.tweets as tweets
from twitter import TwitterError, Status, User

class TestTwitterApi(unittest.TestCase):

    def setUp(self):
        self.username = 'twitturse'
        self.authenticate()

    def authenticate(self):
        try:
            tyrs.init_conf()
        except TypeError:
            pass
        self.api = tweets.Tweets()
        self.api.authentication()

    def test_authentication(self):
        myself = self.api.myself
        username = myself.screen_name
        self.assertIsInstance(myself, User)
        self.assertEqual(username, self.username)

    def test_post_update(self):
        tweet = 'test from unittest at ' + self.get_time()
        result = self.api.post_tweet(tweet)
        self.assertEqual(result.text, tweet)
    
    def test_post_empty_update(self):
        tweet = ''
        result = self.api.post_tweet(tweet)
        self.assertIsNone(result)

    def test_update_home_timeline(self):
        result = self.api.update_home_timeline()
        self.assertIsInstance(result[0], Status)
        self.assertIsInstance(result[10], Status)

    def get_time(self):
        return strftime('%H:%M:%S', gmtime())

if __name__ == '__main__':
    unittest.main ()
