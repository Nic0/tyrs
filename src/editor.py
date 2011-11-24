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
import urwid
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

class TweetEditor(urwid.WidgetWrap):

    __metaclass__ = urwid.signals.MetaSignals
    signals = ['done']

    def __init__(self, init_content=''):
        if init_content:
            init_content += ' '
        self.editor = Editor('>> ', init_content)
        self.counter = urwid.Text('0')
        w = urwid.Columns([ ('fixed', 4, self.counter), self.editor])
        urwid.connect_signal(self.editor, 'done', self.send_sigterm)
        urwid.connect_signal(self.editor, 'change', self.update_count)

        self.__super.__init__(w)

    def send_sigterm(self, content):
        urwid.emit_signal(self, 'done', content)

    def update_count(self, edit, new_edit_text):
        self.counter.set_text(str(len(new_edit_text)))

class Editor(urwid.Edit):

    __metaclass__ = urwid.signals.MetaSignals
    signals = ['done']

    def keypress(self, size, key):
        if key == 'enter':
            urwid.emit_signal(self, 'done', self.get_edit_text())
            return
        if key == 'esc':
            urwid.emit_signal(self, 'done', None)
        urwid.Edit.keypress(self, size, key)

#FIXME old editor, need to be done for url-shorter

    #def shorter_url(self):
        #self._set_service()
        #long_urls = get_urls(self.content)
        #for long_url in long_urls:
            #short_url = self.shorter.do_shorter(long_url)
            #try:
                #self.content = self.content.replace(long_url, short_url)
            #except UnicodeDecodeError:
                #pass

    #def _set_service(self):
        #service = self.conf.params['url_shorter']
        #if service == 'bitly':
            #self.shorter = BitLyUrlShorter() 
        #elif service == 'googl':
            #self.shorter = GooglUrlShorter()
        #elif service == 'msudpl':
            #self.shorter = MsudplUrlShorter()
        #elif service == 'custom':
            #self.shorter = CustomUrlShorter()
        #else:
            #self.shorter = Ur1caUrlShorter()
