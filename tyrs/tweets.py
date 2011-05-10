import twitter
import urllib2

class Tweets:

    def authentification(self, conf):
        self.api = twitter.Api(consumer_key=conf.consumer_key,
                consumer_secret=conf.consumer_secret,
                access_token_key=conf.oauth_token,
                access_token_secret=conf.oauth_token_secret)

    def updateHomeTimeline (self):
        ''' include_entities return some varius metadata in a structure, not use
        yet, but it might be usefull
        '''
        try:
            statuses = self.api.GetFriendsTimeline(retweets=True)
            return statuses
        except urllib2.URLError:
            print 'Could\'t get statuses, network is down ?'

    def postTweet (self, tweet, reply_to=None):
        try:
            self.api.PostUpdate(tweet)
        except:
            print 'ERROR!! impossible to send: \'%s\'' % tweet
