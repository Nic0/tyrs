'''
@package   tyrs
@author    Nicolas Paris <nicolas.caen@gmail.com>
@license   GPLv3
'''

import re
import sys
import time
import signal                   # resize event
import curses

class uiTyrs:
    ''' All dispositions in the screen, and some logics for display tweet

    self.status:
        current:  the current tweet highlight, from the statuses list
        first:    first status displayed, from the status list, mean if we display the midle
                  of the list, the first won't be 0
        last:     the last tweet from statuses list
        count:    usefull, knowing if it's the last one on the statuses list
    self.api              The tweetter API (not directly the api, but the instance of Tweets in tweets.py)
    self.conf             The configuration file parsed in config.py
    self.maxyx            Array contain the window size [y, x]
    self.screen           Main screen (curse)
    self.statuses         List of all status retrieve
    self.current_y        Current line in the screen
    self.status           See explanation above
    self.resize_event     boleen if the window is resize
    self.regexRetweet     regex for retweet
    self.flash            [msg, type_msg]
                          Use like "session-flash", to display some information/warning messages
    self.refresh_token    Boleen to make sure we don't refresh timeline. Usefull to keep editing box on top
    '''

    status = {'current': 0, 'first': 0, 'last': 0, 'count': 0}
    statuses = []
    resize_event = False
    regexRetweet = re.compile('^RT @\w+:')
    flash = []
    refresh_token = False

    def __init__ (self, api, conf):
        '''
        @param api: instance of Tweets, will handle retrieve, sending tweets
        @param conf: contain all configuration parameters parsed
        '''
        self.api    = api
        self.conf   = conf
        signal.signal(signal.SIGWINCH, self.sigwinch_handler)
        self.initScreen()
        self.updateHomeTimeline()
        self.displayHomeTimeline()

    def initScreen (self):

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

        screen.border()
        screen.refresh()
        self.screen = screen

    def updateHomeTimeline (self):
        ''' Retrieves tweets, don't display them
        '''
        #try:
        self.flash = ['Updating timeline...', 'info']
        self.displayHomeTimeline()
        self.appendNewStatuses(self.api.updateHomeTimeline())
        self.displayHomeTimeline()
        self.countStatuses()
        #except:
            #self.flash = ["Couldn't retrieve tweets", 'warning']

    def appendNewStatuses (self, newStatuses):
        # Fresh new start.
        if self.statuses == []:
            self.statuses = newStatuses
        # This mean there is no new status, we just leave then.
        elif newStatuses[0] == self.statuses[0]:
            pass
        # Finally, we append tweets
        else:
            # backtotop is used to make sure we will display the first tweet
            # if the first status was displayed
            backToTop = False
            if self.statuses[0] == self.status['first']:
                backToTop = True
            
            for i in range(len(newStatuses)):
                if newStatuses[i] == self.statuses[0]:
                    self.statuses = newStatuses[:i] + self.statuses
                    self.status['current'] += len(newStatuses[:i])
            if backToTop:
                self.status['first'] = self.statuses[0]

    def countStatuses (self):
        self.status['count'] = len(self.statuses)

    def setFlash (self):
        msg = ' ' + self.flash[0] + ' '
        if self.flash[1] == 'warning':
            self.displayWarningMsg(msg)
        else:
            self.displayInfoMsg(msg)
        self.flash = []

    def displayWarningMsg (self, msg):
            self.screen.addstr(0, 3, msg,
                               curses.color_pair(self.conf.color_warning_msg) | curses.A_BOLD)

    def displayInfoMsg (self, msg):
            self.screen.addstr(0, 3, msg,
                               curses.color_pair(self.conf.color_info_msg) | curses.A_BOLD)

    def displayHomeTimeline (self):
        if not self.refresh_token:
            self.current_y = 1
            self.initScreen()
            for i in range(len(self.statuses)):
                if i >= self.status['first']:
                    self.displayStatus(self.statuses[i], i)
            if len(self.flash) != 0:
                self.setFlash()
            self.screen.refresh()

    def displayStatus (self, status, i):
        ''' Display a status (tweet) from top to bottom of the screen,
        depending on self.current_y, an array [status, panel] is return and
        will be stock in a array, to retreve status information (like id)'''

        # Check if we have a retweet
        self.isRetweet(status)

        # The content of the tweets is handle
        # text is needed for the height of a panel
        charset = sys.stdout.encoding
        text    = status.text.encode(charset)
        header  = self.getHeader(status)

        # We get size and where to display the tweet
        size = self.getSizeStatus(status)
        length = size['length']
        height = size['height']
        start_y = self.current_y
        start_x = 2

        # We leave if no more space left
        if start_y + height + 1 > self.maxyx[0]:
            return

        panel = curses.newpad(height, length)

        if self.conf.params_tweet_border == 1:
            panel.border(0)

        # Highlight (bold) the current status
        if self.status['current'] == i:
            panel.addstr(0,3, header,
                    curses.color_pair(self.conf.color_header)| curses.A_BOLD)
        else:
            panel.addstr(0,3, header, curses.color_pair(self.conf.color_header))

        self.displayText(text, panel, status)

        panel.refresh(0, 0, start_y, start_x,
            start_y + height, start_x + length)

        self.current_y = start_y + height
        self.status['last'] = i

    def displayText (self, text, panel, status):
        '''needed to cut words properly, as it would cut it in a midle of a
        world without. handle highlighting of '#' and '@' tags.'''

        #status.SetTruncated = False

        if status.rt:
            text = text.split(':')[1:]
            text = ':'.join(text)

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
                        panel.addstr(line, curent_x, word,
                                     curses.color_pair(self.conf.color_text))
                    except:
                        pass
                curent_x += len(word) + 1

    def getSizeStatus (self, status):
        length = self.maxyx[1] - 4
        height = len(status.text) / length + 3
        size = {'length': length, 'height': height}
        return size

    def getTime (self, status):
        '''Handle the time format given by the api with something more
        readeable
        @param  date: full iso time format
        @return string: readeable time
        '''

        if self.conf.params_relative_time== 1:
            return status.GetRelativeCreatedAt()
        else:
            hour = status.GetCreatedAt()
            hour = time.mktime(time.strptime(hour, '%a %b %d %H:%M:%S +0000 %Y')) - time.altzone
            hour = time.localtime(hour)
            hour = time.strftime('%H:%M', hour)

            return hour

    def getHeader (self, status):
        '''@return string'''
        charset = sys.stdout.encoding
        pseudo  = status.user.screen_name.encode(charset)
        time    = self.getTime(status).encode(charset)
        #name    = status.user.name.encode(charset)

        if status.rt and self.conf.params_retweet_by == 1:
            rtby = pseudo
            origin = self.originOfRetweet(status)
            header = ' %s (%s) RT by %s ' % (origin, time, rtby)
        else:
            header = " %s (%s) " % (pseudo, time)

        return header

    def isRetweet (self, status):
        status.rt = self.regexRetweet.match(status.GetText())
        return status.rt

    def originOfRetweet (self, status):
        origin = status.GetText()
        origin = origin[4:]
        origin = origin.split(':')[0]
        origin = str(origin)
        return origin

    # Last function call when quiting, restore some defaults params
    def tearDown (self):
        curses.endwin()
        curses.curs_set(1)

    # Resize event callback
    def sigwinch_handler (self, *dummy):
        self.resize_event = True

    def clearStatuses (self):
        self.statuses = [self.statuses[0]]
        self.countStatuses()
        self.status['current'] = 0

    def getCurrentStatus (self):
        return self.statuses[self.status['current']]

    def getUrls (self):
        return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', self.statuses[self.status['current']].text)
