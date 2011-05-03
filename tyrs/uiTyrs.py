import sys
import curses
import time

class uiTyrs:
    ''' All dispositions in the screen, and some logics for display tweet
    '''

    # current:  the current tweet highlight, from the statuses list
    # first:    first status display, from the status list, mean if we display the midle
    #           of the list, the first won't be 0
    # last:     the last tweet from statuses list
    # count:    usefull, knowing if it's the last one on the statuses list as well
    status = {'current': 0, 'first': 0, 'last': 0, 'count': 0}

    def __init__ (self, api, conf):
        self.api    = api
        self.conf   = conf
        screen = curses.initscr()

        curses.noecho()
        curses.cbreak()
        screen.keypad(1)

        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, False)
        curses.init_pair(2, curses.COLOR_BLUE, False)
        curses.init_pair(3, curses.COLOR_CYAN, False)
        curses.init_pair(4, curses.COLOR_GREEN, False)
        curses.init_pair(5, curses.COLOR_MAGENTA, False)
        curses.init_pair(6, curses.COLOR_RED, False)
        curses.init_pair(7, curses.COLOR_WHITE, False)
        curses.init_pair(8, curses.COLOR_YELLOW, False)

        self.maxyx = screen.getmaxyx()

        screen.border(0)
        screen.refresh()
        self.screen = screen

    def updateHomeTimeline (self):
        self.statuses = self.api.updateHomeTimeline()
        self.countStatus()

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
                    panel.addstr(line, curent_x, word)
                curent_x += len(word) + 1

    def getTime (self, date):
        '''Handle the time format given by the api with something more
        readeable'''
        time = date.split(' ')
        time = time[3]
        time = time.split(':')
        time = time[0:2]
        time = ':'.join(time)

        return time

    def getHeader (self, status):
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

            #  MOVE DOWN
            if ch == ord(self.conf.keys_down) or ch == curses.KEY_DOWN:
                # if we have some more tweets to display
                if self.status['current'] < self.status['count'] - 1:
                    if self.status['current'] == self.status['last']:
                        self.status['first'] += 1
                    self.status['current'] += 1
                    self.displayHomeTimeline()

            # MOVE UP
            elif ch == ord(self.conf.keys_up) or ch == curses.KEY_UP:
                # the current tweet must not be the first one of the statuses
                # list
                if self.status['current'] > 0:
                    # if we need to move up the list to display
                    if self.status['current'] == self.status['first']:
                        self.status['first'] -= 1
                    self.status['current'] -= 1
                    self.displayHomeTimeline()

            # QUIT
            # 27 corresponding to the ESC, couldn't find a KEY_* corresponding
            elif ch == ord(self.conf.keys_quit) or ch == 27:
                break

    def tearDown (self):
        curses.endwin()
