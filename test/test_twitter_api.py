#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append('../tyrs')


from time import gmtime, strftime
strftime("%Y-%m-%d %H:%M:%S", gmtime())

import tyrs.tyrs as tyrs
import tyrs.tweets as tweets

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
        result = self.api.myself.screen_name 
        self.assertEqual(result, self.username)

    def test_post_update(self):
        tweet = 'test from unittest at ' + self.get_time()
        result = self.api.post_tweet(tweet, None)
        self.assertEqual(result.text, tweet)

    def get_time(self):
        return strftime('%H:%M:%S', gmtime())

if __name__ == '__main__':
    unittest.main ()
