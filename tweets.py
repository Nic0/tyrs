import twitter

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
        return self.api.GetFriendsTimeline(retweets=True, include_entities=True)
