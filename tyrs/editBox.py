import sys
import curses
import curses.textpad

class EditBox:

    confirm = False

    def __init__(self, screen):

        self.win = self.initWin(screen)
        self.startEdit()
        print 'tweet: %s' % self.tweet

    def startEdit (self):
        tweet = ''

        while True:
            ch = self.win.getch()
            if ch == 10:        # Corresponding to ENTER
                self.confirm = True
                break
            if ch == 27:        # Corresponding to ESC
                break

            else:
                cur_yx = self.win.getyx()
                #ch = str(chr(ch)).encode(sys.stdout.encoding)
                ch = chr(ch)
                self.win.addstr(cur_yx[0], cur_yx[1] + 1, ch.encode(sys.stdout.encoding))
                tweet += ch
                print 'tweet: %s' % tweet

        self.tweet = tweet

    def initWin (self, screen):
        '''
        This try to find a good size for the tweet window,
        and place it in main screen
        @return the EditBox
        '''
        maxyx = screen.getmaxyx()

        # Set height
        if maxyx[0] > 80:
            width = 80
        else:
            width = maxyx[0] - 4

        # Set width
        height = int(200 / width) + 2

        # Start of EditWin
        start_y = maxyx[0]/2 - int(height/2)
        start_x = maxyx[1]/2 - int(width/2)
        self.sizeyx = (height, width)

        # DEBUG
        # print "height:%s width:%s, start_y:%s, start_x:%s" % (height, width, start_y, start_x)

        win = screen.subwin(height, width, start_y, start_x)

        win.border(0)
        win.addstr(0, 3, ' What\'s up ? ', curses.color_pair(3))
        return win

    def getTweet (self):
        return self.tweet
