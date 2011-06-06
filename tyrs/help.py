# -*- coding:utf-8 -*-

import tyrs
import curses

class Help:

    y = 2
    col = [2, 25, 30]

    def __init__ (self):
        self.interface = tyrs.container['interface']
        self.conf = tyrs.container['conf']
        self.max = self.interface.screen.getmaxyx()
        self.displayHelpScreen()

    def displayHelpScreen (self):
        self.interface.refresh_token = True
        self.interface.screen.erase()

        self.displayHeader()
        # Navigation
        self.displayDivision('Navigation')
        self.displayHelpItem('up', 'Moves up')
        self.displayHelpItem('down', 'Moves down')
        self.displayHelpItem('back_on_top', 'Move back on top')
        self.displayHelpItem('back_on_bottom', 'Move to the bottom of the screen')
        # Timelines
        self.displayDivision('Timelines')
        self.displayHelpItem('left', 'Moves left in timelines')
        self.displayHelpItem('right', 'Moves right in timelines')
        self.displayHelpItem('update', 'Refresh the current timeline')
        self.displayHelpItem('clear', 'Clear, and leave the last tweet in your timeline')
        self.displayHelpItem('home', 'Moves to the home timeline')
        self.displayHelpItem('mentions', 'Moves to the mentions timeline')
        self.displayHelpItem('getDM', 'Moves to the direct message timeline')
        self.displayHelpItem('search', 'Ask for a term to search and move to his timeline')
        self.displayHelpItem('search_user', 'Retrieve someone public timeline')
        self.displayHelpItem('search_myself', 'Retrieve your public timeline')
        # Tweets
        self.displayDivision('Tweets')
        self.displayHelpItem('tweet', 'Send a tweet')
        self.displayHelpItem('retweet', 'Retweet the selected tweet')
        self.displayHelpItem('retweet_and_edit', 'Retweet with response the selected tweet')
        self.displayHelpItem('reply', 'Reply to the selected tweet')
        self.displayHelpItem('sendDM', 'Send a direct message')
        self.displayHelpItem('delete', 'Delete the selected tweet, must be your tweet')
        # Follow/Unfollow
        self.displayDivision('Follow/Unfollow')
        self.displayHelpItem('follow_selected', 'Follow the selected twitter')
        self.displayHelpItem('unfollow_selected', 'Unfollow the selected twitter')
        self.displayHelpItem('follow', 'Follow a twitter')
        self.displayHelpItem('unfollow', 'Unfollow a twitter')
        # Others
        self.displayDivision('Others')
        self.displayHelpItem('quit', 'Leave Tyrs')
        self.displayHelpItem('openurl', 'Open an url with your browser')
        self.displayHelpItem('redraw', 'Force to redraw the screen')

        self.interface.screen.refresh()
        self.interface.screen.getch()
        self.interface.screen.erase()

        self.interface.refresh_token = False

    def displayDivision (self, title):
        self.increase(2)
        cp = curses.color_pair(5)
        title = '-- ' + title + ' --'
        self.interface.screen.addstr(self.y, self.col[0], title, cp)
        self.increase(1)

    def displayHeader (self):
        scr = self.interface.screen
        cp = curses.color_pair(5)
        scr.addstr(self.y, self.col[0], 'Name', cp)
        scr.addstr(self.y, self.col[1], 'Key', cp)
        scr.addstr(self.y, self.col[2], 'Description', cp)

    def displayHelpItem (self, key, description):
        scr = self.interface.screen
        cp = self.interface.getColor('help')
        scr.addstr(self.y, self.col[0], key, cp)
        scr.addstr(self.y, self.col[1], chr(self.conf.keys[key]), cp)
        scr.addstr(self.y, self.col[2], description, cp)
        self.increase(1)

    def increase (self, incr):
        '''This make sure there some space left on the screen.'''
        if self.y + incr >= self.max[0]:
            self.interface.screen.refresh()
            self.interface.screen.getch()
            self.y = 2
            self.interface.screen.erase()
            self.displayHeader()
            self.increase(2)
        else:
            self.y += incr
