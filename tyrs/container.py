# -*- coding: utf-8 -*-
'''
@module     container
@author     Nicolas Paris <nicolas.caen@gmail.com>
@licence    GPLv3
'''
class Container:
    '''
    Contain main classes that we need thought all the programm
    such as conf, api and ui
    '''
    _container = {}

    def __setitem__ (self, key, value):
        self._container[key] = value

    def __getitem__ (self, key):
        return self._container[key]

    def add (self, name, dependency):
        self[name] = dependency
