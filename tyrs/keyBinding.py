import os
import curses
import editBox

class KeyBinding:

    def __init__ (self, ui, conf, api):
        self.conf = conf
        self.ui = ui
        self.api = api

    def resizeEvent (self):
        self.ui.resize_event = False
        curses.endwin()
        self.ui.maxyx = self.ui.screen.getmaxyx()
        curses.doupdate()

    def moveDown (self):
        if self.ui.status['current'] < self.ui.status['count'] - 1:
            if self.ui.status['current'] >= self.ui.status['last']:
                self.ui.status['first'] += 1
            self.ui.status['current'] += 1

    def moveUp (self):
        if self.ui.status['current'] > 0:
            # if we need to move up the list to display
            if self.ui.status['current'] == self.ui.status['first']:
                self.ui.status['first'] -= 1
            self.ui.status['current'] -= 1

    def tweet (self, data):
        params = {'char': 200, 'width': 80, 'header': "What's up ?"}
        self.ui.refresh_token = True
        box = editBox.EditBox(self.ui.screen, params, data, self.conf)
        if box.confirm:
            try:
                self.api.postTweet(box.getContent())
                self.ui.flash = ['Tweet has been send successfully.', "info"]
            except:
                self.ui.flash = ["Couldn't send the tweet.", "warning"]
        self.ui.refresh_token = False

    def retweet (self):
        status = self.ui.statuses[self.ui.status['current']]
        try:
            self.api.retweet(status.GetId())
            self.ui.flash = ['Retweet has been send successfully.', 'info']
        except:
            self.ui.flash = ["Couldn't send the retweet.", 'warning']

    def retweetAndEdit (self):
        status = self.ui.getCurrentStatus()
        txt = status.text
        name = status.user.screen_name
        data = 'RT @%s: %s' % (name, txt)
        self.tweet(data)

    def clear (self):
        self.ui.clearStatuses()

    def update (self):
        self.ui.updateHomeTimeline()

    def followSelected (self):
        status = self.ui.getCurrentStatus()
        if self.ui.isRetweet(status):
            pseudo = self.ui.originOfRetweet(status)
        else:
            pseudo = status.user.screen_name
        self.createFriendship(pseudo)

    def unfollowSelected (self):
        pseudo = self.ui.getCurrentStatus().user.screen_name
        self.destroyFriendship(pseudo)

    def follow (self):
        self.ui.refresh_token = True
        box = self.pseudoBox('Follow Someone ?')
        self.createFriendship(self.cutAtTag(box.getContent()))
        self.ui.refresh_token = False

    def unfollow (self):
        self.ui.refresh_token = True
        box = self.pseudoBox('Unfollow Someone ?')
        self.destroyFriendship(self.cutAtTag(box.getContent()))
        self.ui.refresh_token = False

    def cutAtTag (self, name):
        if name[0] == '@':
            name = name[1:]
        return name

    def createFriendship (self, pseudo):
        try:
            self.api.CreateFriendship(pseudo)
            self.ui.flash = ['You are now following %s' % pseudo, 'info']
        except:
            self.ui.flash = ['Failed to follow %s' % pseudo, 'warning']

    def destroyFriendship (self, pseudo):
        try:
            self.api.DestroyFriendship(pseudo)
            self.ui.flash = ['You have unfollowed %s' % pseudo, 'info']
        except:
            self.ui.flash = ['Failed to unfollow %s' % pseudo, 'warning']

    def openurl (self):
        urls = self.ui.getUrls()
        for url in urls:
            #try:
            os.system(self.conf.params_openurl_command % url)
            #except:
                #self.ui.Flash  = ["Couldn't open url", 'warning']

    def pseudoBox (self, header):
        params = {'char': 40, 'width': 40, 'header': header}
        return editBox.EditBox(self.ui.screen, params, None, self.conf)

    def getMentions (self):
        self.ui.statuses = self.api.getMentions()
        self.changeBuffer()

    def getHome (self):
        self.ui.statuses = self.api.updateHomeTimeline()
        self.changeBuffer()

    def changeBuffer (self):
        self.ui.status['current'] = 0
        self.ui.status['first'] = 0
        self.ui.displayHomeTimeline()

    def handleKeyBinding (self):
        '''Should have all keybinding handle here'''
        while True:

            ch = self.ui.screen.getch()

            if self.ui.resize_event:
                self.resizeEvent()

            # Down and Up key must act as a menu, and should navigate
            # throught every tweets like an item.
            #

            # DOWN
            if ch == ord(self.conf.keys_down) or ch == curses.KEY_DOWN:
                self.moveDown()
            # UP
            elif ch == ord(self.conf.keys_up) or ch == curses.KEY_UP:
                self.moveUp()
            # TWEET
            elif ch == ord(self.conf.keys_tweet):
                self.tweet(None)
            # RETWEET
            elif ch == ord(self.conf.keys_retweet):
                self.retweet()
            # RETWEET AND EDIT
            elif ch == ord(self.conf.keys_retweet_and_edit):
                self.retweetAndEdit()
            # MENTIONS
            elif ch == ord(self.conf.keys_mentions):
                self.getMentions()
            # HOME TIMELINE
            elif ch == ord(self.conf.keys_home):
                self.getHome()
            # CLEAR
            elif ch == ord(self.conf.keys_clear):
                self.clear()
            # UPDATE
            elif ch == ord(self.conf.keys_update):
                self.update()
            # FOLLOW SELECTED
            elif ch == ord(self.conf.keys_follow_selected):
                self.followSelected()
            # UNFOLLOW SELECTED
            elif ch == ord(self.conf.keys_unfollow_selected):
                self.unfollowSelected()
            # FOLLOW
            elif ch == ord(self.conf.keys_follow):
                self.follow()
            # UNFOLLOW
            elif ch == ord(self.conf.keys_unfollow):
                self.unfollow()
            # OPENURL
            elif ch == ord(self.conf.keys_openurl):
                self.openurl()
            # QUIT
            # 27 corresponding to the ESC, couldn't find a KEY_* corresponding
            elif ch == ord(self.conf.keys_quit) or ch == 27:
                break

            self.ui.displayHomeTimeline()
