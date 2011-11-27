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
import tyrs
import urwid
import logging
import urllib2
import oauth2 as oauth
from utils import encode
from help import help_bar
from urllib2 import URLError
from message import FlashMessage
from httplib import BadStatusLine
from twitter import Api, TwitterError, Status, _FileCache

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
        proxify = self.get_proxy()
        self.api = ApiPatch(
            self.conf.token[self.conf.service]['consumer_key'],
            self.conf.token[self.conf.service]['consumer_secret'],
            self.conf.oauth_token,
            self.conf.oauth_token_secret,
            base_url=url,
            proxy=proxify
        )
        self.set_myself()

    def get_base_url(self):
        url = None
        if self.conf.service == 'identica':
            url = self.conf.base_url

        return url

    def get_proxy(self):
        proxy = self.conf.params['proxy']
        if proxy:
            return {
                'http': 'http://{0}'.format(proxy),
                'https': 'https://{0}'.format(proxy),
            }
        else:
            return {}

    def set_myself(self):
        self.myself = self.api.VerifyCredentials()
        self.conf.my_nick = self.myself.screen_name

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
        self.interface.edit_status('tweet', data)

    #def reply(self):
        #status = self.interface.current_status()
        #if hasattr(status, 'user'):
            #nick = status.user.screen_name
        #else:
            #self.direct_message()
        #data = '@' + nick + ' '
        #tweet = TweetEditor(data).content
        #if tweet:
            #self.post_tweet(tweet, status.id)

    def destroy(self):
        self.flash('destroy')
        status = self.interface.current_status()
        try:
            self.api.DestroyStatus(status.id)
        except TwitterError, e:
            self.error(e)

    #FIXME!
    def direct_message(self):
        ''' Two editing box, one for the name, and one for the content'''
        nick = self.nick_for_direct_message()
        tweet = TweetEditor().content
        if tweet:
            self.send_direct_message(nick, tweet)

    #FIXME!
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
        self.interface.edit_status('follow')

    def follow_selected(self):
        status = self.interface.current_status()
        if self.interface.is_retweet(status):
            nick = self.interface.origin_of_retweet(status)
        else:
            nick = status.user.screen_name
        self.create_friendship(nick)

    #def unfollow(self):
        #nick = NickEditor().content
        #if nick:
            #self.destroy_friendship(nick)

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
            timeline = self.timelines[timeline]
            timeline.append_new_statuses(statuses)
            if timeline.unread and self.conf.params['beep']:
                self.interface.beep()

        except TwitterError, e:
            self.update_error(e)
        except BadStatusLine, e:
            self.update_error(e)
        except ValueError, e:
            self.update_error(e)
        except URLError, e:
            self.update_error(e)

    def update_error(self, err):
        logging.error('Updating issue: {0}'.format(err))
        self.flash_message.event = 'update'
        self.flash_message.level = 1
        self.interface.display_flash_message()

    def retreive_statuses(self, timeline, page=None):
        self.flash_message.event = 'update'
        self.flash_message.level = 0
        self.interface.display_flash_message()
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

    def find_public_timeline(self, nick):
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

    def search(self, content):
        self.search_word = content
        self.flash('search', self.search_word)
        self.timelines['search'].empty()
        try:
            self.timelines['search'].append_new_statuses(self.api.GetSearch(self.search_word))
            self.interface.change_buffer('search')
        except TwitterError, e:
            self.error(e)

    def tweet_done(self, content):
        self.clean_edit()
        urwid.disconnect_signal(self, self.interface.foot, 'done', self.tweet_done)
        if content:
            self.post_tweet(encode(content))

    def reply_done(self, content):
        self.clean_edit()
        urwid.disconnect_signal(self, self.interface.foot, 'done', self.reply_done)
        if content:
            self.post_tweet(encode(content), self.interface.current_status().id)

    def follow_done(self, content):
        self.clean_edit()
        urwid.disconnect_signal(self, self.interface.foot, 'done', self.follow_done)
        if content:
            self.create_friendship(content)

    def unfollow_done(self, content):
        self.clean_edit()
        urwid.disconnect_signal(self, self.interface.foot, 'done', self.unfollow_done)
        if content:
            self.destroy_friendship(content)

    def search_done(self, content):
        self.clean_edit()
        urwid.disconnect_signal(self, self.interface.foot, 'done', self.search_done)
        if content:
            self.search(encode(content))

    def public_done(self, content):
        self.clean_edit()
        urwid.disconnect_signal(self, self.interface.foot, 'done', self.public_done)
        if content:
            self.find_public_timeline(content)

    def clean_edit(self):
        footer = help_bar()
        self.interface.main_frame.set_focus('body')
        self.interface.main_frame.set_footer(footer)

    def flash(self, event, string=None):
        self.flash_message.event = event
        if string:
            self.flash_message.string = string

    def error(self, err=None):
        logging.warning('Error catch: {0}'.format(err))
        self.flash_message.warning()

DEFAULT_CACHE = object()

class ApiPatch(Api):

    def __init__(self,
               consumer_key=None,
               consumer_secret=None,
               access_token_key=None,
               access_token_secret=None,
               input_encoding=None,
               request_headers=None,
               cache=DEFAULT_CACHE,
               shortner=None,
               base_url=None,
               use_gzip_compression=False,
               debugHTTP=False,
               proxy={}
              ):


        self.SetCache(cache)
        self._urllib         = urllib2
        self._cache_timeout  = Api.DEFAULT_CACHE_TIMEOUT
        self._input_encoding = input_encoding
        self._use_gzip       = use_gzip_compression
        self._debugHTTP      = debugHTTP
        self._oauth_consumer = None
        self._proxy = proxy

        self._InitializeRequestHeaders(request_headers)
        self._InitializeUserAgent()
        self._InitializeDefaultParameters()

        if base_url is None:
            self.base_url = 'https://api.twitter.com/1'
        else:
            self.base_url = base_url

        if consumer_key is not None and (access_token_key is None or
                                         access_token_secret is None):
            print >> sys.stderr, 'Twitter now requires an oAuth Access Token for API calls.'
            print >> sys.stderr, 'If your using this library from a command line utility, please'
            print >> sys.stderr, 'run the the included get_access_token.py tool to generate one.'

            raise TwitterError('Twitter requires oAuth Access Token for all API access')

        self.SetCredentials(consumer_key, consumer_secret, access_token_key, access_token_secret)

    def _FetchUrl(self,
                url,
                post_data=None,
                parameters=None,
                no_cache=None,
                use_gzip_compression=None):


    # Build the extra parameters dict
      extra_params = {}
      if self._default_params:
        extra_params.update(self._default_params)
      if parameters:
        extra_params.update(parameters)

      if post_data:
        http_method = "POST"
      else:
        http_method = "GET"

      if self._debugHTTP:
        _debug = 1
      else:
        _debug = 0

      http_handler = self._urllib.HTTPHandler(debuglevel=_debug)
      https_handler = self._urllib.HTTPSHandler(debuglevel=_debug)
      proxy_handler = self._urllib.ProxyHandler(self._proxy)

      opener = self._urllib.OpenerDirector()
      opener.add_handler(http_handler)
      opener.add_handler(https_handler)

      if self._proxy:
          opener.add_handler(proxy_handler)

      if use_gzip_compression is None:
        use_gzip = self._use_gzip
      else:
        use_gzip = use_gzip_compression

    # Set up compression
      if use_gzip and not post_data:
        opener.addheaders.append(('Accept-Encoding', 'gzip'))

      if self._oauth_consumer is not None:
        if post_data and http_method == "POST":
          parameters = post_data.copy()

        req = oauth.Request.from_consumer_and_token(self._oauth_consumer,
                                                  token=self._oauth_token,
                                                  http_method=http_method,
                                                  http_url=url, parameters=parameters)

        req.sign_request(self._signature_method_hmac_sha1, self._oauth_consumer, self._oauth_token)

        headers = req.to_header()

        if http_method == "POST":
          encoded_post_data = req.to_postdata()
        else:
          encoded_post_data = None
          url = req.to_url()
      else:
        url = self._BuildUrl(url, extra_params=extra_params)
        encoded_post_data = self._EncodePostData(post_data)

      # Open and return the URL immediately if we're not going to cache
      if encoded_post_data or no_cache or not self._cache or not self._cache_timeout:
        response = opener.open(url, encoded_post_data)
        url_data = self._DecompressGzippedResponse(response)
        opener.close()
      else:
      # Unique keys are a combination of the url and the oAuth Consumer Key
        if self._consumer_key:
          key = self._consumer_key + ':' + url
        else:
          key = url

      #TODO I turn off the cache as it bugged all the app,
      #but I need to see what's wrong with that.
      # See if it has been cached before
      #last_cached = self._cache.GetCachedTime(key)

      # If the cached version is outdated then fetch another and store it
      #if not last_cached or time.time() >= last_cached + self._cache_timeout:
        try:
          response = opener.open(url, encoded_post_data)
          url_data = self._DecompressGzippedResponse(response)
        #self._cache.Set(key, url_data)
        except urllib2.HTTPError, e:
          print e
        opener.close()
    #else:
      #url_data = self._cache.Get(key)

    # Always return the latest version
      return url_data

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

    def GetCachedTime(self,key):
        path = self._GetPath(key)
        if os.path.exists(path):
            return os.path.getmtime(path)
        else:
            return None

    def SetCache(self, cache):
        '''Override the default cache.  Set to None to prevent caching.

        Args:
          cache:
            An instance that supports the same API as the twitter._FileCache
        '''
        if cache == DEFAULT_CACHE:
            self._cache = _FileCache()
        else:
            self._cache = cache
