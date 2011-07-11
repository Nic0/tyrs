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
import curses.ascii
from utils import encode, get_urls
try:
    from shorter.ur1ca import Ur1caUrlShorter
    from shorter.bitly import BitLyUrlShorter
    from shorter.msudpl import MsudplUrlShorter
    from shorter.custom import CustomUrlShorter
except ImportError:
    pass

try:
    from shorter.googl import GooglUrlShorter
except ImportError:
    pass

class Editor(object):

    def __init__(self, data=None):
        self.conf = tyrs.container['conf']
        self.interface = tyrs.container['interface'] 
        self.interface.refresh_token = True
        self.init_content(data)
        self.init_win()
        self.start_edit()
        self.tear_down()

    def init_content(self, data):
        self.content = ''
        if data:
            self.content = encode(data)


    def init_win(self):
        self.change_cursor(1)
        self.set_window_size()

        self.win = self.interface.screen.subwin(
                self.size['height'], self.size['width'],
                self.size['start_y'], self.size['start_x'])

        self.win.keypad(1)
        self.init_border()
        self.display_header()
        self.win.move(2,2)
        self.maxyx = self.win.getmaxyx()
        self.display_content()

    def init_border(self):
        if self.conf.params['old_skool_border']:
            self.win.border('|','|','-','-','+','+','+','+')
        else:
            self.win.border(0)

    def display_header(self):
        counter = self.count_chr()
        header = ' %s %s ' % (self.params['header'], str(counter))
        self.win.addstr(0, 3, encode(header), curses.color_pair(self.conf.colors['header']['c']))

    def set_window_size(self):
        maxyx = self.interface.screen.getmaxyx()

        # Set width
        if maxyx[1] > self.params['width']:
            width = self.params['width']
        else:
            width = maxyx[1] - 4 # 4: leave 2pix on every side at least

        # Set height
        height = int(self.params['char'] / width) + 4

        # Start of EditWin, display in the middle of the main screen
        if self.conf.params['box_position'] != 1:
            start_y = maxyx[0]/2 - int(height/2)
        else:
            start_y = maxyx[0] - height
        start_x = maxyx[1]/2 - int(width/2)
        self.sizeyx = (height, width)

        self.size = {
                'height': height, 'width': width,
                'start_y': start_y, 'start_x': start_x
        }


    def start_edit(self):

        while True:
            ch = self.win.getch()
            if ch == curses.KEY_UP or ch == curses.KEY_DOWN \
                    or ch == curses.KEY_LEFT or ch == curses.KEY_RIGHT:
                continue

            elif ch == 10:          # ENTER: send the tweet
                break

            elif ch == 27:        # ESC: abord
                self.content = None
                break

            elif ch == 127 or ch == curses.KEY_BACKSPACE:       # DEL
                if len(self.content) > 0:
                    self.content = self.content[:-1]
            elif curses.ascii.unctrl(ch) == '^U':
                self.shorter_url()
            else:
                self.content += chr(ch)

            self.refresh()

    def refresh(self):
        self.win.erase()
        self.init_win()
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
            self.win.addstr(y, x, w, self.interface.get_color('text'))
            x += len(w)+1

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

    def change_cursor(self, opt):
        try:
            curses.curs_set(opt)
        except curses.error:
            pass

    def tear_down(self):
        self.win.erase()
        self.change_cursor(0)
        self.interface.refresh_token = False

class TweetEditor(Editor):
    params = {'char': 200, 'width': 80, 'header': _("What's up?")}

    def shorter_url(self):
        self._set_service()
        long_urls = get_urls(self.content)
        for long_url in long_urls:
            short_url = self.shorter.do_shorter(long_url)
            try:
                self.content = self.content.replace(long_url, short_url)
            except UnicodeDecodeError:
                pass

    def _set_service(self):
        service = self.conf.params['url_shorter']
        if service == 'bitly':
            self.shorter = BitLyUrlShorter() 
        elif service == 'googl':
            self.shorter = GooglUrlShorter()
        elif service == 'msudpl':
            self.shorter = MsudplUrlShorter()
        elif service == 'custom':
            self.shorter = CustomUrlShorter()
        else:
            self.shorter = Ur1caUrlShorter()


class NickEditor(Editor):
    params = {'char': 40, 'width': 40, 'header': _("Entry a name")}

class SearchEditor(Editor):
    params = {'char': 40, 'width': 40, 'header': _("Search for something?")}
