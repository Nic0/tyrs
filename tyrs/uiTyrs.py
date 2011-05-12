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
import editBox


class uiTyrs:
    ''' All dispositions in the screen, and some logics for display tweet

    self.status:
        current:  the current tweet highlight, from the statuses list
        first:    first status displayed, from the status list, mean if we display the midle
                  of the list, the first won't be 0
        last:     the last tweet from statuses list
        count:    usefull, knowing if it's the last one on the statuses list
    self.api          The tweetter API (not directly the api, but the instance of Tweets in tweets.py)
    self.conf         The configuration file parsed in config.py
    self.maxyx        Array contain the window size [y, x]
    self.screen       Main screen (curse)
    self.statuses     List of all status retrieve
    self.current_y    Current line in the screen
    self.status       See explanation above
    self.resize_event boleen if the window is resize
    self.regexRetweet regex for retweet
    self.flash        [boleen, type_msg, msg]
                      Use like "session-flash", to display some information/warning messages
    '''

    status = {'current': 0, 'first': 0, 'last': 0, 'count': 0}
    statuses = []
    resize_event = False
    regexRetweet = re.compile('^RT @\w+:')
    flash = [False]
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
        try:
            self.flash = [True, 'info', 'Updating timeline...']
            self.displayHomeTimeline()
            self.appendNewStatuses(self.api.updateHomeTimeline())
            self.countStatuses()
        except:
            self.flash = [True, 'warning', "Couldn't retrieve tweets"]

    def appendNewStatuses (self, newStatuses):
        # Fresh new start.
        if self.statuses == []:
            self.statuses = newStatuses
        # This mean there is no new status, we just leave then.
        elif newStatuses[0] == self.statuses[0]:
            pass
        # Finally, we append tweets
        else:
            for i in range(len(newStatuses)):
                if newStatuses[i] == self.statuses[0]:
                    self.statuses = newStatuses[:i] + self.statuses

    def countStatuses (self):
        self.status['count'] = len(self.statuses)

    def setFlash (self):
        if self.flash[1] == 'warning':
            self.displayWarningMsg(self.flash[2])
        else:
            self.displayInfoMsg(self.flash[2])
        self.flash[0] = False

    def displayWarningMsg (self, msg):
            self.screen.addstr(0, 3, msg,
                               curses.color_pair(self.conf.color_warning_msg) | curses.A_BOLD)

    def displayInfoMsg (self, msg):
            self.screen.addstr(0, 3, msg,
                               curses.color_pair(self.conf.color_info_msg) | curses.A_BOLD)

    def displayHomeTimeline (self):
        self.current_y = 1
        self.initScreen()
        for i in range(len(self.statuses)):
            if i >= self.status['first']:
                self.displayStatus(self.statuses[i], i)
        if self.flash[0]:
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

    def getTime (self, date, status):
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
        time    = self.getTime(status.created_at, status).encode(charset)
        #name    = status.user.name.encode(charset)

        if status.rt and self.conf.params_retweet_by == 1:
            rtby = pseudo
            origine = status.GetText()
            origine = origine[4:]
            origine = origine.split(':')[0]
            origine = str(origine)
            header = ' %s (%s) RT by %s ' % (origine, time, rtby)
        else:
            header = " %s (%s) " % (pseudo, time)

        return header

    def isRetweet (self, status):
        status.rt = self.regexRetweet.match(status.GetText())

    def handleKeybinding(self):
        '''Should have all keybinding handle here'''
        while True:

            ch = self.screen.getch()

            needRefresh = False

            if self.resize_event:
                self.resize_event = False
                curses.endwin()
                self.maxyx = self.screen.getmaxyx()
                curses.doupdate()
                needRefresh = True

            # Down and Up key must act as a menu, and should navigate
            # throught every tweets like an item.
            #
            # MOVE DOWN
            #
            if ch == ord(self.conf.keys_down) or ch == curses.KEY_DOWN:
                if self.status['current'] < self.status['count'] - 1:
                    if self.status['current'] >= self.status['last']:
                    # We need to be sure it will have enough place to
                    # display the next tweet, otherwise we still stay
                    # to the current tweet
                    # This is due to the dynamic height of a tweet.

                    # height_first_status = self.getSizeStatus(self.statuses[self.status['first']])
                    # next_status = self.status['last'] + 1
                    # height_next_status  = self.getSizeStatus(self.statuses[next_status])
                    # height_left = self.current_y - self.maxyx[0]-1
                    # if height_next_status['height'] > (height_left + height_first_status['height']):
                    #     self.status['current'] -=

                        self.status['first'] += 1


                    self.status['current'] += 1
                    needRefresh = True
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
                    needRefresh = True

            #
            # TWEET
            #
            elif ch == ord(self.conf.keys_tweet):
                box = editBox.EditBox(self.screen)

                if box.confirm:
                    try:
                        self.api.postTweet(box.getTweet())
                        self.flash = [True, 'info', 'Tweet has been send successfully.']
                    except:
                        self.flash = [True, 'warning', "Couldn't send the tweet."]
                needRefresh = True

            #
            # RETWEET
            #
            if ch == ord(self.conf.keys_retweet):
                status = self.statuses[self.status['current']]
                try:
                    self.api.retweet(status.GetId())
                    self.flash = [True, 'info', 'Retweet has been send successfully.']
                except:
                    self.flash = [True, 'warning', "Couldn't send the retweet."]
                needRefresh = True
            #
            # CLEAR
            #
            elif ch == ord(self.conf.keys_clear):
                self.clearStatuses()
                self.countStatuses()
                self.status['current'] = 0
                needRefresh = True

            #
            # UPDATE
            #
            elif ch == ord(self.conf.keys_update):
                self.updateHomeTimeline()
                needRefresh = True

            #
            # QUIT
            #
            # 27 corresponding to the ESC, couldn't find a KEY_* corresponding
            elif ch == ord(self.conf.keys_quit) or ch == 27:
                break

            if needRefresh:
                self.displayHomeTimeline()

    # Last function call when quiting, restore some defaults params
    def tearDown (self):
        curses.endwin()
        curses.curs_set(1)

    # Resize event callback
    def sigwinch_handler (self, *dummy):
        self.resize_event = True

    def clearStatuses (self):
        self.statuses = [self.statuses[0]]
