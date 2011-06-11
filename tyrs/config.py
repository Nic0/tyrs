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
import message
import constant
import ConfigParser
import curses.ascii
import oauth2 as oauth

try:
    from urlparse import parse_qsl
except:
    from cgi import parse_qsl

class Config(object):

    def __init__(self, args):
        self.token = constant.token
        self.colors = constant.colors
        self.color_set = constant.color_set
        self.keys = constant.key
        self.params = constant.params
        self.home = os.environ['HOME']
        self.get_xdg_config()
        self.get_browser()
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

    def get_xdg_config(self):
        try:
            self.xdg_config = os.environ['XDG_CONFIG_HOME']
        except:
            self.xdg_config = self.home+'/.config'

    def get_browser(self):
        try:
            self.browser    = os.environ['BROWSER']
        except:
            self.browser    = ''

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

        choice = self.ask_service()
        if choice == '2':
            self.ask_root_url()

        self.authorization()
        self.createTokenFile()

    def ask_service(self):
        message.print_ask_service(self.config_file)
        choice = raw_input('Your choice? > ')

        if choice == '1':
            self.service = 'twitter'
        elif choice == '2':
            self.service = 'identica'
        else:
            sys.exit(1)
        return choice

    def ask_root_url(self):
        message.print_ask_root_url()
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
        self.parse_color()
        self.parse_keys()
        self.parse_params()

    def parse_color(self):
        for c in self.colors:
            self.colors[c]['b'] = False
            if self.conf.has_option('colors', c):
                self.colors[c]['c'] = int(self.conf.get('colors', c))
        self.parse_bold()
        self.parse_rgb()

    def parse_bold(self):
        if self.conf.has_option('colors', 'bold'):
            self.get_bold_colors(self.conf.get('colors', 'bold'))

    def parse_rgb(self):
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

    def parse_params(self):

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
