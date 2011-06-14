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
            _('Could not retrieve tweets')
            ],
        'tweet': [
            _('Your tweet has been sent'),
            _('Could not send the tweet'),
            ],
        'retweet': [
            _('Your retweet has been sent'),
            _('Could not send the retweet'),
            ],
        'destroy': [
            _('You have destroyed the tweet'),
            _('Could not destroyed the tweet'),
            ],
        'favorite': [
            _('The tweet is now in your favorite list'),
            _('Could not add the tweet in your favorite list'),
            ],
        'favorite_del': [
            _('Your favorite tweet has been destroyed'),
            _('Could not destroy the favorite tweet'),
            ],
        'direct': [
            _('You direct message has been sent'),
            _('Could not send the direct message'),
            ],
        'follow': [
            _('You are now following %s'),
            _('You could not follow %s')
            ],
        'unfollow': [
            _('You have unfollowed %s'),
            _('You could not follow %s')
            ],
        'search': [
            _('Result for search with %s'),
            _('Could not search for %s'),
            ],
        }

    def __init__(self):
        self.reset()

    def reset(self):
        self.level = 0
        self.event = None
        self.string = None

    def warning(self):
        self.level = 1

    def get_msg(self):
        return self.compose_msg()

    def compose_msg(self):
        msg = self.message[self.event][self.level]
        if self.string != None: 
            msg = self.message[self.event][self.level] % self.string
        
        return ' ' +msg+ ' '

def print_ask_service(config_file):
    print ''
    print encode(_('There is no profile detected.'))
    print ''
    print encode(_('It should be in %s')) % config_file
    print encode(_('If you want to setup a new account, let\'s go through some basic steps'))
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
    print encode(_('Which root url do you want? (leave blank for default value, https://identi.ca/api)'))
    print ''
