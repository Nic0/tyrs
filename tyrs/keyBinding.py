import os
import curses
import editBox
import uiTyrs

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

    def moveBuffer (self, move):
        buffer = ['home', 'mentions', 'direct', 'search', 'user', 'favorite']
        id = buffer.index(self.ui.buffer)
        new_id = id + move
        if new_id >= 0 and new_id < len(buffer):
            self.changeBuffer(buffer[new_id])

    def tweet (self, data, reply_to_id=None, dm=False):
        params = {'char': 200, 'width': 80, 'header': "What's up ?"}
        box = editBox.EditBox(self.ui, params, data, self.conf)
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

    def delete (self):
        id = self.ui.getCurrentStatus().GetId()
        # In case we want delete direct message, it will handle
        # with DestroyDirectMessage(id)
        try:
            self.api.api.DestroyStatus(id)
            self.ui.flash = ['Tweet destroyed successfully.', 'info']
        except:
            self.ui.flash = ['The tweet could not been destroyed.', 'warning']

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
        nick = self.pseudoBox('Follow Someone ?')
        if nick != False:
            self.createFriendship(nick)

    def unfollow (self):
        nick = self.pseudoBox('Unfollow Someone ?')
        if nick != False:
            self.destroyFriendship(nick)

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

    def setFavorite (self):
        status = self.ui.getCurrentStatus()
        try:
            self.api.api.CreateFavorite(status)
            self.ui.flash = ['The tweet is now in your favorite list', 'info']
        except:
            self.ui.flash = ['Could not set the current tweet as favorite', 'warning']

    def getFavorites (self):
        self.changeBuffer('favorite')

    def destroyFavorite (self):
        status = self.ui.getCurrentStatus()
        try:
            self.api.api.DestroyFavorite(status)
            self.ui.flash = ['The current favorite has been destroyed', 'info']
        except:
            self.ui.flash = ['Could not destroy the favorite tweet', 'warning']

    def openurl (self):
        urls = self.ui.getUrls()
        for url in urls:
            #try:
            os.system(self.conf.params['openurl_command'] % url)
            #except:
                #self.ui.Flash  = ["Couldn't open url", 'warning']

    def pseudoBox (self, header, pseudo=None):
        params = {'char': 40, 'width': 40, 'header': header}
        box = editBox.EditBox(self.ui, params, pseudo, self.conf)
        if box.confirm:
            return self.cutAtTag(box.getContent())
        else:
            return False

    def userTimeline (self, myself=False):
        if not myself:
            nick = self.pseudoBox('Looking for someone?')
        else:
            nick = self.api.me.screen_name
        if nick != False:
            if self.api.search_user != nick:
                self.ui.emptyDict('user')
            self.api.search_user = nick
            self.changeBuffer('user')

    def search (self):
        self.ui.buffer = 'search'
        self.api.search_word = self.pseudoBox('What should I search?')
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

        pseudo = self.pseudoBox("Send a Direct Message at whom ?", pseudo)
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
            if ch == self.conf.keys['down'] or ch == curses.KEY_DOWN:
                self.moveDown()
            # UP
            elif ch == self.conf.keys['up'] or ch == curses.KEY_UP:
                self.moveUp()
            # LEFT
            elif ch == self.conf.keys['left'] or ch == curses.KEY_LEFT:
                self.moveBuffer(-1)
            # RIGHT
            elif ch == self.conf.keys['right'] or ch == curses.KEY_RIGHT:
                self.moveBuffer(+1)
            # TWEET
            elif ch == self.conf.keys['tweet']:
                self.tweet(None)
            # RETWEET
            elif ch == self.conf.keys['retweet']:
                self.retweet()
            # RETWEET AND EDIT
            elif ch == self.conf.keys['retweet_and_edit']:
                self.retweetAndEdit()
            # DELETE TwEET
            elif ch == self.conf.keys['delete']:
                self.delete()
            # MENTIONS
            elif ch == self.conf.keys['mentions']:
                self.changeBuffer('mentions')
            # HOME TIMELINE
            elif ch == self.conf.keys['home']:
                self.changeBuffer('home')
            # CLEAR
            elif ch == self.conf.keys['clear']:
                self.clear()
            # UPDATE
            elif ch == self.conf.keys['update']:
                self.update()
            # FOLLOW SELECTED
            elif ch == self.conf.keys['follow_selected']:
                self.followSelected()
            # UNFOLLOW SELECTED
            elif ch == self.conf.keys['unfollow_selected']:
                self.unfollowSelected()
            # FOLLOW
            elif ch == self.conf.keys['follow']:
                self.follow()
            # UNFOLLOW
            elif ch == self.conf.keys['unfollow']:
                self.unfollow()
            # OPENURL
            elif ch == self.conf.keys['openurl']:
                self.openurl()
            # BACK ON TOP
            elif ch == self.conf.keys['back_on_top']:
                self.changeBuffer(self.ui.buffer)
            # BACK ON BOTTOM
            elif ch == self.conf.keys['back_on_bottom']:
                self.backOnBottom()
            # REPLY
            elif ch == self.conf.keys['reply']:
                self.reply()
            # GET DIRECT MESSAGE
            elif ch == self.conf.keys['getDM']:
                self.changeBuffer('direct')
            # SEND DIRECT MESSAGE
            elif ch == self.conf.keys['sendDM']:
                self.sendDirectMessage()
            # SEARCH
            elif ch == self.conf.keys['search']:
                self.search()
            # SEARCH USER
            elif ch == self.conf.keys['search_user']:
                self.userTimeline()
            # SEARCH MYSELF
            elif ch == self.conf.keys['search_myself']:
                self.userTimeline(True)
            # Redraw screen
            elif ch == self.conf.keys['redraw']:
                self.ui.displayRedrawScreen()
            # Help
            elif ch == ord('?'):
                uiTyrs.Help(self.ui, self.conf)
            # Create favorite
            elif ch == self.conf.keys['fav']:
                self.setFavorite()
            # Get favorite
            elif ch == self.conf.keys['get_fav']:
                self.getFavorites()
            # Destroy favorite
            elif ch == self.conf.keys['delete_fav']:
                self.destroyFavorite()
            # QUIT
            # 27 corresponding to the ESC, couldn't find a KEY_* corresponding
            elif ch == self.conf.keys['quit'] or ch == 27:
                break

            self.ui.displayTimeline()

