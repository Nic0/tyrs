#! -*- coding: utf-8 -*-
'''
   @package  tyrs
   @author   Nicolas Paris <nicolas.caen@gmail.com>
   @license  GPLv3
'''
import os
import sys
import curses
import oauth2 as oauth
import ConfigParser

try:
    from urlparse import parse_qsl
except:
    from cgi import parse_qsl

class Config:

    consumer_key = 'Eq9KLjwH9sJNcpF4OOYNw'
    consumer_secret = '3JoHyvBp3L6hhJo4BJr6H5aFxLhSlR70ZYnM8jBCQ'

    # c: color value
    # b: bold
    colors = {
        'highlight':    {'c': 1, 'b': False},
        'header':       {'c': 6, 'b': False},
        'hashtag':      {'c': 3, 'b': False},
        'attag':        {'c': 2, 'b': False},
        'text':         {'c': 7, 'b': False},
        'warning_msg':  {'c': 1, 'b': False},
        'info_msg':     {'c': 2, 'b': False},
        'current':      {'c': 5, 'b': False},
    }

    color_set = [False, False, False, False, False, False, False, False]

    keys = {
        'up':                ord('k'),
        'down':              ord('j'),
        'quit':              ord('q'),
        'tweet':             ord('t'),
        'clear':             ord('c'),
        'retweet':           ord('r'),
        'retweet_and_edit':  ord('R'),
        'update':            ord('u'),
        'follow_selected':   ord('f'),
        'unfollow_selected': ord('l'),
        'follow':            ord('F'),
        'unfollow':          ord('L'),
        'openurl':           ord('o'),
        'home':              ord('h'),
        'mentions':          ord('m'),
        'reply':             ord('M'),
        'back_on_top':       ord('g'),
        'back_on_bottom':    ord('G'),
        'getDM':             ord('d'),
        'sendDM':            ord('D'),
        'search':            ord('s'),
    }

    params_refresh         = 10
    params_tweet_border    = 1
    params_relative_time   = 0
    params_retweet_by      = 1
    params_openurl_command = 'firefox %s'
    params_transparency    = True

    home       = os.environ['HOME']

    def __init__ (self, args):

        self.tokenFile = self.home + '/.config/tyrs/tyrs.tok'
        if args.account != None:
            self.tokenFile += '.' + args.account

        self.configFile = self.home + '/.config/tyrs/tyrs.cfg'
        if args.config != None:
            self.configFile += '.' + args.config

        if not os.path.isfile(self.tokenFile):
            self.newAccount()
        else:
            self.parseToken()

        self.conf = ConfigParser.RawConfigParser()
        self.conf.read(self.configFile)
        self.parseConfig()

    def newAccount (self):
        print ''
        print 'There is no profile detected.'
        print ''
        print 'It should be in %s' % self.configFile
        print 'If you want to setup a new account, let\'s go through some basic steps'
        print 'If you want to skip this, just press return or ctrl-C.'
        print ''

        self.authorization()
        self.createTokenFile()

    def parseToken (self):
        token = ConfigParser.RawConfigParser()
        token.read(self.tokenFile)
        self.oauth_token = token.get('token', 'oauth_token')
        self.oauth_token_secret = token.get('token', 'oauth_token_secret')

    def parseConfig (self):
        ''' This parse the configuration file, and set
        some defaults values if the parameter is not given'''

        #
        # COLORS
        #
        for c in self.colors:
            if self.conf.has_option('colors', c):
                self.colors[c]['c'] = int(self.conf.get('colors', c))
        # Bold
        if self.conf.has_option('colors', 'bold'):
            self.getBoldColors(self.conf.get('colors', 'bold'))
        # Setup
        for i in range(len(self.color_set)):
            if self.conf.has_option('colors', 'color_set'+str(i)):
                self.color_set[i] = []
                rgb = (self.conf.get('colors', 'color_set'+str(i)))
                rgb = rgb.split(' ')
                self.color_set[i] = [int(rgb[0]), int(rgb[1]), int(rgb[2])]

        #
        # KEYS
        #

        for key in self.keys:
            if self.conf.has_option('keys', key):
                self.keys[key] = self.charValue(self.conf.get('keys', key))

        #
        # PARAMS
        #

        # refresh (in minutes)
        if self.conf.has_option('params', 'refresh'):
            self.params_refresh     = int(self.conf.get('params', 'refresh'))

        # tweet_border
        if self.conf.has_option('params', 'tweet_border'):
            self.params_tweet_border = int(self.conf.get('params', 'tweet_border'))

        # Relative_time
        if self.conf.has_option('params', 'relative_time'):
            self.params_relative_time = int(self.conf.get('params', 'relative_time'))

        # Retweet_By
        if self.conf.has_option('params', 'retweet_by'):
            self.params_retweet_by = int(self.conf.get('params', 'retweet_by'))

        # Openurl_command
        if self.conf.has_option('params', 'openurl_command'):
            self.params_openurl_command = self.conf.get('params',
                'openurl_command')

        # Transparency
        if self.conf.has_option('params', 'transparency'):
            if int(self.conf.get('params', 'transparency')) == 0:
                self.params_transparency = False

    def charValue (self, ch):
        if ch[0] == '^':
            i = 0
            while i <= 31:
                if curses.ascii.unctrl(i) == ch:
                    return i
                i +=1
        return ord(ch)

    def getBoldColors (self, str):
        bolds = str.split(' ')
        for bold in bolds:
            self.colors[bold]['b'] = True

    def authorization (self):
        ''' This function from python-twitter developers '''
        # Copyright 2007 The Python-Twitter Developers
        #
        # Licensed under the Apache License, Version 2.0 (the "License");
        # you may not use this file except in compliance with the License.
        # You may obtain a copy of the License at
        #
        #     http://www.apache.org/licenses/LICENSE-2.0
        #
        # Unless required by applicable law or agreed to in writing, software
        # distributed under the License is distributed on an "AS IS" BASIS,
        # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
        # See the License for the specific language governing permissions and
        # limitations under the License.
        REQUEST_TOKEN_URL          = 'https://api.twitter.com/oauth/request_token'
        ACCESS_TOKEN_URL           = 'https://api.twitter.com/oauth/access_token'
        AUTHORIZATION_URL          = 'https://api.twitter.com/oauth/authorize'
        consumer_key               = 'Eq9KLjwH9sJNcpF4OOYNw'
        consumer_secret            = '3JoHyvBp3L6hhJo4BJr6H5aFxLhSlR70ZYnM8jBCQ'
        signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()
        oauth_consumer             = oauth.Consumer(key=consumer_key, secret=consumer_secret)
        oauth_client               = oauth.Client(oauth_consumer)

        print 'Requesting temp token from Twitter'

        resp, content = oauth_client.request(REQUEST_TOKEN_URL, 'GET')

        if resp['status'] != '200':
            print 'Invalid respond from Twitter requesting temp token: %s' % resp['status']
        else:
            request_token = dict(parse_qsl(content))

            print ''
            print 'Please visit this Twitter page and retrieve the pincode to be used'
            print 'in the next step to obtaining an Authentication Token:'
            print ''
            print '%s?oauth_token=%s' % (AUTHORIZATION_URL, request_token['oauth_token'])
            print ''

            pincode = raw_input('Pincode? ')

            token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
            token.set_verifier(pincode)

            print ''
            print 'Generating and signing request for an access token'
            print ''

            oauth_client  = oauth.Client(oauth_consumer, token)
            resp, content = oauth_client.request(ACCESS_TOKEN_URL, method='POST', body='oauth_verifier=%s' % pincode)
            access_token  = dict(parse_qsl(content))

            if resp['status'] != '200':
                print 'The request for a Token did not succeed: %s' % resp['status']
                print access_token
                sys.exit()
            else:
                self.oauth_token = access_token['oauth_token']
                self.oauth_token_secret = access_token['oauth_token_secret']

    def createTokenFile(self):

        if not os.path.isdir(self.home + '/.config/tyrs'):
            try:
                os.mkdir(self.home + '/.config/tyrs')
            except:
                print 'Error to create directory .config/tyrs'

        conf = ConfigParser.RawConfigParser()
        conf.add_section('token')
        conf.set('token', 'oauth_token', self.oauth_token)
        conf.set('token', 'oauth_token_secret', self.oauth_token_secret)

        with open(self.tokenFile, 'wb') as tokens:
            conf.write(tokens)

        print 'your account has been saved'
