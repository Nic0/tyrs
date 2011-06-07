# -*- coding: utf-8 -*-
'''
@module     update
@author     Nicolas Paris <nicolas.caen@gmail.com>
@licence    GPLv3
'''
import tyrs
import threading

class UpdateThread(threading.Thread):
    '''
    The only thread that update all timelines
    '''
    def __init__(self):
        self.interface = tyrs.container['interface']
        self.conf = tyrs.container['conf']
        threading.Thread.__init__(self, target=self.run)
        self._stopevent = threading.Event()

    def run(self):
        while not self._stopevent.isSet():
            self._stopevent.wait(self.conf.params['refresh'] * 60.0)
            if not self._stopevent.isSet():
                self.interface.update_timeline('home')
                self.interface.update_timeline('mentions')
                self.interface.update_timeline('direct')
                self.interface.display_timeline()

    def stop(self):
        self._stopevent.set()
