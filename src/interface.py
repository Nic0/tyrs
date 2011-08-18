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
import os
import sys
import time
import tyrs
import signal                   # resize event
import curses
import logging
from user import User
from utils import html_unescape, encode, get_source, get_urls

class Interface(object):
    ''' All dispositions in the screen

    self.api              The tweetter API (not directly the api, but the instance of Tweets in tweets.py)
    self.conf             The configuration file parsed in config.py
    self.maxyx            Array contain the window size [y, x]
    self.screen           Main screen (curse)
    self.current_y        Current line in the screen
    self.resize_event     boleen if the window is resize
    self.regexRetweet     regex for retweet
    self.refresh_token    Boleen to make sure we don't refresh timeline. Usefull to keep editing box on top
    self.buffer           The current buffer we're looking at, (home, mentions, direct search)
    self.timelines        Containe all timelines with statuses, all Timeline
                          objects
    '''

    def __init__(self):
        self.api        = tyrs.container['api']
        self.conf       = tyrs.container['conf']
        self.timelines  = tyrs.container['timelines']
        self.buffers    = tyrs.container['buffers']
        tyrs.container.add('interface', self)
        self.last_read_home = self.conf.load_last_read()
        self.api.set_interface()
        self.resize_event     = False
        self.regex_retweet     = re.compile('^RT @\w+:')
        self.refresh_token    = False
        self.buffer           = 'home'
        self.charset = sys.stdout.encoding
        # resize event
        signal.signal(signal.SIGWINCH, self.sigwinch_handler)
        self.init_screen()
        self.first_update()

    def init_screen(self):

        self.screen = curses.initscr()
        curses.noecho()         # Dont print anything
        #curses.cbreak()
        self.screen.timeout(500)
        self.screen.keypad(1)        # Use of arrow keys
        try:
            curses.curs_set(0)      # Dont display cursor
        except curses.error:
            pass
        curses.meta(1)          # allow 8bits inputs
        self.init_colors()
        self.maxyx = self.screen.getmaxyx()

        self.screen.refresh()

    def init_colors(self):
        curses.start_color()
        self.init_rgb_colors()
        self.init_color_pairs()

    def init_rgb_colors(self):
        if curses.can_change_color():
            for i in range(len(self.conf.color_set)):
                if not self.conf.color_set[i]:
                    continue
                else:
                    rgb = self.conf.color_set[i]
                    curses.init_color(i, rgb[0], rgb[1], rgb[2])
    
    def init_color_pairs(self):
        bgcolor = self.init_background()
        curses.init_pair(0, curses.COLOR_BLACK, bgcolor)    # 0 black
        curses.init_pair(1, curses.COLOR_RED, bgcolor)      # 1 red
        curses.init_pair(2, curses.COLOR_GREEN, bgcolor)    # 2 green
        curses.init_pair(3, curses.COLOR_YELLOW, bgcolor)   # 3 yellow
        curses.init_pair(4, curses.COLOR_BLUE, bgcolor)     # 4 blue
        curses.init_pair(5, curses.COLOR_MAGENTA, bgcolor)  # 5 magenta
        curses.init_pair(6, curses.COLOR_CYAN, bgcolor)     # 6 cyan
        curses.init_pair(7, curses.COLOR_WHITE, bgcolor)    # 7 white

    def init_background(self):
        bgcolor = False
        if self.conf.params['transparency']:
            curses.use_default_colors()
            bgcolor = -1
        return bgcolor

    def first_update(self):
        updates = ['home', 'direct', 'mentions', 'user_retweet', 'favorite']
        for buff in updates:
            self.api.update_timeline(buff)
            self.timelines[buff].reset()
            self.timelines[buff].all_read()
        self.display_timeline()

    def handle_resize_event(self):
        self.resize_event = False
        curses.endwin()
        self.set_max_window_size()
        self.display_redraw_screen()
        curses.doupdate()

    def change_buffer(self, buffer):
        self.screen.clear()
        self.buffer = buffer
        self.timelines[buffer].reset()
        self.display_timeline()
    
    def navigate_buffer(self, nav):
        '''Navigate with the arrow, mean nav should be -1 or +1'''
        index = self.buffers.index(self.buffer)
        new_index = index + nav
        if new_index >= 0 and new_index < len(self.buffers):
            self.change_buffer(self.buffers[new_index])

    def display_flash_message(self):
        if self.api.flash_message.event and not self.refresh_token:
            msg = self.api.flash_message.get_msg()
            level = self.api.flash_message.level
            msg_color = { 0: 'info_msg', 1: 'warning_msg', }
            self.screen.addstr(0, 3, msg.encode(self.charset), self.get_color(msg_color[level]))
            self.api.flash_message.reset()
            self.screen.refresh()

    def erase_flash_message(self):
        try:
            self.screen.addstr(0,3, '                               ')
        except curses.error:
            pass

    def display_update_msg(self):
        self.api.flash_message.event = 'update'
        self.display_flash_message()
    
    def display_redraw_screen(self):
        self.screen.erase()
        self.set_max_window_size()
        self.display_timeline()

    def set_max_window_size(self):
        self.maxyx = self.screen.getmaxyx()

    def display_timeline(self):
        '''Main entry to display a timeline, as it does not take arguments,
           make sure to set self.buffer before
        '''
        try:
            if not self.refresh_token:
                self.set_max_window_size()
                self.set_date()

                timeline = self.select_current_timeline()
                statuses_count = len(timeline.statuses)

                self.display_flash_message()
                self.display_activities()
                self.display_help_bar()

                # It might have no tweets yet, we try to retrieve some then
                if statuses_count  == 0:
                    self.api.update_timeline(self.buffer)
                    timeline.reset()

                self.current_y = 1
                for i in range(len(timeline.statuses)):
                    if i >= timeline.first:
                        self.check_for_last_read(timeline.statuses[i].id)
                        br = self.display_status(timeline.statuses[i], i)
                        if not br:
                            break
                timeline.unread = 0 
                if self.buffer == 'home':
                    self.conf.save_last_read(timeline.last_read)
                self.screen.refresh()
                self.check_current_not_on_screen()
        except curses.error:
            logging.error('Curses error for display_timeline')
            pass

    def check_for_last_read(self, id):
        if self.buffer == 'home':
            if self.last_read_home == str(id):
                self.screen.hline(self.current_y, 1, '-', self.maxyx[1]-3)
                self.current_y += 1

    def set_date(self):
        self.date = time.strftime("%d %b", time.gmtime())

    def select_current_timeline(self):
        return self.timelines[self.buffer]

    def check_current_not_on_screen(self):
        '''TODO this hack should be solved when we realy display tweets'''
        timeline = self.select_current_timeline()
        if timeline.current > timeline.last:
            timeline.current = timeline.last
            self.display_redraw_screen()
            self.display_timeline()

    def display_activities(self):
        '''Main entry to display the activities bar'''
        if self.conf.params['activities']:
            maxyx = self.screen.getmaxyx()
            max_x = maxyx[1]
            self.screen.addstr(0, max_x - 23, ' ')
            for b in self.buffers:
                self.display_buffer_activities(b)
                self.display_counter_activities(b)

    def display_buffer_activities(self, buff):
        display = { 
                'home': 'H', 'mentions': 'M', 'direct': 'D', 
                'search': 'S', 'user': 'U', 'favorite': 'F',
                'thread': 'T', 'user_retweet': 'R'}
        if self.buffer == buff:
            self.screen.addstr(display[buff], self.get_color('current_tab'))
        else:
            self.screen.addstr(display[buff], self.get_color('other_tab'))

    def display_counter_activities(self, buff):
        self.select_current_timeline().all_read()
        if buff in ['home', 'mentions', 'direct']:
            unread = self.timelines[buff].unread
            if unread == 0:
                color = 'read'
            else:
                color = 'unread'

            self.screen.addstr(':%s ' % str(unread), self.get_color(color))

    def display_help_bar(self):
        '''The help bar display at the bottom of the screen,
           for keysbinding reminder'''
        if self.conf.params['help']:
            maxyx = self.screen.getmaxyx()
            self.screen.addnstr(maxyx[0] -1, 2,
                'help:? up:%s down:%s tweet:%s retweet:%s reply:%s home:%s mentions:%s update:%s' %
                               (chr(self.conf.keys['up']),
                                chr(self.conf.keys['down']),
                                chr(self.conf.keys['tweet']),
                                chr(self.conf.keys['retweet']),
                                chr(self.conf.keys['reply']),
                                chr(self.conf.keys['home']),
                                chr(self.conf.keys['mentions']),
                                chr(self.conf.keys['update']),
                               ), maxyx[1] -4, self.get_color('text')
            )

    def display_status (self, status, i):
        ''' Display a status (tweet) from top to bottom of the screen,
        depending on self.current_y, an array [status, panel] is return and
        will be stock in a array, to retreve status information (like id)
        @param status, the status to display
        @param i, to know on witch status we're display (this could be refactored)
        @return True if the tweet as been displayed, to know it may carry on to display some
                more, otherwise return False
        '''

        timeline = self.select_current_timeline()
        self.is_retweet(status)

        # The content of the tweets is handle
        # text is needed for the height of a panel
        try:
            header  = self.get_header(status)
        except UnicodeDecodeError:
            header = 'encode error'

        # We get size and where to display the tweet
        size = self.get_size_status(status)
        length = size['length']
        height = size['height']
        start_y = self.current_y
        start_x = self.conf.params['margin']
        # We leave if no more space left
        if start_y + height +1 > self.maxyx[0]:
            return False

        panel = curses.newpad(height, length)

        if self.conf.params['tweet_border'] == 1:
            if self.conf.params['old_skool_border']:
                panel.border('|','|','-','-','+','+','+','+')
            else:
                if self.conf.params['compact']:
                    panel.border(curses.ACS_VLINE, curses.ACS_VLINE, curses.ACS_HLINE, ' ',
                                 curses.ACS_ULCORNER, curses.ACS_URCORNER, ' ', ' ')
                else:
                    panel.border(0)

        # Highlight the current status
        if timeline.current == i:
            panel.addstr(0,3, header, self.get_color('current_tweet'))
        else:
            panel.addstr(0, 3, header, self.get_color('header'))

        self.display_text(panel, status)
        try:
            panel.refresh(0, 0, start_y, start_x,
                start_y + height, start_x + length)
        except curses.error:
            pass
        # An adjustment to compress a little the display
        if self.conf.params['compact']:
            c = -1
        else:
            c = 0

        self.current_y = start_y + height + c
        timeline.last = i

        return True

    def get_text(self, status):
        text = html_unescape(status.text.replace('\n', ' '))
        if status.rt:
            text = text.split(':')[1:]
            text = ':'.join(text)

            if hasattr(status, 'retweeted_status'):
                if hasattr(status.retweeted_status, 'text') \
                        and len(status.retweeted_status.text) > 0:
                    text = status.retweeted_status.text
        return text

    def display_text(self, panel, status):
        '''needed to cut words properly, as it would cut it in a midle of a
        world without. handle highlighting of '#' and '@' tags.
        '''
        text = self.get_text(status)
        words = text.split(' ')
        margin = self.conf.params['margin']
        padding = self.conf.params['padding']
        myself = self.api.myself.screen_name
        curent_x = padding
        line = 1

        hashtag = encode('#')
        attag = encode('@')


        for word in words:
            word = encode(word)
            if curent_x + len(word) > self.maxyx[1] - (margin + padding)*2:
                line += 1
                curent_x = padding

            if word != '':
                # The word is an HASHTAG ? '#'
                if word[0] == hashtag:
                    panel.addstr(line, curent_x, word, self.get_color('hashtag'))
                # Or is it an 'AT TAG' ? '@'
                elif word[0] == attag:
                    # The AT TAG is,  @myself
                    if word == attag + myself or word == attag + myself+ encode(':'):
                        panel.addstr(line, curent_x, word, self.get_color('highlight'))
                    # @anyone
                    else:
                        panel.addstr(line, curent_x, word, self.get_color('attag'))
                # It's just a normal word
                else:
                    try:
                        panel.addstr(line, curent_x, word, self.get_color('text'))
                    except curses.error:
                        pass
                curent_x += len(word) + 1

                # We check for ugly empty spaces
                while panel.inch(line, curent_x -1) == ord(' ') and panel.inch(line, curent_x -2) == ord(' '):
                    curent_x -= 1

    def get_size_status(self, status):
        '''Allow to know how height will be the tweet, it calculate it exactly
           as it will display it.
        '''
        length = self.get_max_lenght()
        margin = self.conf.params['margin']
        padding = self.conf.params['padding']
        x = padding+margin
        y = 1
        txt = self.get_text(status)
        words = txt.split(' ')
        for w in words:
            if x+len(w) > length - (padding+margin)*2:
                y += 1
                x = padding+margin
            x += len(w)+1

        height = y + 2
        size = {'length': length, 'height': height}
        return size

    def get_max_lenght(self):
        adjust = self.conf.params['margin'] + self.conf.params['padding']
        return self.maxyx[1] - adjust

    def get_time(self, status):
        '''Handle the time format given by the api with something more
        readeable
        @param  date: full iso time format
        @return string: readeable time
        '''
        if self.conf.params['relative_time'] == 1 and self.buffer != 'direct':
            result =  status.GetRelativeCreatedAt()
        else:
            hour = time.gmtime(status.GetCreatedAtInSeconds() - time.altzone)
            result = time.strftime('%H:%M', hour)
            if time.strftime('%d %b', hour) != self.date:
                result += time.strftime(' - %d %b', hour)

        return result

    def get_header(self, status):
        retweeted = ''
        reply = ''
        retweet_count = ''
        retweeter = ''
        source = self.get_source(status)
        nick = self.get_nick(status)
        time = self.get_time(status)

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
            time = time,
            nick = nick,
            reply = reply,
            retweeted = retweeted,
            source = source,
            retweet_count = retweet_count,
            retweeter = retweeter
            )

        return encode(header)

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

    def tear_down(self, *dummy):
        '''Last function call when quiting, restore some defaults params'''
        self.screen.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.curs_set(1)
        curses.endwin()

    def sigwinch_handler(self, *dummy):
        '''Resize event callback'''
        self.resize_event = True

    def clear_statuses(self):
        timeline = self.select_current_timeline()
        timeline.statuses = [timeline.statuses[0]]
        timeline.count_statuses()
        timeline.reset()

    def current_status(self):
        '''@return the status object itself'''
        timeline = self.select_current_timeline()
        return timeline.statuses[timeline.current]

    def get_color(self, color):
        '''Return the curses code, with bold if enable of the color
           given in argument of the function
           @return color_pair code
        '''
        cp = curses.color_pair(self.conf.colors[color]['c'])
        if self.conf.colors[color]['b']:
            cp |= curses.A_BOLD

        return cp

    def move_down(self):
        timeline = self.select_current_timeline()
        if timeline.current < timeline.count - 1:
            if timeline.current >= timeline.last:
                timeline.first += 1
            timeline.current += 1
        else:
            self.lazzy_load()

    def lazzy_load(self):
        timeline = self.select_current_timeline()
        timeline.page += 1
        statuses = self.api.retreive_statuses(self.buffer, timeline.page)
        timeline.append_old_statuses(statuses)
        timeline.first += 1
        timeline.current += 1

    def move_up(self):
        timeline = self.select_current_timeline()
        if timeline.current > 0:
            # if we need to move up the list to display
            if timeline.current == timeline.first:
                timeline.first -= 1
            timeline.current -= 1

    def back_on_bottom(self):
        timeline = self.select_current_timeline()
        timeline.current = timeline.last

    def back_on_top(self):
        timeline = self.select_current_timeline()
        timeline.current = 0
        timeline.reset()

    def openurl(self):
        urls = get_urls(self.current_status().text)
        for url in urls:
            try:
                os.system(self.conf.params['openurl_command'] % url)
            except:
                pass 

    def current_user_info(self):
        User(self.current_status().user)
