import sys
import curses
import time

class uiTyrs:

    def __init__ (self, api, conf):
        self.api    = api
        self.conf   = conf
        screen = curses.initscr()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, False)
        curses.init_pair(2, curses.COLOR_RED, False)
        curses.init_pair(3, curses.COLOR_GREEN, False)
        curses.init_pair(4, curses.COLOR_YELLOW, False)

        self.maxyx = screen.getmaxyx()

        screen.border(0)
        screen.refresh()
        self.screen = screen

    def displayHomeTimeline (self):
        statuses = self.api.updateHomeTimeline()

        self.current_y = 2

        for i in range(len(statuses)):
            self.displayStatus(statuses[i], i)
        self.screen.getch()

    def displayStatus (self, status, i):

        charset = sys.stdout.encoding
        text    = status.text.encode(charset)
        header  = self.getHeader(status)

        length = self.maxyx[1] - 4 
        height = len(text) / length + 3

        start_y = self.current_y
        start_x = 2

        # si on a plus de place pour afficher, on quitte
        if start_y + height > self.maxyx[0]:
            return 

        tweet = curses.newpad(height, length)
        tweet.border(0, curses.color_pair(1))
        
        tweet.addstr(0,3, header, curses.color_pair(4))
        tweet.addstr(1,2, text)
        tweet.refresh(0, 0, start_y, start_x, 
            start_y + height, start_x + length)

        self.current_y = start_y + height

        return tweet

    def getTime (self, date):
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
