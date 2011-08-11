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
import logging
from urllib2 import URLError
from editor import *
from utils import cut_attag
from message import FlashMessage
from twitter import Api, TwitterError, Status

try:
    import json
except ImportError:
    import simplejson as json

class Tweets(object):
 
    def __init__(self):
        self.conf = tyrs.container['conf']
        self.timelines = tyrs.container['timelines']
        self.search_user = None
        self.search_word = None
        self.flash_message = FlashMessage()
    
    def set_interface(self):
        self.interface = tyrs.container['interface']

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
        self.conf.my_nick = self.myself.screen_name

    def tweet(self, data=None):
        tweet = TweetEditor(data).content
        if tweet:
            self.post_tweet(tweet)
        else:
            self.flash('empty')

    def post_tweet(self, tweet, reply_to=None):
        self.flash('tweet')
        try:
            return self.api.PostUpdate(tweet, reply_to)
        except TwitterError, e:
            self.error(e) 

    def retweet(self):
        self.flash('retweet')
        status = self.interface.current_status()
        try:
            self.api.PostRetweet(status.id)
        except TwitterError, e:
            self.error(e)

    def retweet_and_edit(self):
        status = self.interface.current_status()
        nick = status.user.screen_name
        data = 'RT @%s: %s' % (nick, status.text)
        self.tweet(data)

    def reply(self):
        status = self.interface.current_status()
        if hasattr(status, 'user'):
            nick = status.user.screen_name
        else:
            self.direct_message()
        data = '@' + nick + ' '
        tweet = TweetEditor(data).content
        if tweet:
            self.post_tweet(tweet, status.id)

    def destroy(self):
        self.flash('destroy')
        status = self.interface.current_status()
        try:
            self.api.DestroyStatus(status.id)
        except TwitterError, e:
            self.error(e)

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
        except TwitterError, e:
            self.error(e)

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
        except TwitterError, e:
            self.error(e)

    def destroy_friendship(self, nick):
        self.flash('unfollow', nick)
        try:
            self.api.DestroyFriendship(nick)
        except TwitterError, e:
            self.error(e)

    def set_favorite(self):
        self.flash('favorite')
        status = self.interface.current_status()
        try:
            self.api.CreateFavorite(status)
        except TwitterError, e:
            self.error(e) 

    def destroy_favorite(self):
        self.flash('favorite_del')
        status = self.interface.current_status()
        try:
            self.api.DestroyFavorite(status)
        except TwitterError, e:
            self.error(e)

    def get_favorites(self):
        self.interface.change_buffer('favorite')

    def update_timeline(self, timeline):
        '''
        Retrieves tweets, don't display them
        @param the buffer to retreive tweets
        '''

        logging.debug('updating "{0}" timeline'.format(timeline))
        try:
            statuses = self.retreive_statuses(timeline)
            self.timelines[timeline].append_new_statuses(statuses)

        except TwitterError, e:
            self.update_error(e)

    def update_error(self, err):
        logging.error('Updating issue: {0}'.format(err))
        self.flash_message.event = 'update'
        self.flash_message.level = 1
        self.interface.display_flash_message()

    def retreive_statuses(self, timeline, page=None):
        self.interface.display_update_msg()
        if timeline == 'home':
            statuses = self.api.GetFriendsTimeline(retweets=True, page=page)
        elif timeline == 'mentions':
            statuses = self.api.GetMentions(page=page)
        elif timeline == 'user_retweet':
            statuses = self.api.GetUserRetweets()
        elif timeline == 'search' and self.search_word != '':
            statuses = self.api.GetSearch(self.search_word, page=page)
        elif timeline == 'direct':
            statuses = self.api.GetDirectMessages(page=page)
        elif timeline == 'user' and self.search_user != '':
            statuses = self.load_user_public_timeline(page=page)
        elif timeline == 'favorite':
            statuses = self.api.GetFavorites(page=page)
        elif timeline == 'thread':
            statuses = self.get_thread()
        self.interface.erase_flash_message()

        return statuses

    def find_public_timeline(self):
        nick = NickEditor().content
        if nick and nick != self.search_user:
            self.change_search_user(nick)
            self.load_user_public_timeline()
            self.interface.change_buffer('user')

    def find_current_public_timeline(self):
        self.change_search_user(self.interface.current_status().user.screen_name)
        self.load_user_public_timeline()
        self.interface.change_buffer('user')

    def change_search_user(self, nick):
        self.search_user = nick
        self.timelines['user'].empty()

    def my_public_timeline(self):
        self.change_search_user(self.myself.screen_name)
        self.load_user_public_timeline()

    def load_user_public_timeline(self, page=None):
        if self.search_user:
            return self.api.GetUserTimeline(self.search_user,
                    include_rts=True, page=page)
        else:
            return []

    def get_thread(self):
        try:
            status = self.interface.current_status()
            self.timelines['thread'].empty()
            self.statuses = [status]
            self.build_thread(status)
            self.timelines['thread'].append_new_statuses(self.statuses)
            self.interface.change_buffer('thread')
        except IndexError:
            return []

    def build_thread(self, status):
        if status.in_reply_to_status_id:
            try:
                reply_to = self.api.GetStatus(status.in_reply_to_status_id)
                self.statuses.append(reply_to)
                self.build_thread(reply_to)
            except TwitterError:
                pass

    def search(self):
        self.search_word = SearchEditor().content
        self.flash('search', self.search_word)
        self.timelines['search'].empty()
        try:
            self.timelines['search'].append_new_statuses(self.api.GetSearch(self.search_word))
            self.interface.change_buffer('search')
        except TwitterError, e:
            self.error(e)


    def flash(self, event, string=None):
        self.flash_message.event = event
        if string:
            self.flash_message.string = string
    
    def error(self, err=None):
        logging.warning('Error catch: {0}'.format(err))
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
