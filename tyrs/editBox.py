#! -*- coding: utf-8 -*-
import curses
import curses.textpad

class EditBox:
    ''' Popup box with editing faculty.
    @param params {char, width, header}
           with char, the approximative maximum charactere we want the edit box may contain
    @param screen the main screen
    '''

    confirm = False
    content = ''
    del_utf = False

    def __init__(self, screen, params):

        self.screen = screen
        self.params = params
        self.win = self.initWin(screen)
        self.startEdit()
        self.win.erase()

    def startEdit (self):
        self.maxyx = self.win.getmaxyx()

        while True:
            ch = self.win.getch()

            if ch == 10:          # ENTER: send the tweet
                self.confirm = True
                break

            elif ch == 27:        # ESC: abord
                break

            elif ch == 127:       # DEL

                if len(self.content) > 0:
                    if ord(self.content[-1]) <= 128:
                        self.content = self.content[:-1]
                    else:
                        self.content = self.content[:-2]

                    if len(self.content) > 0 and self.content[-1] > 128:
                        self.del_utf = True

            else:
                self.content += chr(ch)

            self.refresh()

    def refresh (self):
        self.win.erase()
        self.win = self.initWin(self.screen)
        self.displayContent()
        self.win.refresh()

    def displayContent (self):
        yx = [2,2]
        token = False
        for ch in self.content:
            if yx[1] == self.maxyx[1]-2:
                yx[0] += 1
                yx[1] = 2
            self.win.addstr(yx[0], yx[1], ch)
            if not token:
                yx[1] += 1
                if not ord(ch) <= 128:
                    token = True
            else:
                token = False

        if self.del_utf == True:
            if len(self.content) > 0:
                if ord(self.content[-1]) >= 128:
                    curyx = self.win.getyx()
                    self.win.delch(curyx[0], curyx[1])
            self.del_utf == False
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

        #win.addstr(0, 3, ' ' + self.params['header'] + ' ' + counter + ' ', curses.color_pair(3))
        win.addstr(0, 3, header, curses.color_pair(3))
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

