'''
@package   tyrs
@author    Nicolas Paris <nicolas.caen@gmail.com>
'''

import sys
import curses
import curses.textpad

class uiTyrs:
    ''' All dispositions in the screen, and some logics for display tweet
    '''

    '''
    current:  the current tweet highlight, from the statuses list
    first:    first status displayed, from the status list, mean if we display the midle
              of the list, the first won't be 0
    last:     the last tweet from statuses list
    count:    usefull, knowing if it's the last one on the statuses list
    '''
    status = {'current': 0, 'first': 0, 'last': 0, 'count': 0}

    '''
    self.api          The tweetter API (not directly the api, but the instance of Tweets in tweets.py)
    self.conf         The configuration file parsed in config.py
    self.maxyx        Array contain the window size [y, x]
    self.screen       Main screen (curse)
    self.statuses     List of all status retrieve
    self.current_y    Current line in the screen
    self.status       See explanation above
    '''

    def __init__ (self, api, conf):
        '''
        @param api: instance of Tweets, will handle retrieve, sending tweets
        @param conf: contain all configuration parameters parsed
        '''
        self.api    = api
        self.conf   = conf
        screen = curses.initscr()

        curses.noecho()         # Dont print anything
        curses.cbreak()
        screen.keypad(1)        # Use of arrow keys
        curses.curs_set(0)      # Dont display cursor

        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, False)   # 1 black
        curses.init_pair(2, curses.COLOR_BLUE, False)    # 2 blue
        curses.init_pair(3, curses.COLOR_CYAN, False)    # 3 cyan
        curses.init_pair(4, curses.COLOR_GREEN, False)   # 4 green
        curses.init_pair(5, curses.COLOR_MAGENTA, False) # 5 magenta
        curses.init_pair(6, curses.COLOR_RED, False)     # 6 red
        curses.init_pair(7, curses.COLOR_WHITE, False)   # 7 white
        curses.init_pair(8, curses.COLOR_YELLOW, False)  # 8 yellow

        self.maxyx = screen.getmaxyx()

        screen.border(0)
        screen.refresh()
        self.screen = screen

    def updateHomeTimeline (self):
        ''' Retrieves tweets, don't display them
        '''
        self.statuses = self.api.updateHomeTimeline()
        self.countStatus()

        # /!\ DEBUG
        # curses.endwin()
        # for status in self.statuses:
        #     print status

    def countStatus (self):
        self.status['count'] = 0
        for status in self.statuses:
            self.status['count'] += 1

    def displayHomeTimeline (self):
        self.current_y = 1

        for i in range(len(self.statuses)):
            if i >= self.status['first']:
                self.displayStatus(self.statuses[i], i)

    def displayStatus (self, status, i):
        ''' Display a status (tweet) from top to bottom of the screen,
        depending on self.current_y, an array [status, panel] is return and
        will be stock in a array, to retreve status information (like id)'''
        
        # The content of the tweets is handle
        # text is needed for the height of a panel
        charset = sys.stdout.encoding
        text    = status.text.encode(charset)
        header  = self.getHeader(status)

        # We get size and where to display the tweet
        length = self.maxyx[1] - 4 
        height = len(text) / length + 3
        start_y = self.current_y
        start_x = 2

        # We leave if no more space left
        if start_y + height + 1 > self.maxyx[0]:
            return 

        panel = curses.newpad(height, length)

        if self.conf.params_tweet_border == 1:
            panel.border(0)

        if self.status['current'] == i:
            panel.addstr(0,3, header,
                    curses.color_pair(self.conf.color_header)| curses.A_BOLD)
        else:
            panel.addstr(0,3, header, curses.color_pair(self.conf.color_header))

        self.displayText(text, panel)

        panel.refresh(0, 0, start_y, start_x, 
            start_y + height, start_x + length)

        self.current_y = start_y + height
        self.status['last'] = i
        #tweet = {'status': status, 'panel': panel}
        #return tweet

    def displayText (self, text, panel):
        '''needed to cut words properly, as it would cut it in a midle of a
        world without. handle highlighting of '#' and '@' tags.'''
        words = text.split(' ')
        curent_x = 2
        line = 1
        for word in words:
            if curent_x + len(word) > self.maxyx[1] -6:
                line += 1
                curent_x = 2

            if word != '':
                if word[0] == '#':
                    panel.addstr(line, curent_x, word,
                                 curses.color_pair(self.conf.color_hashtag))
                elif word[0] == '@':
                    panel.addstr(line, curent_x, word,
                                 curses.color_pair(self.conf.color_attag))
                else:
                    try:
                        panel.addstr(line, curent_x, word)
                    except:
                        pass
                curent_x += len(word) + 1

    def getTime (self, date):
        '''Handle the time format given by the api with something more
        readeable
        @param  date: full iso time format
        @return string: readeable time
        '''
        time = date.split(' ')
        time = time[3]
        time = time.split(':')
        time = time[0:2]
        time = ':'.join(time)

        return time

    def getHeader (self, status):
        '''@return string'''
        charset = sys.stdout.encoding
        pseudo  = status.user.screen_name.encode(charset)
        time    = self.getTime(status.created_at).encode(charset)
        #name    = status.user.name.encode(charset)

        header = " %s (%s) " % (pseudo, time)
        
        return header

    def handleKeybinding(self):
        '''Should have all keybinding handle here'''
        while True:

            ch = self.screen.getch()
            # Down and Up key must act as a menu, and should navigate
            # throught every tweets like an item.
            #
            # MOVE DOWN
            #
            if ch == ord(self.conf.keys_down) or ch == curses.KEY_DOWN:
                # if we have some more tweets to display
                if self.status['current'] < self.status['count'] - 1:
                    if self.status['current'] == self.status['last']:
                        self.status['first'] += 1
                    self.status['current'] += 1
                    self.displayHomeTimeline()
            #        
            # MOVE UP
            #
            elif ch == ord(self.conf.keys_up) or ch == curses.KEY_UP:
                # the current tweet must not be the first one of the statuses
                # list
                if self.status['current'] > 0:
                    # if we need to move up the list to display
                    if self.status['current'] == self.status['first']:
                        self.status['first'] -= 1
                    self.status['current'] -= 1
                    self.displayHomeTimeline()

            #        
            # TWEET
            #        
            elif ch == ord(self.conf.keys_tweet):
                box = TweetBox(self.screen)
                tweet = box.getTweet()
                self.api.postTweet(tweet)


            #
            # QUIT
            #
            # 27 corresponding to the ESC, couldn't find a KEY_* corresponding
            elif ch == ord(self.conf.keys_quit) or ch == 27:
                break

    # Last function call when quiting, restore some defaults params 
    def tearDown (self):
        curses.endwin()
        curses.curs_set(1)

class TweetBox:

    def __init__(self, screen):

        win = screen.subwin(5, 60, 5, 10)

        tweet = ''
        curses.echo()

        while True:

            ch = win.getch()
            if ch == 10:
                break
            chr(ch)
            tweet +=  chr(ch)

        curses.noecho()
        self.tweet = tweet

    def getTweet (self):
        return self.tweet

    def validate (self, ch):
        if ch == 10:            # 10 corresponding to ENTER
            ch = curses.ascii.BEL
        return ch
