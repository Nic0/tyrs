#import twitter
from twitter import Api
import urllib2
import simplejson

class Tweets(Api):

    search_user = ''
    search_word = ''

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
        json = self._FetchUrl(url, post_data={'dummy': None})
        data = simplejson.loads(json)
        self._CheckForTwitterError(data)
#        return Status.NewFromJsonDict(data)
