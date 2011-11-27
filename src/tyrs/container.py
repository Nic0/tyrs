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

class Container(object):
    '''
    Contain main classes that we need thought all the programm
    such as conf, api and ui
    '''
    _container = {}

    def __setitem__(self, key, value):
        self._container[key] = value

    def __getitem__(self, key):
        return self._container[key]

    def add(self, name, dependency):
        self[name] = dependency
