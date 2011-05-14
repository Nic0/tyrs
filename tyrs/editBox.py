import curses
import curses.textpad

class EditBox:
    ''' Popup box with editing faculty.
    @param params {char, width, header}
           with char, the approximative maximum charactere we want the edit box may contain
    @param screen the main screen
    '''

    confirm = False

    def __init__(self, screen, params):

        self.screen = screen
        self.params = params
        self.win = self.initWin(screen)
        self.startEdit()
        self.win.erase()

    def startEdit (self):
        content = ''
        maxyx = self.win.getmaxyx()

        while True:
            ch = self.win.getch()

            if ch == 10:          # ENTER: send the tweet
                self.content = content
                self.confirm = True
                break

            elif ch == 27:        # ESC: abord
                break

            elif ch == 127:       # DEL
                cur_yx = self.win.getyx()
                if cur_yx[1] > 0:
                    self.win.move(cur_yx[0], cur_yx[1] - 1) # move back once
                    cur_yx = self.win.getyx()               # store new position
                    self.win.delch(cur_yx[0], cur_yx[1])    # delete the char
                    content = content[:-1]                      # delete last char in tweet string
            else:
                cur_yx = self.win.getyx()

                # for new lines, we don't want to start right in the border
                # we move the cursor, and get the correct value back to cur_yx
                if cur_yx[1] == maxyx[1] - 2:
                    self.win.move(cur_yx[0] +1, 2)
                    cur_yx = self.win.getyx()

                content += chr(ch)
                self.win.addstr(cur_yx[0], cur_yx[1], chr(ch))
                cur_yx = self.win.getyx()

            # Character counter
            position = cur_yx   # Remember position of cursor
            self.win.addstr((maxyx[0]-1), (maxyx[1]-5), str(len(content))) # print number of char
            self.win.move(position[0], position[1]) # go back to position

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
        win.addstr(0, 3, ' ' + self.params['header'] + ' ', curses.color_pair(3))
        win.move(2, 2)
        return win

    def getContent (self):
        return self.content
