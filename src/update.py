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

import tyrs
import time
import logging
import threading

class UpdateThread(threading.Thread):
    '''
    The only thread that update all timelines
    '''

    def __init__(self):
        self.interface = tyrs.container['interface']
        self.conf = tyrs.container['conf']
        self.api = tyrs.container['api']
        threading.Thread.__init__(self, target=self.run)
        self._stopevent = threading.Event()

    def run(self):
        self.update_timeline()
        logging.info('Thread started')
        for i in range(self.conf.params['refresh'] * 60):
            time.sleep(1)
            if self._stopevent.isSet() or self.interface.stoped:
                logging.info('Thread forced to stop')
                return
        self.start_new_thread()
        logging.info('Thread stoped')
        self.stop()

    def stop(self):
        self._stopevent.set()

    def start_new_thread(self):
        update = UpdateThread()
        update.start()

    def update_timeline(self):
        timeline = ('home', 'mentions', 'direct')
        for t in timeline:
            self.api.update_timeline(t)
        self.interface.display_timeline()
        self.interface.redraw_screen()
