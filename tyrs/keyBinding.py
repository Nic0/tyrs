import curses

class KeyBinding:

    def __init__ (self, ui, conf, api):
        self.conf = conf
        self.ui = ui
        self.api = api

    def handleKeyBinding(self):
        '''Should have all keybinding handle here'''
        while True:

            ch = self.ui.screen.getch()

            needRefresh = False

            if self.ui.resize_event:
                self.ui.resize_event = False
                curses.endwin()
                self.ui.maxyx = self.ui.screen.getmaxyx()
                curses.doupdate()
                needRefresh = True

            # Down and Up key must act as a menu, and should navigate
            # throught every tweets like an item.
            #
            # MOVE DOWN
            #
            if ch == ord(self.conf.keys_down) or ch == curses.KEY_DOWN:
                if self.ui.status['current'] < self.ui.status['count'] - 1:
                    if self.ui.status['current'] >= self.ui.status['last']:
                    # We need to be sure it will have enough place to
                    # display the next tweet, otherwise we still stay
                    # to the current tweet
                    # This is due to the dynamic height of a tweet.

                    # height_first_status = self.getSizeStatus(self.statuses[self.status['first']])
                    # next_status = self.status['last'] + 1
                    # height_next_status  = self.getSizeStatus(self.statuses[next_status])
                    # height_left = self.current_y - self.maxyx[0]-1
                    # if height_next_status['height'] > (height_left + height_first_status['height']):
                    #     self.status['current'] -=

                        self.ui.status['first'] += 1


                    self.ui.status['current'] += 1
                    needRefresh = True
            # MOVE UP
            elif ch == ord(self.conf.keys_up) or ch == curses.KEY_UP:
                # the current tweet must not be the first one of the statuses
                # list
                if self.ui.status['current'] > 0:
                    # if we need to move up the list to display
                    if self.ui.status['current'] == self.ui.status['first']:
                        self.ui.status['first'] -= 1
                    self.ui.status['current'] -= 1
                    needRefresh = True

            # TWEET
            elif ch == ord(self.conf.keys_tweet):
                self.ui.refresh_token = True
                box = editBox.EditBox(self.screen)
                if box.confirm:
                    try:
                        self.api.postTweet(box.getTweet())
                        self.ui.flash = [True, 'info', 'Tweet has been send successfully.']
                    except:
                        self.ui.flash = [True, 'warning', "Couldn't send the tweet."]
                needRefresh = True
                self.ui.refresh_token = False

            # RETWEET
            if ch == ord(self.conf.keys_retweet):
                status = self.ui.statuses[self.status['current']]
                try:
                    self.api.retweet(status.GetId())
                    self.ui.flash = [True, 'info', 'Retweet has been send successfully.']
                except:
                    self.ui.flash = [True, 'warning', "Couldn't send the retweet."]
                needRefresh = True

            # CLEAR
            elif ch == ord(self.conf.keys_clear):
                self.ui.clearStatuses()
                self.ui.countStatuses()
                self.ui.status['current'] = 0
                needRefresh = True

            # UPDATE
            elif ch == ord(self.conf.keys_update):
                self.ui.updateHomeTimeline()
                needRefresh = True

            # QUIT
            # 27 corresponding to the ESC, couldn't find a KEY_* corresponding
            elif ch == ord(self.conf.keys_quit) or ch == 27:
                break

            if needRefresh:
                self.ui.displayHomeTimeline()
