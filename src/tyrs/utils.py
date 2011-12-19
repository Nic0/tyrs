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
#import tyrs
import string
from htmlentitydefs import entitydefs

def set_console_title():
    try:
        sys.stdout.write("\x1b]2;Tyrs\x07")
    except:
        pass

def cut_attag(name):
    if name[0] == '@':
        name = name[1:]
    return name

def get_exact_nick(word):
    if word[0] == '@':
        word = word[1:]
    alphanum = string.letters + string.digits
    try:
        while word[-1] not in alphanum:
            word = word[:-1]
    except IndexError:
        pass
    return word

def encode(string):
    try:
        return string.encode(sys.stdout.encoding, 'replace')
    except AttributeError:
        return string

def html_unescape(str):
    """ Unescapes HTML entities """
    def entity_replacer(m):
        entity = m.group(1)
        if entity in entitydefs:
            return entitydefs[entity]
        else:
            return m.group(0)

    return re.sub(r'&([^;]+);', entity_replacer, str)


def get_source(source):
    if source != 'web':
        source = source.split('>')
        source = source[1:]
        source = ' '.join(source)
        source = source.split('<')[:1]
        source = source[:1]
        source = ' '.join(source)
    return source

def open_image(user):
    image = user.profile_image_url
    command = tyrs.container['conf'].params['open_image_command']
    os.system(command % image)


def get_urls(text):
    return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
