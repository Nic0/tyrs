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
        if self.ui.status['current'] < self.ui.count[self.ui.buffer] - 1:
            if self.ui.status['current'] >= self.ui.status['last']:
                self.ui.status['first'] += 1
            self.ui.status['current'] += 1

    def moveUp (self):
        if self.ui.status['current'] > 0:
            # if we need to move up the list to display
            if self.ui.status['current'] == self.ui.status['first']:
                self.ui.status['first'] -= 1
            self.ui.status['current'] -= 1

    def tweet (self, data, reply_to_id=None, dm=False):
        params = {'char': 200, 'width': 80, 'header': "What's up ?"}
        self.ui.refresh_token = True
        box = editBox.EditBox(self.ui.screen, params, data, self.conf)
        if box.confirm:
            try:
                content = box.getContent()
                if not dm:
                    self.api.postTweet(content, reply_to_id)
                    self.ui.flash = ['Tweet has been send successfully.', "info"]
                else:
                    # note in the DM case, we have a screen_name, and not the id
                    self.api.api.PostDirectMessage(reply_to_id, content)
                    self.ui.flash = ['The direct message has benn send.', 'info']
            except:
               self.ui.flash = ["Couldn't send the tweet.", "warning"]
        self.ui.refresh_token = False

    def retweet (self):
        status = self.ui.getCurrentStatus()
        try:
            self.api.api.PostRetweet(status.GetId())
            self.ui.flash = ['Retweet has been send successfully.', 'info']
        except:
            self.ui.flash = ["Couldn't send the retweet.", 'warning']

    def retweetAndEdit (self):
        status = self.ui.getCurrentStatus()
        txt = status.text
        name = status.user.screen_name
        data = 'RT @%s: %s' % (name, txt)
        self.tweet(data)

    def reply (self):
        status = self.ui.getCurrentStatus()
        reply_to_id = status.GetId()
        data = '@'+status.user.screen_name
        self.tweet(data, reply_to_id)

    def clear (self):
        self.ui.clearStatuses()

    def update (self):
        self.ui.updateTimeline(self.ui.buffer)

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
            self.api.api.CreateFriendship(pseudo)
            self.ui.flash = ['You are now following %s' % pseudo, 'info']
        except:
            self.ui.flash = ['Failed to follow %s' % pseudo, 'warning']

    def destroyFriendship (self, pseudo):
        try:
            self.api.api.DestroyFriendship(pseudo)
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

    def pseudoBox (self, header, pseudo=None):
        params = {'char': 40, 'width': 40, 'header': header}
        return editBox.EditBox(self.ui.screen, params, pseudo, self.conf)

    def search (self):
        self.ui.buffer = 'search'
        self.api.search_word = self.pseudoBox('What should I search?').getContent()
        try:
            self.ui.statuses['search'] = self.api.api.GetSearch(self.api.search_word)
            self.changeBuffer('search')
            if len(self.ui.statuses['search']) == 0:
                self.ui.flash = ['The research does not return any result', 'info']
        except:
            self.ui.flash = ['Failed with the research']

    def sendDirectMessage (self):
        ''' Two editing box, one for the name, and one for the content'''
        try:
            status = self.ui.getCurrentStatus()
            try:
                pseudo = status.user.screen_name
            except:
                pseudo = status.sender_screen_name
        except:
            pseudo = ''

        pseudobox = self.pseudoBox("Send a Direct Message at whom ?", pseudo)
        pseudo = pseudobox.getContent()
        self.tweet(False, pseudo, True)

    def changeBuffer (self, buffer):
        self.ui.buffer = buffer
        self.ui.status['current'] = 0
        self.ui.status['first'] = 0
        self.ui.countUnread(buffer)
        self.ui.displayTimeline()

    def backOnBottom (self):
        self.ui.status['current'] = self.ui.status['last']

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
            if ch == self.conf.keys_down or ch == curses.KEY_DOWN:
                self.moveDown()
            # UP
            elif ch == self.conf.keys_up or ch == curses.KEY_UP:
                self.moveUp()
            # TWEET
            elif ch == self.conf.keys_tweet:
                self.tweet(None)
            # RETWEET
            elif ch == self.conf.keys_retweet:
                self.retweet()
            # RETWEET AND EDIT
            elif ch == self.conf.keys_retweet_and_edit:
                self.retweetAndEdit()
            # MENTIONS
            elif ch == self.conf.keys_mentions:
                self.changeBuffer('mentions')
            # HOME TIMELINE
            elif ch == self.conf.keys_home:
                self.changeBuffer('home')
            # CLEAR
            elif ch == self.conf.keys_clear:
                self.clear()
            # UPDATE
            elif ch == self.conf.keys_update:
                self.update()
            # FOLLOW SELECTED
            elif ch == self.conf.keys_follow_selected:
                self.followSelected()
            # UNFOLLOW SELECTED
            elif ch == self.conf.keys_unfollow_selected:
                self.unfollowSelected()
            # FOLLOW
            elif ch == self.conf.keys_follow:
                self.follow()
            # UNFOLLOW
            elif ch == self.conf.keys_unfollow:
                self.unfollow()
            # OPENURL
            elif ch == self.conf.keys_openurl:
                self.openurl()
            # BACK ON TOP
            elif ch == self.conf.keys_back_on_top:
                self.changeBuffer(self.ui.buffer)
            # BACK ON BOTTOM
            elif ch == self.conf.keys_back_on_bottom:
                self.backOnBottom()
            # REPLY
            elif ch == self.conf.keys_reply:
                self.reply()
            # GET DIRECT MESSAGE
            elif ch == self.conf.keys_getDM:
                self.changeBuffer('direct')
            # SEND DIRECT MESSAGE
            elif ch == self.conf.keys_sendDM:
                self.sendDirectMessage()
            elif ch == self.conf.keys_search:
                self.search()

            # QUIT
            # 27 corresponding to the ESC, couldn't find a KEY_* corresponding
            elif ch == self.conf.keys_quit or ch == 27:
                break

            self.ui.displayTimeline()
