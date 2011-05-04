import os
import ConfigParser

class Config:

    consumer_key = 'Eq9KLjwH9sJNcpF4OOYNw'
    consumer_secret = '3JoHyvBp3L6hhJo4BJr6H5aFxLhSlR70ZYnM8jBCQ'
    
    def __init__ (self):

        configFile = os.environ['HOME'] + '/.config/tyrsrc'
        conf = ConfigParser.RawConfigParser()
        conf.read(configFile)

        self.pseudo             = conf.get('account', 'pseudo')
        self.oauth_token        = conf.get('token', 'oauth_token')
        self.oauth_token_secret = conf.get('token', 'oauth_token_secret')

        #
        # COLORS
        #

        # header
        if conf.has_option('colors', 'header'):
            self.color_header       = int(conf.get('colors', 'header'))
        else:
            self.color_header = 3

        # hashtag ('#')
        if conf.has_option('colors', 'hashtag'):
            self.color_hashtag      = int(conf.get('colors', 'hashtag'))
        else:
            self.color_hashtag = 8

        # attag ('@')
        if conf.has_option('colors', 'attag'):
            self.color_attag        = int(conf.get('colors', 'attag'))
        else:
            self.color_attag = 4

        #
        # KEYS
        #

        # up
        if conf.has_option('keys', 'up'):
            self.keys_up            = conf.get('keys', 'up')
        else:
            self.keys_up = 'k'

        # down
        if conf.has_option('keys', 'down'):
            self.keys_down          = conf.get('keys', 'down')
        else:
            self.keys_down = 'j'

        # quit
        if conf.has_option('keys', 'quit'):
            self.keys_quit          = conf.get('keys', 'quit')
        else:
            self.keys_quit = 'q'

        # tweet 
        if conf.has_option('keys', 'tweet'):
            self.keys_tweet         = conf.get('keys', 'tweet')
        else:
            self.keys_tweet = 't'

        #
        # PARAMS
        #

        # refresh (in minutes)
        if conf.has_option('params', 'refresh'):
            self.params_refresh     = int(conf.get('params', 'refresh'))
        else:
            self.params_refresh = 10
