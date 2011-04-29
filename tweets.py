import twitter

class Tweets:

    def authentification(self, conf):
        self.api = twitter.Api(consumer_key=conf.consumer_key,
                consumer_secret=conf.consumer_secret,
                access_token_key=conf.oauth_token,
                access_token_secret=conf.oauth_token_secret) 

    def updateHomeTimeline (self):
        return self.api.GetFriendsTimeline()
