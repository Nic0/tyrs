#! -*- coding: utf-8 -*-
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
import curses.wrapper

class uiTyrs:
    ''' All dispositions in the screen, and some logics for display tweet

    self.status:  It's use mainly for display purpose
        current:    the current tweet highlight, from the statuses list
        first:      first status displayed, from the status list, mean if we display the midle
                    of the list, the first won't be 0
        last:       the last tweet from statuses list
    self.count            Keep the count of each statuses list
    self.api              The tweetter API (not directly the api, but the instance of Tweets in tweets.py)
    self.conf             The configuration file parsed in config.py
    self.maxyx            Array contain the window size [y, x]
    self.screen           Main screen (curse)
    self.last_read        keep the ID of the status for each lists of statuses
    self.unread           keep the count of tweet that haven't been read in other buffer, usefull to see active buffer
    self.statuses         4 lists for each buffer containing all status in each list, the name of each list
                          is the name of the buffer
    self.current_y        Current line in the screen
    self.resize_event     boleen if the window is resize
    self.regexRetweet     regex for retweet
    self.flash            [msg, type_msg]
                          Use like "session-flash", to display some information/warning messages
    self.refresh_token    Boleen to make sure we don't refresh timeline. Usefull to keep editing box on top
    self.buffer           The current buffer we're looking at, (home, mentions, direct search)
    '''

    status           = {'current': 0, 'first': 0, 'last': 0}
    statuses         = {}
    count            = {}
    unread           = {}
    last_read        = {}
    resize_event     = False
    regexRetweet     = re.compile('^RT @\w+:')
    flash = []
    refresh_token    = False
    buffer           = 'home'

    def __init__ (self, api, conf):
        '''
        @param api: instance of Tweets, will handle retrieve, sending tweets
        @param conf: contain all configuration parameters parsed
        '''
        self.api    = api
        self.conf   = conf
        # resize event
        signal.signal(signal.SIGWINCH, self.sigwinch_handler)
        # startup the ncurses mode
        self.initScreen()
        # initialize statuses, count, unread...
        self.initDict()
        # first update of home timeline
        self.updateTimeline('home')
        self.displayTimeline()

    def initScreen (self):

        screen = curses.initscr()
        curses.noecho()         # Dont print anything
        curses.cbreak()
        screen.keypad(1)        # Use of arrow keys
        curses.curs_set(0)      # Dont display cursor
        curses.meta(1)          # allow 8bits inputs
        self.initColors()
        self.maxyx = screen.getmaxyx()
        screen.border()

        screen.refresh()
        self.screen = screen

    def initColors (self):
        curses.start_color()

        if self.conf.params['transparency']:
            curses.use_default_colors()
            bgcolor = -1
        else:
            bgcolor = False

        # Setup colors rgb
        if curses.can_change_color():
            for i in range(len(self.conf.color_set)):
                if not self.conf.color_set[i]:
                    continue
                else:
                    rgb = self.conf.color_set[i]
                    curses.init_color(i, rgb[0], rgb[1], rgb[2])

        curses.init_pair(0, curses.COLOR_BLACK, bgcolor)    # 0 black
        curses.init_pair(1, curses.COLOR_RED, bgcolor)      # 1 red
        curses.init_pair(2, curses.COLOR_GREEN, bgcolor)    # 2 green
        curses.init_pair(3, curses.COLOR_YELLOW, bgcolor)   # 3 yellow
        curses.init_pair(4, curses.COLOR_BLUE, bgcolor)     # 4 blue
        curses.init_pair(5, curses.COLOR_MAGENTA, bgcolor)  # 5 magenta
        curses.init_pair(6, curses.COLOR_CYAN, bgcolor)     # 6 cyan
        curses.init_pair(7, curses.COLOR_WHITE, bgcolor)    # 7 white

    def initDict (self):
        buffers = ('home', 'mentions', 'direct', 'search')
        for buffer in buffers:
            self.statuses[buffer]   = []
            self.unread[buffer]     = 0
            self.count[buffer]      = 0
            self.last_read[buffer]  = 0

    def updateTimeline (self, buffer):
        ''' Retrieves tweets, don't display them
        '''
        try:
            if not self.refresh_token:
                self.displayUpdateMsg()

            if buffer == 'home':
                self.appendNewStatuses(self.api.updateHomeTimeline(), buffer)
            elif buffer == 'mentions':
                self.appendNewStatuses(self.api.api.GetMentions(), buffer)
            elif buffer == 'search':
                self.appendNewStatuses(self.api.api.GetSearch(self.api.search_word), buffer)
            elif buffer == 'direct':
                self.appendNewStatuses(self.api.api.GetDirectMessages(), buffer)
            #TODO does it realy need to display the timeline here ?!
            self.displayTimeline()
        except:
            self.flash = ["Couldn't retrieve tweets", 'warning']
        self.countStatuses(buffer)
        self.countUnread(buffer)

    def appendNewStatuses (self, newStatuses, buffer):
        # Fresh new start.
        if self.statuses[buffer] == []:
            self.statuses[buffer] = newStatuses
        # This mean there is no new status, we just leave then.
        # TODO, this might meen we didn't fetch enought statuses
        elif newStatuses[0].id == self.statuses[buffer][0].id:
            pass
        # Finally, we append tweets
        else:
            for i in range(len(newStatuses)):
                if newStatuses[i].id == self.statuses[buffer][0].id:
                    self.statuses[buffer] = newStatuses[:i] + self.statuses[buffer]
                    # we don't want to move our current position
                    # if the update is in another buffer
                    if buffer == self.buffer:
                        self.status['current'] += len(newStatuses[:i])

    def countStatuses (self, buffer):
        self.count[buffer] = len(self.statuses[buffer])

    def countUnread (self, buffer):
        self.unread[buffer] = 0
        for i in range(len(self.statuses[buffer])):
            if self.statuses[buffer][i].id == self.last_read[buffer]:
                break
            self.unread[buffer] += 1
        self.unread[self.buffer] = 0

    def displayFlash (self):
        msg = ' ' + self.flash[0] + ' '
        if self.flash[1] == 'warning':
            self.displayWarningMsg(msg)
        else:
            self.displayInfoMsg(msg)
        self.flash = []

    def displayUpdateMsg (self):
        self.displayInfoMsg(' Updating timeline... ')
        self.screen.refresh()

    def displayWarningMsg (self, msg):
        self.screen.addstr(0, 3, msg, self.getColor('warning_msg'))

    def displayInfoMsg (self, msg):
        self.screen.addstr(0, 3, msg, self.getColor('info_msg'))


    def displayRedrawScreen (self):
        self.screen.erase()
        self.displayTimeline ()

    def displayTimeline (self):
        # It might have no tweets yet, we try to retrieve some then
        if len(self.statuses[self.buffer]) == 0:
            self.updateTimeline(self.buffer)

        if not self.refresh_token:
            # The first status become the last_read for this buffer
            if len(self.statuses[self.buffer]) > 0:
                self.last_read[self.buffer] = self.statuses[self.buffer][0].id

            self.current_y = 1
            self.initScreen()
            for i in range(len(self.statuses[self.buffer])):
                if i >= self.status['first']:
                    br = self.displayStatus(self.statuses[self.buffer][i], i)
                    if not br:
                        break
            if len(self.flash) != 0:
                self.displayFlash()
            if self.status['current'] > self.status['last']:
                self.status['current'] = self.status['last']
                self.displayTimeline()

            if self.conf.params['activities']:
                self.displayActivity()
            self.screen.refresh()

    def displayActivity (self):

        buffer = ['home', 'mentions', 'direct', 'search' ]
        max = self.screen.getmaxyx()
        max_x = max[1]
        self.screen.addstr(0, max_x - 20, ' ')
        for b in buffer:
            self.displayBufferActivities(b)
            self.displayCounterActivities(b)

    def displayBufferActivities (self, buffer):
        display = { 'home': 'H:', 'mentions': 'M:', 'direct': 'D:', 'search': 'S:' }
        if self.buffer == buffer:
            self.screen.addstr(display[buffer], self.getColor('current_tab'))
        else:
            self.screen.addstr(display[buffer], self.getColor('other_tab'))

    def displayCounterActivities (self, buffer):
        if self.unread[buffer] == 0:
            color = 'read'
        else:
            color = 'unread'

        self.screen.addstr('%s ' % str(self.unread[buffer]), self.getColor(color))

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
            return False

        panel = curses.newpad(height, length)

        if self.conf.params['tweet_border'] == 1:
            panel.border(0)

        # Highlight the current status
        if self.status['current'] == i:
            panel.addstr(0,3, header, self.getColor('current_tweet'))
        else:
            panel.addstr(0, 3, header, self.getColor('header'))

        self.displayText(text, panel, status)

        panel.refresh(0, 0, start_y, start_x,
            start_y + height, start_x + length)

        self.current_y = start_y + height
        self.status['last'] = i

        return True

    def displayText (self, text, panel, status):
        '''needed to cut words properly, as it would cut it in a midle of a
        world without. handle highlighting of '#' and '@' tags.'''

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
                # The word is an HASHTAG ? '#'
                if word[0] == '#':
                    panel.addstr(line, curent_x, word, self.getColor('hashtag'))
                # Or is it an 'AT TAG' ? '@'
                elif word[0] == '@':
                    name = self.api.me.screen_name
                    # The AT TAG is,  @myself
                    if word == '@'+name or word == '@'+name+':':
                        panel.addstr(line, curent_x, word, self.getColor('highlight'))
                    # @anyone
                    else:
                        panel.addstr(line, curent_x, word, self.getColor('attag'))
                # It's just a normal word
                else:
                    try:
                        panel.addstr(line, curent_x, word, self.getColor('text'))
                    except:
                        pass
                curent_x += len(word) + 1

                # We check for ugly empty spaces
                while panel.inch(line, curent_x -1) == ord(' ') and panel.inch(line, curent_x -2) == ord(' '):
                    curent_x -= 1


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
        if self.conf.params['relative_time'] == 1 and self.buffer != 'direct':
            hour =  status.GetRelativeCreatedAt()
        else:
            hour = time.gmtime(status.GetCreatedAtInSeconds() - time.altzone)
            hour = time.strftime('%H:%M', hour)

        return hour

    def getHeader (self, status):
        '''@return string'''
        charset = sys.stdout.encoding
        try:
            pseudo  = status.user.screen_name.encode(charset)
        except:
            # Only for the Direct Message case
            pseudo = status.sender_screen_name.encode(charset)
        time    = self.getTime(status)
        #name    = status.user.name.encode(charset)

        if status.rt and self.conf.params['retweet_by'] == 1:
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
    def tearDown (self, *dummy):
        self.screen.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.curs_set(1)
        curses.endwin()

    # Resize event callback
    def sigwinch_handler (self, *dummy):
        self.resize_event = True

    def clearStatuses (self):
        self.statuses[self.buffer] = [self.statuses[self.buffer][0]]
        self.countStatuses(self.buffer)
        self.status['current'] = 0

    def getCurrentStatus (self):
        return self.statuses[self.buffer][self.status['current']]

    def getUrls (self):
        return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', self.statuses[self.buffer][self.status['current']].text)

    def getColor (self, color):
        cp = curses.color_pair(self.conf.colors[color]['c'])
        if self.conf.colors[color]['b']:
            cp |= curses.A_BOLD

        return cp
