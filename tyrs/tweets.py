# -*- coding:utf-8 -*-

from twitter import Api, TwitterError
import urllib2
try:
    import json
except ImportError:
    import simplejson as json

class Tweets(Api):
 
    search_user = ''
    search_word = ''

    def setUi(self, ui):
        self.ui = ui

    def authentification(self, conf):
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
        self.setMyUser()

    def setMyUser(self):
        self.me = self.api.VerifyCredentials()

    def updateHomeTimeline (self):
        return self.api.GetFriendsTimeline(retweets=True)

    def postTweet (self, tweet, reply_to=None):
        self.api.PostUpdate(tweet, reply_to)

    def delete (self):
        statusId = self.ui.getCurrentStatus().GetId()
        # In case we want delete direct message, it will handle
        # with DestroyDirectMessage(id)
        try:
            self.api.api.DestroyStatus(statusId)
            self.ui.flash = ['Tweet destroyed successfully.', 'info']
        except:
            self.ui.flash = ['The tweet could not been destroyed.', 'warning']

    def createFriendship (self, pseudo):
        try:
            self.api.CreateFriendship(pseudo)
            self.ui.flash = ['You are now following %s' % pseudo, 'info']
        except:
            self.ui.flash = ['Failed to follow %s' % pseudo, 'warning']

    def destroyFriendship (self, pseudo):
        try:
            self.api.DestroyFriendship(pseudo)
            self.ui.flash = ['You have unfollowed %s' % pseudo, 'info']
        except:
            self.ui.flash = ['Failed to unfollow %s' % pseudo, 'warning']

    def setFavorite (self):
        status = self.ui.getCurrentStatus()
        try:
            self.api.CreateFavorite(status)
            self.ui.flash = ['The tweet is now in your favorite list', 'info']
        except:
            self.ui.flash = ['Could not set the current tweet as favorite', 'warning']

    def destroyFavorite (self):
        status = self.ui.getCurrentStatus()
        try:
            self.api.DestroyFavorite(status)
            self.ui.flash = ['The current favorite has been destroyed', 'info']
        except:
            self.ui.flash = ['Could not destroy the favorite tweet', 'warning']

    def getFavorites (self):
        self.ui.changeBuffer('favorite')

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
