# -*- coding: utf-8 -*-
'''
   @module   help 
   @author   Nicolas Paris <nicolas.caen@gmail.com>
   @license  GPLv3
'''
import tyrs
import curses

class Help:

    y = 2
    col = [2, 25, 30]

    def __init__ (self):
        self.interface = tyrs.container['interface']
        self.conf = tyrs.container['conf']
        self.max = self.interface.screen.getmaxyx()
        self.display_help_screen()

    def display_help_screen (self):
        self.interface.refresh_token = True
        self.interface.screen.erase()

        self.display_header()
        # Navigation
        self.display_division('Navigation')
        self.display_help_item('up', 'Moves up')
        self.display_help_item('down', 'Moves down')
        self.display_help_item('back_on_top', 'Move back on top')
        self.display_help_item('back_on_bottom', 'Move to the bottom of the screen')
        # Timelines
        self.display_division('Timelines')
        self.display_help_item('left', 'Moves left in timelines')
        self.display_help_item('right', 'Moves right in timelines')
        self.display_help_item('update', 'Refresh the current timeline')
        self.display_help_item('clear', 'Clear, and leave the last tweet in your timeline')
        self.display_help_item('home', 'Moves to the home timeline')
        self.display_help_item('mentions', 'Moves to the mentions timeline')
        self.display_help_item('getDM', 'Moves to the direct message timeline')
        self.display_help_item('search', 'Ask for a term to search and move to his timeline')
        self.display_help_item('search_user', 'Retrieve someone public timeline')
        self.display_help_item('search_myself', 'Retrieve your public timeline')
        # Tweets
        self.display_division('Tweets')
        self.display_help_item('tweet', 'Send a tweet')
        self.display_help_item('retweet', 'Retweet the selected tweet')
        self.display_help_item('retweet_and_edit', 'Retweet with response the selected tweet')
        self.display_help_item('reply', 'Reply to the selected tweet')
        self.display_help_item('sendDM', 'Send a direct message')
        self.display_help_item('delete', 'Delete the selected tweet, must be your tweet')
        # Follow/Unfollow
        self.display_division('Follow/Unfollow')
        self.display_help_item('follow_selected', 'Follow the selected twitter')
        self.display_help_item('unfollow_selected', 'Unfollow the selected twitter')
        self.display_help_item('follow', 'Follow a twitter')
        self.display_help_item('unfollow', 'Unfollow a twitter')
        # Others
        self.display_division('Others')
        self.display_help_item('quit', 'Leave Tyrs')
        self.display_help_item('openurl', 'Open an url with your browser')
        self.display_help_item('redraw', 'Force to redraw the screen')

        self.interface.screen.refresh()
        self.interface.screen.getch()
        self.interface.screen.erase()

        self.interface.refresh_token = False

    def display_division (self, title):
        self.increase(2)
        color = curses.color_pair(5)
        title = '-- ' + title + ' --'
        self.interface.screen.addstr(self.y, self.col[0], title, color)
        self.increase(1)

    def display_header (self):
        scr = self.interface.screen
        color = curses.color_pair(5)
        scr.addstr(self.y, self.col[0], 'Name', color)
        scr.addstr(self.y, self.col[1], 'Key', color)
        scr.addstr(self.y, self.col[2], 'Description', color)

    def display_help_item (self, key, description):
        scr = self.interface.screen
        color = self.interface.get_color('help')
        scr.addstr(self.y, self.col[0], key, color)
        scr.addstr(self.y, self.col[1], chr(self.conf.keys[key]), color)
        scr.addstr(self.y, self.col[2], description, color)
        self.increase(1)

    def increase (self, incr):
        '''This make sure there some space left on the screen.'''
        if self.y + incr >= self.max[0]:
            self.interface.screen.refresh()
            self.interface.screen.getch()
            self.y = 2
            self.interface.screen.erase()
            self.display_header()
            self.increase(2)
        else:
            self.y += incr
