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

import re
import tyrs
import time
import urwid
from utils import html_unescape, encode, get_source, get_urls

class HeaderWidget(urwid.WidgetWrap):

    def __init__(self):
        self.api = tyrs.container['api']
        self.interface = tyrs.container['interface']
        self.timelines = tyrs.container['timelines']
        self.buffer = self.interface.buffer
        flash = self.set_flash()
        activities = self.set_activities()
        w = urwid.Columns([flash, ('fixed', 20, activities)])
        self.__super.__init__(w)

    def set_flash(self):
        msg = ''
        level = 0
        msg = self.api.flash_message.get_msg()
        color = {0: 'info_msg', 1: 'warn_msg'}
        level = self.api.flash_message.level
        event_message = urwid.Text(msg)
        flash = urwid.AttrWrap(event_message, color[level])
        return flash

    def set_activities(self):

        buffers = (
            'home', 'mentions', 'direct', 'search',
            'user', 'favorite', 'thread', 'user_retweet'
        )
        display = { 
            'home': 'H', 'mentions': 'M', 'direct': 'D', 
            'search': 'S', 'user': 'U', 'favorite': 'F',
            'thread': 'T', 'user_retweet': 'R'
        }
        buff_widget = []
        for b in buffers:
            if b == self.buffer:
                buff_widget.append(('current_tab', display[b]))
            else:
                buff_widget.append(('other_tab', display[b]))
            if b in ('home', 'mentions', 'direct'):
                buff_widget.append(self.get_unread(b))
                    
        return urwid.Text(buff_widget)

    def get_unread(self, buff):
        self.select_current_timeline().all_read()
        unread = self.timelines[buff].unread
        if unread == 0:
            color = 'read'
        else:
            color = 'unread'
        return [('read', ':'), (color , str(unread)), ' ']

    def select_current_timeline(self):
        return self.timelines[self.buffer]

class StatusWidget (urwid.WidgetWrap):

    def __init__ (self, id, status):
        self.regex_retweet     = re.compile('^RT @\w+:')
        self.conf       = tyrs.container['conf']
        self.api       = tyrs.container['api']
        self.set_date()
        self.buffer = tyrs.container['interface'].buffer
        self.is_retweet(status)
        self.id = id
        self.status = status
        status_content = urwid.Padding(
            urwid.AttrWrap(urwid.Text(self.get_text(status)), 'body'), left=1, right=1)
        w = urwid.AttrWrap(TitleLineBox(status_content, title=self.get_header(status)), 'body', 'focus')
        self.__super.__init__(w)

    def selectable (self):
        return True

    def keypress(self, size, key):
        return key

    def get_text(self, status):
        result = []
        text = html_unescape(status.text.replace('\n', ' '))
        if status.rt:
            text = text.split(':')[1:]
            text = ':'.join(text)

        if hasattr(status, 'retweeted_status'):
            if hasattr(status.retweeted_status, 'text') \
                    and len(status.retweeted_status.text) > 0:
                text = status.retweeted_status.text

        myself = self.api.myself.screen_name

        words = text.split(' ')
        for word in words:
            if word != '':
                word += ' '
                # The word is an HASHTAG ? '#'
                if word[0] == '#':
                    result.append(('hashtag', word))
                elif word[0] == '@':
                    ## The AT TAG is,  @myself
                    if word == '@%s ' % myself or word == '@%s: ' % myself:
                        result.append(('highlight_nick', word))
                    ## @anyone
                    else:
                        result.append(('attag', word))
                else:
                    result.append(word)
        return result

    def get_header(self, status):
        retweeted = ''
        reply = ''
        retweet_count = ''
        retweeter = ''
        source = self.get_source(status)
        nick = self.get_nick(status)
        timer = self.get_time(status)

        if self.is_reply(status):
            reply = u' \u2709'
        if status.rt:
            retweeted = u" \u267b "
            retweeter = nick
            nick = self.origin_of_retweet(status)

        if self.get_retweet_count(status):
            retweet_count = str(self.get_retweet_count(status))

        header_template = self.conf.params['header_template'] 
        header = unicode(header_template).format(
            time = timer,
            nick = nick,
            reply = reply,
            retweeted = retweeted,
            source = source,
            retweet_count = retweet_count,
            retweeter = retweeter
            )

        return encode(header)

    def set_date(self):
        self.date = time.strftime("%d %b", time.gmtime())

    def get_time(self, status):
        '''Handle the time format given by the api with something more
        readeable
        @param  date: full iso time format
        @return string: readeable time
        '''
        if self.conf.params['relative_time'] == 1 and self.buffer != 'direct':
            try:
                result =  status.GetRelativeCreatedAt()
            except AttributeError:
                return ''
        else:
            hour = time.gmtime(status.GetCreatedAtInSeconds() - time.altzone)
            result = time.strftime('%H:%M', hour)
            if time.strftime('%d %b', hour) != self.date:
                result += time.strftime(' - %d %b', hour)

        return result

    def get_source(self, status):
        source = ''
        if hasattr(status, 'source'):
            source = get_source(status.source)

        return source

    def get_nick(self, status):
        if hasattr(status, 'user'):
            nick = status.user.screen_name
        else:
            #Used for direct messages
            nick = status.sender_screen_name

        return nick

    def get_retweet_count(self, status):
        if hasattr(status, 'retweet_count'):
            return status.retweet_count

    def is_retweet(self, status):
        status.rt = self.regex_retweet.match(status.text)
        return status.rt

    def is_reply(self, status):
        if hasattr(status, 'in_reply_to_screen_name'):
            reply = status.in_reply_to_screen_name
            if reply:
                return True
        return False

    def origin_of_retweet(self, status):
        '''When its a retweet, return the first person who tweet it,
           not the retweeter
        '''
        origin = status.text
        origin = origin[4:]
        origin = origin.split(':')[0]
        origin = str(origin)
        return origin


class TitleLineBox(urwid.WidgetDecoration, urwid.WidgetWrap):
    def __init__(self, original_widget, title=''):
        """Draw a line around original_widget."""
        
        tlcorner=None; tline=None; lline=None
        trcorner=None; blcorner=None; rline=None
        bline=None; brcorner=None
        
        def use_attr( a, t ):
            if a is not None:
                t = urwid.AttrWrap(t, a)
            return t
            
        tline = use_attr( tline, urwid.Columns([
            ('fixed', 2, urwid.Divider(urwid.utf8decode("─"))),
            ('fixed', len(title), urwid.Text(title)),
            urwid.Divider(urwid.utf8decode("─"))]))
        bline = use_attr( bline, urwid.Divider(urwid.utf8decode("─")))
        lline = use_attr( lline, urwid.SolidFill(urwid.utf8decode("│")))
        rline = use_attr( rline, urwid.SolidFill(urwid.utf8decode("│")))
        tlcorner = use_attr( tlcorner, urwid.Text(urwid.utf8decode("┌")))
        trcorner = use_attr( trcorner, urwid.Text(urwid.utf8decode("┐")))
        blcorner = use_attr( blcorner, urwid.Text(urwid.utf8decode("└")))
        brcorner = use_attr( brcorner, urwid.Text(urwid.utf8decode("┘")))
        top = urwid.Columns([ ('fixed', 1, tlcorner),
            tline, ('fixed', 1, trcorner) ])
        middle = urwid.Columns( [('fixed', 1, lline),
            original_widget, ('fixed', 1, rline)], box_columns = [0,2],
            focus_column = 1)
        bottom = urwid.Columns([ ('fixed', 1, blcorner),
            bline, ('fixed', 1, brcorner) ])
        pile = urwid.Pile([('flow',top),middle,('flow',bottom)],
            focus_item = 1)
        
        urwid.WidgetDecoration.__init__(self, original_widget)
        urwid.WidgetWrap.__init__(self, pile)
