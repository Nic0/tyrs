# -*- coding:utf-8 -*-

import tyrs
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

    def setUi(self, ui):
        self.ui = ui

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
        self.setMyUser()

    def setMyUser(self):
        self.me = self.api.VerifyCredentials()

    def tweet (self, data, reply_to_id=None, dm=False):
        params = {'char': 200, 'width': 80, 'header': "What's up ?"}
        box = editBox.EditBox(self.ui, params, data, self.conf)
        if box.confirm:
            try:
                content = box.getContent()
                if not dm:
                    self.postTweet(content, reply_to_id)
                    self.ui.flash = ['Tweet has been sent successfully.', "info"]
                else:
                    # note in the DM case, we have a screen_name, and not the id
                    self.api.PostDirectMessage(reply_to_id, content)
                    self.ui.flash = ['The direct message has been sent.', 'info']
            except:
               self.ui.flash = ["Couldn't send the tweet.", "warning"]

    def sendDirectMessage (self):
        ''' Two editing box, one for the name, and one for the content'''
        try:
            status = self.ui.getCurrentStatus()
            try:
                pseudo = status.user.screen_name
            except:
                pseudo = status.sender_screen_name
        except:
            pseudo = ''

        pseudo = self.pseudoBox("Send a Direct Message to whom ?", pseudo)
        self.tweet(False, pseudo, True)

    def updateHomeTimeline (self):
        return self.api.GetFriendsTimeline(retweets=True)

    def postTweet (self, tweet, reply_to=None):
        self.api.PostUpdate(tweet, reply_to)

    def retweet (self):
        status = self.ui.getCurrentStatus()
        try:
            self.api.api.PostRetweet(status.GetId())
            self.ui.flash = ['Retweet has been sent successfully.', 'info']
        except:
            self.ui.flash = ["Could not send the retweet.", 'warning']

    def retweetAndEdit (self):
        status = self.ui.getCurrentStatus()
        txt = status.text
        name = status.user.screen_name
        data = 'RT @%s: %s' % (name, txt)
        self.tweet(data)

    def reply (self):
        status = self.ui.getCurrentStatus()
        reply_to_id = status.GetId()
        data = '@'+status.user.screen_name
        self.tweet(data, reply_to_id)

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

    def userTimeline (self, myself=False):
        if not myself:
            nick = self.pseudoBox('Looking for someone?')
        else:
            nick = self.me.screen_name
        if nick != False:
            if self.search_user != nick:
                self.ui.emptyDict('user')
            self.search_user = nick
            self.ui.changeBuffer('user')

    def search (self):
        self.ui.buffer = 'search'
        self.search_word = self.pseudoBox('What should I search?')
        try:
            self.ui.statuses['search'] = self.api.GetSearch(self.api.search_word)
            self.ui.changeBuffer('search')
            if len(self.ui.statuses['search']) == 0:
                self.ui.flash = ['The search does not return any result', 'info']
        except:
            self.ui.flash = ['Failed with the search']

    def pseudoBox (self, header, pseudo=None):
        params = {'char': 40, 'width': 40, 'header': header}
        box = editBox.EditBox(self.ui, params, pseudo, self.conf)
        if box.confirm:
            return self.cutAtTag(box.getContent())
        else:
            return False

     def followSelected (self):
        status = self.ui.getCurrentStatus()
        if self.ui.isRetweet(status):
            pseudo = self.ui.originOfRetweet(status)
        else:
            pseudo = status.user.screen_name
        self.api.createFriendship(pseudo)

    def unfollowSelected (self):
        pseudo = self.ui.getCurrentStatus().user.screen_name
        self.api.destroyFriendship(pseudo)

    def follow (self):
        nick = self.pseudoBox('Follow Someone ?')
        if nick != False:
            self.api.createFriendship(nick)

    def unfollow (self):
        nick = self.pseudoBox('Unfollow Someone ?')
        if nick != False:
            self.api.destroyFriendship(nick)       

    def cutAtTag (self, name):
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
