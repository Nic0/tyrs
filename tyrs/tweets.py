# -*- coding: utf-8 -*-
'''
@module    tweets
@author    Nicolas Paris <nicolas.caen@gmail.com>
@license   GPLv3
'''
import tyrs
import editBox
import urllib2
from twitter import Api, TwitterError

try:
    import json
except ImportError:
    import simplejson as json

class Tweets(Api):
 
    search_user = ''
    search_word = ''

    def __init__ (self):
        self.conf = tyrs.container['conf']

    def set_ui(self, ui):
        self.interface = ui

    def authentification(self):
        conf = self.conf
        if conf.service == 'identica':
            url = conf.base_url
        else:
            url = None

        self.api = ApiPatch(
            conf.token[conf.service]['consumer_key'],
            conf.token[conf.service]['consumer_secret'],
            conf.oauth_token,
            conf.oauth_token_secret,
            base_url=url
        )
        self.set_myself()

    def set_myself(self):
        self.myself = self.api.VerifyCredentials()

    def tweet (self, data, reply_to_id=None, dm=False):
        params = {'char': 200, 'width': 80, 'header': "What's up ?"}
        box = editBox.EditBox(self.interface, params, data, self.conf)
        if box.confirm:
            try:
                content = box.get_content()
                if not dm:
                    self.post_tweet(content, reply_to_id)
                    self.interface.flash = ['Tweet has been sent successfully.', "info"]
                else:
                    # note in the DM case, we have a screen_name, and not the id
                    self.api.PostDirectMessage(reply_to_id, content)
                    self.interface.flash = ['The direct message has been sent.', 'info']
            except:
               self.interface.flash = ["Couldn't send the tweet.", "warning"]

    def send_direct_message (self):
        ''' Two editing box, one for the name, and one for the content'''
        try:
            status = self.interface.get_current_status()
            try:
                pseudo = status.user.screen_name
            except:
                pseudo = status.sender_screen_name
        except:
            pseudo = ''

        pseudo = self.nick_box("Send a Direct Message to whom ?", pseudo)
        self.tweet(False, pseudo, True)

    def update_home_timeline (self):
        return self.api.GetFriendsTimeline(retweets=True)

    def post_tweet (self, tweet, reply_to=None):
        self.api.PostUpdate(tweet, reply_to)

    def retweet (self):
        status = self.interface.get_current_status()
        try:
            self.api.PostRetweet(status.GetId())
            self.interface.flash = ['Retweet has been sent successfully.', 'info']
        except:
            self.interface.flash = ["Could not send the retweet.", 'warning']

    def retweet_and_edit (self):
        status = self.interface.get_current_status()
        txt = status.text
        name = status.user.screen_name
        data = 'RT @%s: %s' % (name, txt)
        self.tweet(data)

    def reply (self):
        status = self.interface.get_current_status()
        reply_to_id = status.GetId()
        data = '@'+status.user.screen_name
        self.tweet(data, reply_to_id)

    def delete (self):
        statusId = self.interface.get_current_status().GetId()
        # In case we want delete direct message, it will handle
        # with DestroyDirectMessage(id)
        try:
            self.api.DestroyStatus(statusId)
            self.interface.flash = ['Tweet destroyed successfully.', 'info']
        except:
            self.interface.flash = ['The tweet could not been destroyed.', 'warning']

    def create_friendship (self, pseudo):
        try:
            self.api.CreateFriendship(pseudo)
            self.interface.flash = ['You are now following %s' % pseudo, 'info']
        except:
            self.interface.flash = ['Failed to follow %s' % pseudo, 'warning']

    def destroy_friendship (self, pseudo):
        try:
            self.api.DestroyFriendship(pseudo)
            self.interface.flash = ['You have unfollowed %s' % pseudo, 'info']
        except:
            self.interface.flash = ['Failed to unfollow %s' % pseudo, 'warning']

    def set_favorite (self):
        status = self.interface.get_current_status()
        try:
            self.api.CreateFavorite(status)
            self.interface.flash = ['The tweet is now in your favorite list', 'info']
        except:
            self.interface.flash = ['Could not set the current tweet as favorite', 'warning']

    def destroy_favorite (self):
        status = self.interface.get_current_status()
        try:
            self.api.DestroyFavorite(status)
            self.interface.flash = ['The current favorite has been destroyed', 'info']
        except:
            self.interface.flash = ['Could not destroy the favorite tweet', 'warning']

    def get_favorites (self):
        self.interface.change_buffer('favorite')

    def user_timeline (self, myself=False):
        if not myself:
            nick = self.nick_box('Looking for someone?')
        else:
            nick = self.myself.screen_name
        if nick != False:
            if self.search_user != nick:
                self.interface.emptyDict('user')
            self.search_user = nick
            self.interface.change_buffer('user')

    def search (self):
        self.interface.buffer = 'search'
        self.search_word = self.nick_box('What should I search?')
        try:
            self.interface.statuses['search'] = self.api.GetSearch(self.search_word)
            self.interface.change_buffer('search')
            if len(self.interface.statuses['search']) == 0:
                self.interface.flash = ['The search does not return any result', 'info']
        except:
            self.interface.flash = ['Failed with the search', 'warning']

    def nick_box (self, header, pseudo=None):
        params = {'char': 40, 'width': 40, 'header': header}
        box = editBox.EditBox(self.interface, params, pseudo, self.conf)
        if box.confirm:
            return self.cat_attag(box.getContent())
        else:
            return False

    def follow_selected (self):
        status = self.interface.get_current_status()
        if self.interface.is_retweet(status):
            pseudo = self.interface.origin_of_retweet(status)
        else:
            pseudo = status.user.screen_name
        self.create_friendship(pseudo)

    def unfollow_selected (self):
        pseudo = self.interface.get_current_status().user.screen_name
        self.destroy_friendship(pseudo)

    def follow (self):
        nick = self.nick_box('Follow Someone ?')
        if nick != False:
            self.create_friendship(nick)

    def unfollow (self):
        nick = self.nick_box('Unfollow Someone ?')
        if nick != False:
            self.destroy_friendship(nick)       

    def cat_attag (self, name):
        if name[0] == '@':
            name = name[1:]
        return name

class ApiPatch (Api):
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
