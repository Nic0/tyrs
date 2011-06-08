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

import tyrs
import urllib2
from editor import *
from utils import cut_attag
from message import FlashMessage
from twitter import Api, TwitterError

try:
    import json
except ImportError:
    import simplejson as json

class Tweets:
 
    def __init__(self):
        self.conf = tyrs.container['conf']
        self.sear_user = ''
        self.search_word = ''
        self.flash_message = FlashMessage()

    def set_ui(self, interface):
        self.interface = interface

    def authentication(self):
        url = self.get_base_url()
        self.api = ApiPatch(
            self.conf.token[self.conf.service]['consumer_key'],
            self.conf.token[self.conf.service]['consumer_secret'],
            self.conf.oauth_token,
            self.conf.oauth_token_secret,
            base_url=url
        )
        self.set_myself()

    def get_base_url(self):
        url = None
        if self.conf.service == 'identica':
            url = self.conf.base_url

        return url

    def set_myself(self):
        self.myself = self.api.VerifyCredentials()

    def tweet(self, data=None):
        tweet = TweetEditor(data).content
        if tweet:
            self.post_tweet(tweet)

    def post_tweet(self, tweet, reply_to=None):
        self.flash('tweet')
        try:
            return self.api.PostUpdate(tweet, reply_to)
        except TwitterError:
            self.error() 

    def retweet(self):
        self.flash('retweet')
        status = self.interface.current_status()
        try:
            self.api.PostRetweet(status.id)
        except TwitterError:
            self.error()

    def retweet_and_edit(self):
        status = self.interface.current_status()
        nick = status.user.screen_name
        data = 'RT @%s: %s' % (nick, status.text)
        self.tweet(data)

    def reply(self):
        status = self.interface.current_status()
        data = '@' + status.user.screen_name + ' '
        tweet = TweetEditor(data).content
        if tweet:
            self.post_tweet(data, status.id)

    def destroy(self):
        self.flash('destroy')
        status = self.interface.current_status()
        try:
            self.api.DestroyStatus(status.id)
        except TwitterError:
            self.error()

    def direct_message(self):
        ''' Two editing box, one for the name, and one for the content'''
        nick = self.nick_for_direct_message()
        tweet = TweetEditor().content
        if tweet:
            self.send_direct_message(nick, tweet)

    def nick_for_direct_message(self):
        status = self.interface.current_status()
        if hasattr(status, 'user'):
            nick = status.user.screen_name
        else:
            nick = status.sender_screen_name
        nick = NickEditor(nick).content

        return nick

    def send_direct_message(self, nick, tweet):
        self.flash('direct')
        try:
            return self.api.PostDirectMessage(nick, tweet)
        except TwitterError:
            self.error()

    def follow(self):
        nick = NickEditor().content
        if nick:
            self.create_friendship(nick)

    def follow_selected(self):
        status = self.interface.current_status()
        if self.interface.is_retweet(status):
            nick = self.interface.origin_of_retweet(status)
        else:
            nick = status.user.screen_name
        self.create_friendship(nick)

    def unfollow(self):
        nick = NickEditor().content
        if nick:
            self.destroy_friendship(nick)       

    def unfollow_selected(self):
        nick = self.interface.current_status().user.screen_name
        self.destroy_friendship(nick)

    def create_friendship(self, nick):
        self.flash('follow', nick)
        try:
            self.api.CreateFriendship(nick)
        except TwitterError:
            self.error()

    def destroy_friendship(self, nick):
        self.flash('unfollow', nick)
        try:
            self.api.DestroyFriendship(nick)
        except TwitterError:
            self.error()

    def set_favorite(self):
        self.flash('favorite')
        status = self.interface.current_status()
        try:
            self.api.CreateFavorite(status)
        except TwitterError:
            self.error() 

    def destroy_favorite(self):
        self.flash('favorite_del')
        status = self.interface.current_status()
        try:
            self.api.DestroyFavorite(status)
        except TwitterError:
            self.error()

    def get_favorites(self):
        self.interface.change_buffer('favorite')

    def update_home_timeline(self):
        return self.api.GetFriendsTimeline(retweets=True)

    def user_timeline(self, myself=False):
        if not myself:
            nick = self.nick_box('Looking for someone?')
        else:
            nick = self.myself.screen_name
        if nick != False:
            if self.search_user != nick:
                self.interface.emptyDict('user')
            self.search_user = nick
            self.interface.change_buffer('user')

    def search(self):
        self.interface.buffer = 'search'
        self.search_word = SearchEditor('What should I search?').content
        try:
            self.interface.statuses['search'] = self.api.GetSearch(self.search_word)
            self.interface.change_buffer('search')
            if len(self.interface.statuses['search']) == 0:
                self.interface.flash = ['The search does not return any result', 'info']
        except:
            self.interface.flash = ['Failed with the search', 'warning']


    def flash(self, event, string=None):
        self.flash_message.event = event
        if string:
            self.flash_message.string = string
    
    def error(self):
        self.flash_message.warning()

class ApiPatch(Api):
    def PostRetweet(self, id):
        '''This code come from issue #130 on python-twitter tracker'''

        if not self._oauth_consumer:
            raise TwitterError("The twitter.Api instance must be authenticated.")
        try:
            if int(id) <= 0:
                raise TwitterError("'id' must be a positive number")
        except ValueError:
            raise TwitterError("'id' must be an integer")
        url = 'http://api.twitter.com/1/statuses/retweet/%s.json' % id
        json_data = self._FetchUrl(url, post_data={'dummy': None})
        data = json.loads(json_data)
        self._CheckForTwitterError(data)
        return Status.NewFromJsonDict(data)
