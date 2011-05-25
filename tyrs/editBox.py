#! -*- coding: utf-8 -*-
import curses
import curses.textpad
import sys

class EditBox:
    ''' Popup box with editing faculty.
    @param params {char, width, header}
           with char, the approximative maximum charactere we want the edit box may contain
    @param screen the main screen
    '''

    confirm = False
    content = ''

    def __init__(self, screen, params, data, conf):

        self.conf = conf
        self.screen = screen
        self.params = params
        self.data   = data
        self.win = self.initWin(screen)
        self.win.keypad(1)
        curses.curs_set(1)
        self.startEdit()
        self.win.erase()

    def startEdit (self):

        if self.data:
            self.content = self.data.encode('utf-8')
            self.refresh()

        self.maxyx = self.win.getmaxyx()

        while True:
            ch = self.win.getch()
            if ch == curses.KEY_UP or ch == curses.KEY_DOWN \
                    or ch == curses.KEY_LEFT or ch == curses.KEY_RIGHT:
                continue

            elif ch == 10:          # ENTER: send the tweet
                self.confirm = True
                break

            elif ch == 27:        # ESC: abord
                break

            elif ch == 127:       # DEL
                if len(self.content) > 0:
                    self.content = self.content[:-1]
            else:
                self.content += chr(ch)

            self.refresh()

    def refresh (self):
        self.win.erase()
        self.win = self.initWin(self.screen)
        self.displayContent()
        self.win.refresh()

    def displayContent (self):
        self.win.addstr(2, 2, self.content)

    def initWin (self, screen):
        '''
        This try to find a good size for the tweet window,
        and place it in main screen
        @return the EditBox
        '''
        maxyx = screen.getmaxyx()

        # Set width
        if maxyx[1] > self.params['width']:
            width = self.params['width']
        else:
            width = maxyx[1] - 4 # 4: leave 2pix on every side at least

        # Set height
        height = int(self.params['char'] / width) + 4

        # Start of EditWin, display in the middle of the main screen
        start_y = maxyx[0]/2 - int(height/2)
        start_x = maxyx[1]/2 - int(width/2)
        self.sizeyx = (height, width)

        # DEBUG
        # print "height:%s width:%s, start_y:%s, start_x:%s" % (height, width, start_y, start_x)

        win = screen.subwin(height, width, start_y, start_x)

        win.border(0)
        counter = str(self.countChr())
        header = ' %s %s ' % (self.params['header'], counter)

        #TODO this doen't take bold
        win.addstr(0, 3, header, curses.color_pair(self.conf.colors['header']['c']))
        return win

    def countChr (self):
        i = 0
        token = False
        for ch in self.content:
            if not token:
                i += 1
                if not ord(ch) <= 128:
                    token = True
            else:
                token = False
        return i

    def getContent (self):
        return self.content

