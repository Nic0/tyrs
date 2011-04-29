import sys
import curses
import time

# colors:
# 1 black
# 2 blue
# 3 cyan
# 4 green
# 5 magenta
# 6 red
# 7 white
# 8 yellow

class uiTyrs:

    def __init__ (self, api, conf):
        self.api    = api
        self.conf   = conf
        screen = curses.initscr()
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

        panel = curses.newpad(height, length)
        panel.border(0)
        
        panel.addstr(0,3, header, curses.color_pair(self.conf.color_header))
        self.displayText(text, panel)
        panel.refresh(0, 0, start_y, start_x, 
            start_y + height, start_x + length)

        self.current_y = start_y + height

        #return panel

    def displayText (self, text, panel):

        words = text.split(' ')
        curent_x = 2
        line = 1
        for word in words:
            if curent_x + len(word) > self.maxyx[1] -6:
                line += 1
                curent_x = 2

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
