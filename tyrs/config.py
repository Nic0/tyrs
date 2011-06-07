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

import os
import sys
import curses
import curses.ascii
import oauth2 as oauth
import ConfigParser

try:
    from urlparse import parse_qsl
except:
    from cgi import parse_qsl

class Config:

    token = {
        'twitter': {
            'consumer_key':     'Eq9KLjwH9sJNcpF4OOYNw',
            'consumer_secret':  '3JoHyvBp3L6hhJo4BJr6H5aFxLhSlR70ZYnM8jBCQ'
        },
        'identica': {
            'consumer_key':     '6b2cf8346a141d530739f72b977b7078',
            'consumer_secret':  '31b342b348502345d4a343a331e00edb'
        }
    }

    # c: color value
    # b: bold
    colors = {
        'highlight':      {'c': 1},
        'header':         {'c': 6},
        'hashtag':        {'c': 3},
        'attag':          {'c': 2},
        'text':           {'c': 7},
        'warning_msg':    {'c': 1},
        'info_msg':       {'c': 2},
        'current_tweet':  {'c': 5},
        'current_tab':    {'c': 6},
        'other_tab':      {'c': 7},
        'unread':         {'c': 1},
        'read':           {'c': 7},
        'help':           {'c': 6},
    }

    color_set = [False, False, False, False, False, False, False, False]

    keys = {
        'up':                'k',
        'down':              'j',
        'left':              'J',
        'right':             'K',
        'quit':              'q',
        'tweet':             't',
        'clear':             'c',
        'retweet':           'r',
        'retweet_and_edit':  'R',
        'delete':            'C',
        'update':            'u',
        'follow_selected':   'f',
        'unfollow_selected': 'l',
        'follow':            'F',
        'unfollow':          'L',
        'openurl':           'o',
        'home':              'h',
        'mentions':          'm',
        'reply':             'M',
        'back_on_top':       'g',
        'back_on_bottom':    'G',
        'getDM':             'd',
        'sendDM':            'D',
        'search':            's',
        'search_user':       'U',
        'search_myself':     '^U',
        'redraw':            '^L',
        'fav':               'b',
        'get_fav':           'B',
        'delete_fav':        '^B',
    }

    params = {
        'refresh':              10,
        'tweet_border':         1,
        'relative_time':        0,
        'retweet_by':           1,
        'openurl_command':      'firefox %s',
        'transparency':         True,
        'activities':           True,
        'compress':             False,
        'help':                 True,
    }

    home       = os.environ['HOME']
    try:
        xdg_config = os.environ['XDG_CONFIG_HOME']
    except:
        xdg_config = home+'/.config'

    try:
        browser    = os.environ['BROWSER']
    except:
        browser    = ''

    def __init__(self, args):

        # generate the config file
        if args.generate_config != None:
            self.generate_config_file(args)

        self.set_path(args)
        if not os.path.isfile(self.tokenFile):
            self.new_account()
        else:
            self.parse_token()

        self.conf = ConfigParser.RawConfigParser()
        self.conf.read(self.config_file)
        self.parse_config()

    def generate_config_file(self, args):

        config_file = args.generate_config
        conf = ConfigParser.RawConfigParser()
        conf.read(config_file)

        # COLOR
        conf.add_section('colors')
        for c in self.colors:
            conf.set('colors', c, self.colors[c]['c'])
        conf.set('colors', 'bold', '')
        # KEYS
        conf.add_section('keys')
        for k in self.keys:
            conf.set('keys', k, self.keys[k])
        # PARAMS
        conf.add_section('params')
        for p in self.params:
            if self.params[p] == True:
                value = 1
            elif self.params[p] == False:
                value = 0
            else:
                value = self.params[p]

            conf.set('params', p, value)

        with open(config_file, 'wb') as config:
            conf.write(config)

        sys.exit(0)

    def set_path(self, args):
        # Default config path set
        if self.xdg_config != '':
            self.tyrs_path = self.xdg_config + '/tyrs/'
        else:
            self.tyrs_path = self.home + '/.config/tyrs/'
        # Setup the token file
        self.tokenFile = self.tyrs_path + 'tyrs.tok'
        if args.account != None:
            self.tokenFile += '.' + args.account
        # Setup the config file
        self.config_file = self.tyrs_path + 'tyrs.cfg'
        if args.config != None:
            self.config_file += '.' + args.config

    def new_account(self):

        choice = self.askService()
        if choice == '2':
            self.ask_root_url()

        self.authorization()
        self.createTokenFile()

    def askService(self):
        print ''
        print 'There is no profile detected.'
        print ''
        print 'It should be in %s' % self.config_file
        print 'If you want to setup a new account, let\'s go through some basic steps'
        print 'If you want to skip this, just press return or ctrl-C.'
        print ''

        print ''
        print 'Which service do you want to use?'
        print ''
        print '1. Twitter'
        print '2. Identi.ca'
        print ''
        choice = raw_input('Your choice? > ')

        if choice == '1':
            self.service = 'twitter'
        elif choice == '2':
            self.service = 'identica'
        else:
            sys.exit(1)
        return choice

    def ask_root_url(self):
        print ''
        print ''
        print 'Which root url do you want? (leave blank for default value, https://identi.ca/api)'
        print ''
        url = raw_input('Your choice? > ')
        if url == '':
            self.base_url = 'https://identi.ca/api'
        else:
            self.base_url = url

    def parse_token(self):
        token = ConfigParser.RawConfigParser()
        token.read(self.tokenFile)
        if token.has_option('token', 'service'):
            self.service = token.get('token', 'service')
        else:
            self.service = 'twitter'

        if token.has_option('token', 'base_url'):
            self.base_url = token.get('token', 'base_url')

        self.oauth_token = token.get('token', 'oauth_token')
        self.oauth_token_secret = token.get('token', 'oauth_token_secret')

    def parse_config(self):
        ''' This parse the configuration file, and set
        some defaults values if the parameter is not given'''
        self.parse_color()
        self.parse_keys()
        self.parseParams()

    def parse_color(self):
        for c in self.colors:
            self.colors[c]['b'] = False
            if self.conf.has_option('colors', c):
                self.colors[c]['c'] = int(self.conf.get('colors', c))
        # Bold
        if self.conf.has_option('colors', 'bold'):
            self.get_bold_colors(self.conf.get('colors', 'bold'))
        # Setup rgb
        for i in range(len(self.color_set)):
            if self.conf.has_option('colors', 'color_set'+str(i)):
                self.color_set[i] = []
                rgb = (self.conf.get('colors', 'color_set'+str(i)))
                rgb = rgb.split(' ')
                self.color_set[i] = [int(rgb[0]), int(rgb[1]), int(rgb[2])]

    def parse_keys(self):
        for key in self.keys:
            if self.conf.has_option('keys', key):
                self.keys[key] = self.char_value(self.conf.get('keys', key))
            else:
                self.keys[key] = self.char_value(self.keys[key])

    def parseParams(self):

        # refresh (in minutes)
        if self.conf.has_option('params', 'refresh'):
            self.params['refresh']     = int(self.conf.get('params', 'refresh'))

        # tweet_border
        if self.conf.has_option('params', 'tweet_border'):
            self.params['tweet_border'] = int(self.conf.get('params', 'tweet_border'))

        # Relative_time
        if self.conf.has_option('params', 'relative_time'):
            self.params['relative_time'] = int(self.conf.get('params', 'relative_time'))

        # Retweet_By
        if self.conf.has_option('params', 'retweet_by'):
            self.params['retweet_by'] = int(self.conf.get('params', 'retweet_by'))

        # Openurl_command
        if self.conf.has_option('params', 'openurl_command'):
            self.params['openurl_command'] = self.conf.get('params',
                'openurl_command')
        elif self.browser != '':
            self.params['openurl_command'] = self.browser + ' %s'

        # Transparency
        if self.conf.has_option('params', 'transparency'):
            if int(self.conf.get('params', 'transparency')) == 0:
                self.params['transparency'] = False
        # Compress display
        if self.conf.has_option('params', 'compress'):
            if int(self.conf.get('params', 'compress')) == 1:
                self.params['compress'] = True
        # Help bar
        if self.conf.has_option('params', 'help'):
            if int(self.conf.get('params', 'help')) == 0:
                self.params['help'] = False

    def char_value(self, ch):
        if ch[0] == '^':
            i = 0
            while i <= 31:
                if curses.ascii.unctrl(i) == ch:
                    return i
                i +=1
        return ord(ch)

    def get_bold_colors(self, str):
        bolds = str.split(' ')
        for bold in bolds:
            try:
                self.colors[bold]['b'] = True
            except:
                print 'The param "%s" does not exist for bold colors' % bold

    def authorization(self):
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

        if self.service == 'twitter':
            base_url = 'https://api.twitter.com'
            self.base_url = base_url
        else:
            base_url = self.base_url


        REQUEST_TOKEN_URL          = base_url + '/oauth/request_token'
        if self.service == 'identica':
            REQUEST_TOKEN_URL += '?oauth_callback=oob'

        ACCESS_TOKEN_URL           = base_url + '/oauth/access_token'
        AUTHORIZATION_URL          = base_url + '/oauth/authorize'
        consumer_key               = self.token[self.service]['consumer_key']
        consumer_secret            = self.token[self.service]['consumer_secret']
        signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()
        oauth_consumer             = oauth.Consumer(key=consumer_key, secret=consumer_secret)
        oauth_client               = oauth.Client(oauth_consumer)

        print 'Requesting temp token from ' + self.service.capitalize()

        resp, content = oauth_client.request(REQUEST_TOKEN_URL, 'GET')

        if resp['status'] != '200':
            print 'Invalid respond from ' +self.service.capitalize() + ' requesting temp token: %s' % resp['status']
        else:
            request_token = dict(parse_qsl(content))

            print ''
            print 'Please visit this ' + self.service.capitalize() + ' page and retrieve the pincode to be used'
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

        if not os.path.isdir(self.tyrs_path):
            try:
                os.mkdir(self.tyrs_path)
            except:
                print 'Error to create directory .config/tyrs'

        conf = ConfigParser.RawConfigParser()
        conf.add_section('token')
        conf.set('token', 'service', self.service)
        conf.set('token', 'base_url', self.base_url)
        conf.set('token', 'oauth_token', self.oauth_token)
        conf.set('token', 'oauth_token_secret', self.oauth_token_secret)

        with open(self.tokenFile, 'wb') as tokens:
            conf.write(tokens)

        print 'your account has been saved'
