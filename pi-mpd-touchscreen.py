# This file is part of pi-jukebox.
#
# pi-jukebox is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pi-jukebox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with pi-jukebox. If not, see < http://www.gnu.org/licenses/ >.
#
# (C) 2015- by Mark Zwart, <mark.zwart@pobox.com>

"""
**pi-mpd-touchscreen.py**: Main file
"""
from screen_blank import *
from screen_player import *
from settings import *
from mpd_client import *
from time import sleep
import sys
import signal
__author__ = 'Mark Zwart'

import logging

logging.basicConfig(filename='pi-mpd-touchscreen.log',
                    format='%(asctime)s:%(levelname)s:%(message)s',
                    level=logging.WARNING)


class PiJukeboxScreens(ScreenControl):
    """ Manages Pi Jukebox's main screens.
            - Player screen
            - Library screen
        Handles screen switching, clicking and swiping and displaying mpd status
        updates on screen(s)
    """

    def __init__(self):
        logging.info("Start screens")
        ScreenControl.__init__(self)

        self.timer = pygame.time.get_ticks
        self.blank_screen_time = self.timer() + BLANK_PERIOD
        # Screen with now playing and cover art
        self.add_screen(ScreenPlaying(SCREEN), self.loop_hook)
        self.add_screen(ScreenBlank(SCREEN), self.loop_hook)

    def mpd_updates(self):
        """ Updates a current screen if it shows mpd relevant content. """
        self.screen_list[self.current_index].update()

    def loop_hook(self):
        mpd_status = mpd.status_get()
        mpd_control_status = mpd.player_control_get()
        is_playing = mpd_control_status != 'pause' and mpd_control_status != 'stop'
        if is_playing:
            self.blank_screen_time = self.timer() + BLANK_PERIOD
            if self.current_index != 0:
                self.current_index = 0
                self.show()
        elif not is_playing and self.timer() > self.blank_screen_time and self.current_index != 1:
            self.current_index = 1
            self.show()

        return mpd_status

    def update(self):
        pass


def main():
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit())

    logging.info("Starting main")
    """ The function where it all starts...."""
    if "SSH_CONNECTION" in os.environ:
        print("Not starting pi-mpd-touchscreen, ssh session")

    pygame.display.set_caption("Pi Jukebox")
    # apply_settings()  # Check for first time settings and applies settings

    # Check whether mpd is running and get it's status
    if not mpd.connect():
        print("Couldn't connect to the mpd server " + mpd.host + " on port " + str(
            mpd.port) + "! Check settings in file pi-jukebox.conf or check is server is running 'systemctl status mpd'.")
        sys.exit()

    mpd.status_get()  # Get mpd status
    screens = PiJukeboxScreens()  # Screens
    screens.show()  # Display the screen

    pygame.init()
    sleep(0.2)
    pygame.display.update()


if __name__ == '__main__':
    main()
