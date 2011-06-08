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
import editBox
import urllib2
from twitter import Api, TwitterError

try:
    import json
except ImportError:
    import simplejson as json

class Tweets(Api):
 
    def __init__(self):
        self.conf = tyrs.container['conf']
        self.sear_user = ''
        self.search_word = ''

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

    def tweet(self, data, reply_to_id=None, dm=False):
        params = {'char': 200, 'width': 80, 'header': "What's up ?"}
        box = editBox.EditBox(self.interface, params, data, self.conf)
        if box.confirm:
            content = box.get_content()
            if not dm:
                self.post_tweet(content, reply_to_id)
                self.interface.flash = ['Tweet has been sent successfully.', "info"]
            else:
                # note in the DM case, we have a screen_name, and not the id
                self.api.PostDirectMessage(reply_to_id, content)
                self.interface.flash = ['The direct message has been sent.', 'info']

    def send_direct_message(self):
        ''' Two editing box, one for the name, and one for the content'''
        try:
            status = self.interface.current_status()
            try:
                pseudo = status.user.screen_name
            except:
                pseudo = status.sender_screen_name
        except:
            pseudo = ''

        pseudo = self.nick_box("Send a Direct Message to whom ?", pseudo)
        self.tweet(False, pseudo, True)

    def update_home_timeline(self):
        return self.api.GetFriendsTimeline(retweets=True)

    def post_tweet(self, tweet, reply_to=None):
        self.flash('tweet')
        try:
            self.api.PostUpdate(tweet, reply_to)
        except TwitterError:
            self.error() 

    def retweet(self):
        self.flash('retweet')
        status = self.interface.current_status()
        try:
            self.api.PostRetweet(status.GetId())
        except TwitterError:
            self.error()

    def retweet_and_edit(self):
        status = self.interface.current_status()
        name = status.user.screen_name
        data = 'RT @%s: %s' % (name, status.text)
        self.tweet(data)

    def reply(self):
        status = self.interface.current_status()
        reply_to_id = status.GetId()
        data = '@'+status.user.screen_name
        self.tweet(data, reply_to_id)

    def destroy(self):
        self.flash('destroy')
        status = self.interface.current_status()
        try:
            self.api.DestroyStatus(status.id)
        except TwitterError:
            self.error()

    def create_friendship(self, nick):
        self.flash('follow', nick)
        try:
            self.api.CreateFriendship(nick)
        except TwitterError:
            self.error()

    def destroy_friendship(self, nick):
        self.flash('unfollow', nick)
        try:
            self.api.DestroyFriendship(pseudo)
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
        self.search_word = self.nick_box('What should I search?')
        try:
            self.interface.statuses['search'] = self.api.GetSearch(self.search_word)
            self.interface.change_buffer('search')
            if len(self.interface.statuses['search']) == 0:
                self.interface.flash = ['The search does not return any result', 'info']
        except:
            self.interface.flash = ['Failed with the search', 'warning']

    def nick_box(self, header, pseudo=None):
        params = {'char': 40, 'width': 40, 'header': header}
        box = editBox.EditBox(self.interface, params, pseudo, self.conf)
        if box.confirm:
            return self.cut_attag(box.get_content())
        else:
            return False

    def follow_selected(self):
        status = self.interface.current_status()
        if self.interface.is_retweet(status):
            pseudo = self.interface.origin_of_retweet(status)
        else:
            pseudo = status.user.screen_name
        self.create_friendship(pseudo)

    def unfollow_selected(self):
        nick = self.interface.current_status().user.screen_name
        self.destroy_friendship(nick)

    def follow(self):
        nick = self.nick_box('Follow Someone ?')
        if nick != False:
            self.create_friendship(nick)

    def unfollow(self):
        nick = self.nick_box('Unfollow Someone ?')
        if nick != False:
            self.destroy_friendship(nick)       

    def cut_attag(self, name):
        if name[0] == '@':
            name = name[1:]
        return name

    def flash(self, event, string=None):
        self.interface.flash_message.event = event
        if string:
            self.interface.flash_message.string = string
    
    def error(self):
        self.interface.flash_message.warning()

class ApiPatch(Api):
    def PostRetweet(self, id):
        '''This code come from issue #130 on python-twitter tracker

        Retweet a tweet with the Retweet API

        The twitter.Api instance must be authenticated.

        Args:
        id: The numerical ID of the tweet you are retweeting

        Returns:
        A twitter.Status instance representing the retweet posted
        '''
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
#        return Status.NewFromJsonDict(data)
