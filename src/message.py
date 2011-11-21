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

from utils import encode

class FlashMessage(object):

    message = {
        'update': [
            _('Updating timeline...'),
            _('Couldn\'t retrieve tweets')
            ],
        'tweet': [
            _('Your tweet was sent'),
            _('Couldn\'t send tweet'),
            ],
        'retweet': [
            _('Your retweet was sent'),
            _('Couldn\'t send retweet'),
            ],
        'destroy': [
            _('You have deleted the tweet'),
            _('Couldn\'t delete tweet'),
            ],
        'favorite': [
            _('The tweet was added to favorites list'),
            _('Couldn\'t add tweet to favorites list'),
            ],
        'favorite_del': [
            _('Tweet was removed from favorites list'),
            _('Couldn\'t delete tweet on favorites list'),
            ],
        'direct': [
            _('Direct message was sent'),
            _('Couldn\'t send direct message'),
            ],
        'follow': [
            _('You are now following %s'),
            _('Couldn\'t follow %s')
            ],
        'unfollow': [
            _('You are not following %s anymore'),
            _('Couldn\'t stop following %s')
            ],
        'search': [
            _('Search results for %s'),
            _('Couldn\'t search for %s'),
            ],
        'empty': [
            '',''
        ]
        }

    def __init__(self):
        self.reset()

    def reset(self):
        self.level = 0
        self.event = 'empty'
        self.string = ''

    def warning(self):
        self.level = 1

    def get_msg(self):
        return self.compose_msg()

    def compose_msg(self):
        try:
            msg = self.message[self.event][self.level] % self.string
        except TypeError:
            msg = self.message[self.event][self.level]
        return ' ' +msg+ ' '

def print_ask_service(token_file):
    print ''
    print encode(_('Couldn\'t find any profile.'))
    print ''
    print encode(_('It should reside in: %s')) % token_file
    print encode(_('If you want to setup a new account, then follow these steps'))
    print encode(_('If you want to skip this, just press return or ctrl-C.'))
    print ''

    print ''
    print encode(_('Which service do you want to use?'))
    print ''
    print '1. Twitter'
    print '2. Identi.ca'
    print ''

def print_ask_root_url():
    print ''
    print ''
    print encode(_('Which root url do you want? (leave blank for default, https://identi.ca/api)'))
    print ''
