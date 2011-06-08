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

class FlashMessage:

    message = {
        'update': ['Updating timeline...'],
        'tweet': [
            'Your tweet has been sent',
            'Could not send the tweet',
            ],
        'retweet': [
            'Your retweet has been sent',
            'Could not send the retweet',
            ],
        'destroy': [
            'You have destroyed the tweet',
            'Could not destroyed the tweet',
            ],
        'favorite': [
            'The tweet is now in you favorite list',
            'Could not added the tweet in your favorite list',
            ],
        'favorite_del': [
            'Your favorite tweet has been destroyed',
            'Could not destroyed the favorite tweet',
            ],
        'direct': [
            'You direct message has been sent',
            'Could not send the direct message',
            ],
        'follow': [
            'You are now following %s',
            'You could not follow %s'
            ],
        'unfollow': [
            'You have unfollowed %s',
            'You could not followed %s'
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
