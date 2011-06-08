# -*- coding: utf-8 -*-
# Copyright © 2011 Nicolas Paris <nicolas.caen@gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import tyrs
import curses
import curses.textpad

class Editor:

    confirm = False
    content = ''

    def __init__(self, data=None):
        self.conf = tyrs.container['conf']
        self.ui = tyrs.container['interface'] 
        self.data   = data
        self.win = self.init_win(self.ui.screen)
        self.win.keypad(1)
        curses.curs_set(1)
        self.start_edit()
        self.win.erase()


    def start_edit(self):

        self.ui.refresh_token = True
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
                self.content = None
                break

            elif ch == 127:       # DEL
                if len(self.content) > 0:
                    self.content = self.content[:-1]
            else:
                self.content += chr(ch)

            self.refresh()
        self.ui.refresh_token = False

    def refresh(self):
        self.win.erase()
        self.win = self.init_win(self.ui.screen)
        self.display_content()
        self.win.refresh()

    def display_content(self):
        x = 2
        y = 2
        words = self.content.split(' ')
        max = self.win.getmaxyx()
        for w in words:
            if x+len(w) > max[1] - 4:
                y += 1
                x = 2
            self.win.addstr(y, x, w, self.ui.get_color('text'))
            x += len(w)+1


    def init_win(self, screen):
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
        counter = str(self.count_chr())
        header = ' %s %s ' % (self.params['header'], counter)

        #TODO this doen't take bold
        win.addstr(0, 3, header, curses.color_pair(self.conf.colors['header']['c']))
        return win

    def count_chr(self):
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

class TweetEditor(Editor):
    params = {'char': 200, 'width': 80, 'header': "What's up?"}

class NickEditor(Editor):
    params = {'char': 40, 'width': 40, 'header': "Entry a name"}

class SearchEditor(Editor):
    params = {'char': 40, 'width': 40, 'header': "Search for something?"}
