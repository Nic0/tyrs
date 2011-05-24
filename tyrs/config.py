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

    color_highlight        = 1
    color_header           = 6
    color_hashtag          = 3
    color_attag            = 2
    color_text             = 7
    color_warning_msg      = 1
    color_info_msg         = 2
    color_current_tweet    = 5

    color_set = [False, False, False, False, False, False, False, False]

    keys_up                = ord('k')
    keys_down              = ord('j')
    keys_quit              = ord('q')
    keys_tweet             = ord('t')
    keys_clear             = ord('c')
    keys_retweet           = ord('r')
    keys_retweet_and_edit  = ord('R')
    keys_update            = ord('u')
    keys_follow_selected   = ord('f')
    keys_unfollow_selected = ord('l')
    keys_follow            = ord('F')
    keys_unfollow          = ord('L')
    keys_openurl           = ord('o')
    keys_home              = ord('h')
    keys_mentions          = ord('m')
    keys_reply             = ord('M')
    keys_back_on_top       = ord('g')
    keys_back_on_bottom    = ord('G')
    keys_getDM             = ord('d')
    keys_sendDM            = ord('D')
    keys_search            = ord('s')

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

        # self.pseudo             = self.conf.get('account', 'pseudo')
        # self.oauth_token        = self.conf.get('token', 'oauth_token')
        # self.oauth_token_secret = self.conf.get('token', 'oauth_token_secret')

        #
        # COLORS
        #

        # header
        if self.conf.has_option('colors', 'header'):
            self.color_header       = int(self.conf.get('colors', 'header'))

        # highlight
        if self.conf.has_option('colors', 'highlight'):
            self.color_highlight    = int(self.conf.get('colors', 'highlight'))

        # hashtag ('#')
        if self.conf.has_option('colors', 'hashtag'):
            self.color_hashtag      = int(self.conf.get('colors', 'hashtag'))

        # attag ('@')
        if self.conf.has_option('colors', 'attag'):
            self.color_attag        = int(self.conf.get('colors', 'attag'))

        # text
        if self.conf.has_option('colors', 'text'):
            self.color_text         = int(self.conf.get('colors', 'text'))

        # Warning messages
        if self.conf.has_option('colors', 'warning_msg'):
            self.color_warning_msg      = int(self.conf.get('colors', 'warning_msg'))

        # Information messages
        if self.conf.has_option('colors', 'info_msg'):
            self.color_info_msg        = int(self.conf.get('colors', 'info_msg'))

        #
        # COLOR SETUP
        #

        for i in range(len(self.color_set)):
            if self.conf.has_option('colors', 'color_set'+str(i)):
                self.color_set[i] = []
                rgb = (self.conf.get('colors', 'color_set'+str(i)))
                rgb = rgb.split(' ')
                self.color_set[i] = [int(rgb[0]), int(rgb[1]), int(rgb[2])]

        #
        # KEYS
        # 

        # up
        if self.conf.has_option('keys', 'up'):
            self.keys_up            = self.charValue(self.conf.get('keys', 'up'))

        # down
        if self.conf.has_option('keys', 'down'):
            self.keys_down          = self.charValue(self.conf.get('keys', 'down'))

        # quit
        if self.conf.has_option('keys', 'quit'):
            self.keys_quit          = self.charValue(self.conf.get('keys', 'quit'))

        # tweet
        if self.conf.has_option('keys', 'tweet'):
            self.keys_tweet         = self.charValue(self.conf.get('keys', 'tweet'))

        # clear
        if self.conf.has_option('keys', 'clear'):
            self.keys_clear         = self.charValue(self.conf.get('keys', 'clear'))

        # retweet
        if self.conf.has_option('keys', 'retweet'):
            self.keys_retweet       = self.charValue(self.conf.get('keys', 'retweet'))

        # retweet and edit
        if self.conf.has_option('keys', 'retweet_and_edit'):
            self.keys_retweet_and_edit = self.charValue(self.conf.get('keys', 'retweet_and_edit'))

        # update
        if self.conf.has_option('keys', 'update'):
            self.keys_update        = self.charValue(self.conf.get('keys', 'update'))

        # follow_selected
        if self.conf.has_option('keys', 'follow_selected'):
            self.keys_follow_selected = self.charValue(self.conf.get('keys', 'follow_selected'))

        # unfollow_selected
        if self.conf.has_option('keys', 'unfollow_selected'):
            self.keys_unfollow_selected = self.charValue(self.conf.get('keys', 'unfollow_selected'))

        # follow
        if self.conf.has_option('keys', 'follow'):
            self.keys_follow = self.charValue(self.conf.get('keys', 'follow'))

        # unfollow
        if self.conf.has_option('keys', 'unfollow'):
            self.keys_unfollow = self.charValue(self.conf.get('keys', 'unfollow'))

        # openurl
        if self.conf.has_option('keys', 'openurl'):
            self.keys_openurl = self.charValue(self.conf.get('keys', 'openurl'))

        # home
        if self.conf.has_option('keys', 'home'):
            self.keys_home = self.charValue(self.conf.get('keys', 'home'))

        # mentions
        if self.conf.has_option('keys', 'mentions'):
            self.keys_mentions = self.charValue(self.conf.get('keys', 'mentions'))

        # back on top
        if self.conf.has_option('keys', 'back_on_top'):
            self.keys_back_on_top = self.charValue(self.conf.get('keys', 'back_on_top'))

        # back on bottom
        if self.conf.has_option('keys', 'back_on_bottom'):
            self.keys_back_on_bottom = self.charValue(self.conf.get('keys', 'back_on_bottom'))

        # Reply
        if self.conf.has_option('keys', 'reply'):
            self.keys_reply = self.charValue(self.conf.get('keys', 'reply'))
        
        # get DM
        if self.conf.has_option('keys', 'getDM'):
            self.keys_getDM = self.charValue(self.conf.get('keys,' 'getDM'))

        # send DM
        if self.conf.has_option('keys', 'sendDM'):
            self.keys_sendDM = self.charValue(self.conf.get('keys', 'sendDM'))

        # search
        if self.conf.has_option('keys', 'search'):
            self.keys_search = self.charValue(self.conf.get('keys', 'search'))

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
