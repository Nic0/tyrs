# -*- coding:utf-8 -*-

import threading

class UpdateThread (threading.Thread):

    def __init__ (self, container):
        self.ui = container['ui']
        self.conf = container['conf']
        threading.Thread.__init__(self, target=self.run)
        self._stopevent = threading.Event()


    def run (self):
        while not self._stopevent.isSet():
            self._stopevent.wait(self.conf.params['refresh'] * 60.0)
            if not self._stopevent.isSet():
                self.ui.updateTimeline('home')
                self.ui.updateTimeline('mentions')
                self.ui.updateTimeline('direct')
                self.ui.displayTimeline()

    def stop (self):
        self._stopevent.set()
