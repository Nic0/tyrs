#!/usr/bin/python
# -*- coding: utf-8 -*-

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
        result = self.api.post_tweet(tweet, None)
        self.assertEqual(result.text, tweet)
    
    def test_post_empty_update(self):
        tweet = ''
        with self.assertRaises(TwitterError):
            self.api.post_tweet(tweet, None)

    def test_update_home_timeline(self):
        result = self.api.update_home_timeline()
        self.assertIsInstance(result[0], Status)
        self.assertIsInstance(result[10], Status)

    def get_time(self):
        return strftime('%H:%M:%S', gmtime())

if __name__ == '__main__':
    unittest.main ()
