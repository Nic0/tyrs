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
        i=0
        for status in statuses:
            self.displayStatus(status, i)
            i = i+1
        self.screen.getch()

    def displayStatus (self, status, i):

        charset = sys.stdout.encoding
        text    = status.text.encode(charset)
        header  = self.getHeader(status)

        start_y = 2 + 4 * i
        start_x = 2

        if start_y + 4 > self.maxyx[0]:
            return 

        height = 4
        length = self.maxyx[1] - 4 

        tweet = curses.newpad(height, length)
        tweet.border(0)
        
        tweet.addstr(0,3, header, curses.color_pair(4))
        tweet.addstr(1,2, text)
        tweet.refresh(0, 0, start_y, start_x, 
            start_y + height, start_x + length)

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
