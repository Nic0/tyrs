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

palette = [
    ('body','dark blue', '', 'standout'),
    ('focus','dark red', '', 'standout'),
    ('head','light red', ''),
    ('info_msg', 'dark green', ''),
    ('warn_msg', 'dark red', ''),
    ('current_tab', 'light blue', ''),
    ('other_tab', 'dark blue', ''),
    ('read', 'dark blue', ''),
    ('unread', 'dark red', ''),
    ('hashtag', 'dark green', ''),
    ('attag', 'brown', ''),
    ('highlight', 'dark red', ''),
    ('highlight_nick', 'light red', ''),
    ('help_bar', 'yellow', 'dark blue'),
    ('help_key', 'dark red', ''),
    ]

# c: color value
# b: bold
colors = {
    'highlight':      {'c': 1},
    'header':         {'c': 6},
    'hashtag':        {'c': 3},
    'attag':          {'c': 2},
    'text':           {'c': 0},
    'warning_msg':    {'c': 1},
    'info_msg':       {'c': 2},
    'current_tweet':  {'c': 5},
    'current_tab':    {'c': 6},
    'other_tab':      {'c': 0},
    'unread':         {'c': 1},
    'read':           {'c': 0},
    'help':           {'c': 6},
}

color_set = [False, False, False, False, False, False, False, False]

key = {
    'up':                'k',
    'down':              'j',
    'left':              'J',
    'right':             'K',
    'quit':              'q',
    'tweet':             't',
    'clear':             'c',
    'retweet':           'r',
    'retweet_and_edit':  'R',
    'delete':            'C',
    'update':            'u',
    'follow_selected':   'f',
    'unfollow_selected': 'l',
    'follow':            'F',
    'unfollow':          'L',
    'openurl':           'o',
    'open_image':        'ctrl i',
    'home':              'h',
    'mentions':          'm',
    'reply':             'M',
    'back_on_top':       'g',
    'back_on_bottom':    'G',
    'getDM':             'd',
    'sendDM':            'D',
    'search':            's',
    'search_user':       'U',
    'search_current_user': 'ctrl f',
    'search_myself':     'ctrl u',
    'redraw':            'ctrl l',
    'fav':               'b',
    'get_fav':           'B',
    'delete_fav':        'ctrl b',
    'thread':            'T',
    'waterline':         'w',
}

params = {
    'refresh':              2,
    'tweet_border':         1,
    'relative_time':        1,
    'retweet_by':           1,
    'margin':               1,
    'padding':              2,
    'openurl_command':      'firefox %s',
    'open_image_command':   'feh %s',
    'transparency':         True,
    'activities':           True,
    'compact':              False,
    'help':                 True,
    'old_skool_border':     False,
    'box_position':         1,
    'url_shorter':          'ur1ca',
    'logging_level':        3,
    'header_template':      ' {nick}{retweeted}{retweeter} - {time}{reply} {retweet_count} ',
    'proxy':                None,
    'beep':                 False,
}

filter = {
    'activate':         False,
    'myself':           False,
    'behavior':         'all',
    'except':           [],
}

token = {
    'twitter': {
        'consumer_key':     'Eq9KLjwH9sJNcpF4OOYNw',
        'consumer_secret':  '3JoHyvBp3L6hhJo4BJr6H5aFxLhSlR70ZYnM8jBCQ'
    },
    'identica': {
        'consumer_key':     '6b2cf8346a141d530739f72b977b7078',
        'consumer_secret':  '31b342b348502345d4a343a331e00edb'
    }
}
