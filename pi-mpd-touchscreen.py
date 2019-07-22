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
__author__ = 'Mark Zwart'
import sys, pygame
from time import sleep
from pygame import *
# from gui_screens import *
# from config_file import *
# from settings import *
from mpd_client import *
# from screen_player import *
# from screen_library import *
# from screen_directory import *
# from screen_radio import *
# from screen_settings import *


# class PiJukeboxScreens(ScreenControl):
#     """ Manages Pi Jukebox's main screens.
#             - Player screen
#             - Library screen
#         Handles screen switching, clicking and swiping and displaying mpd status
#         updates on screen(s)
#     """
#     def __init__(self):
#         ScreenControl.__init__(self)
#
#         #self.add_screen(ScreenPlaying(SCREEN), self.loop_hook)  # Screen with now playing and cover art
#         #self.add_screen(ScreenPlaylist(SCREEN), self.loop_hook)  # Create player with playlist screen
#         #self.add_screen(ScreenLibrary(SCREEN), self.loop_hook)  # Create library browsing screen
#         #self.add_screen(ScreenDirectory(SCREEN), self.loop_hook)  # Create directory browsing screen
#         #self.add_screen(ScreenRadio(SCREEN), self.loop_hook)  # Create radio station managing screen
#
#     def mpd_updates(self):
#         """ Updates a current screen if it shows mpd relevant content. """
#         #self.screen_list[self.current_index].update()
#
#     def loop_hook(self):
#         #return mpd.status_get()
#
#     def update(self):
#         #pass
#
#
# def apply_settings():
#     # Check for first time settings
#     if not config_file.setting_exists('MPD Settings', 'music directory'):
#         screen_message = ScreenMessage(SCREEN, 'No music directory',
#                                        "If you want to display cover art, Pi-Jukebox needs to know which directory your music collection is in. The location can also be found in your mpd.conf entry 'music directory'.",
#                                        'warning')
#         screen_message.show()
#         settings_mpd_screen = ScreenSettingsMPD(SCREEN)
#         settings_mpd_screen.keyboard_setting("Set music directory", 'MPD Settings', 'music directory',
#                                              '/var/lib/mpd/music/')
#     mpd.host = config_file.setting_get('MPD Settings', 'host')
#     mpd.port = int(config_file.setting_get('MPD Settings', 'port'))
#     mpd.music_directory_set(config_file.setting_get('MPD Settings', 'music directory'))
#     if not config_file.section_exists('Radio stations'):
#         config_file.setting_set('Radio stations', "Radio Swiss Jazz", "http://stream.srg-ssr.ch/m/rsj/mp3_128")


def main():
    """ The function where it all starts...."""
    pygame.display.set_caption("Pi Jukebox")
    # apply_settings()  # Check for first time settings and applies settings

    # Check whether mpd is running and get it's status
    if not mpd.connect():
        print("Couldn't connect to the mpd server " + mpd.host + " on port " + str(
            mpd.port) + "! Check settings in file pi-jukebox.conf or check is server is running 'sudo service mpd status'.")
        sys.exit()
    mpd.status_get()  # Get mpd status
    #screens = PiJukeboxScreens()  # Screens
    #screens.show()  # Display the screen

    pygame.init()
    sleep(0.2)
    pygame.display.update()


if __name__ == '__main__':
    main()
