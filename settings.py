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

================================================
**settings.py**: Contains project wide variables
================================================

"""
__author__ = 'Mark Zwart'

import logging

logging.info("Start loading settings")
import os
os.environ['SDL_AUDIODRIVER'] = 'dsp'
import pygame

# Sound spectrometer settings
INPUT_DEVICE_INDEX = 4
INPUT_SOUND_RATE = 10000 # 44100
INPUT_BLOCK_TIME = 0.005 # 30 ms

#: Switches between development/debugging on your desktop/laptop versus running on your Raspberry Pi
RUN_ON_RASPBERRY_PI = os.uname()[4] == 'aarch64'

# Setting up touch screen, set if statement to true on Raspberry Pi
if RUN_ON_RASPBERRY_PI:
    os.environ['SDL_FBDEV'] = '/dev/fb1'
    INPUT_DEVICE_INDEX = 9

# Display settings
pygame.init() 	# Pygame initialization
#: The display dimensions, change this if you have a bigger touch screen.
DISPLAY_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 800, 480
PYGAME_EVENT_DELAY = 0 #25

if RUN_ON_RASPBERRY_PI:  # If started on Raspberry Pi
    display_flags = pygame.FULLSCREEN  # Turn on video acceleration
    SCREEN = pygame.display.set_mode(DISPLAY_SIZE, display_flags)
    pygame.mouse.set_visible(False)                                 # Hide mouse cursor
else:
    SCREEN = pygame.display.set_mode(DISPLAY_SIZE)

#: The directory where resources like button icons or the font file is stored.
RESOURCES = os.path.dirname(__file__) + '/resources/'

#: Standard font type
FONT = pygame.font.Font(RESOURCES + 'DroidSans.ttf', 26)

""" Color definitions """
BLUE = 0, 148, 255
CREAM = 206, 206, 206
BLACK = 0, 0, 0
WHITE = 255, 255, 255
YELLOW = 255, 255, 0
RED = 255, 0, 0
GREEN = 0, 255, 0

""" Mouse related variables """
GESTURE_MOVE_MIN = 50  # Minimum movement in pixels to call it a move
GESTURE_CLICK_MAX = 15  # Maximum movement in pixels to call it a click
GESTURE_PRESS_MIN = 500  # Minimum time to call a click a long press
# Gesture enumeration
GESTURE_NONE = -1
GESTURE_CLICK = 0
GESTURE_SWIPE_LEFT = 1
GESTURE_SWIPE_RIGHT = 2
GESTURE_SWIPE_UP = 3
GESTURE_SWIPE_DOWN = 4
GESTURE_LONG_PRESS = 5
GESTURE_DRAG_VERTICAL = 6
GESTURE_DRAG_HORIZONTAL = 7

""" Used icons """
# Switch icons
ICO_SWITCH_ON = RESOURCES + 'switch_on_48x32.png'
ICO_SWITCH_OFF = RESOURCES + 'switch_off_48x32.png'
ICO_MODAL_CANCEL = RESOURCES + 'back_22x18.png'

# Player icons
PIC_PLAY = RESOURCES + 'play.png'
ICO_MENU = RESOURCES + 'menu_80x50.png'
ICO_PLAY = RESOURCES + 'play_48x32.png'
ICO_PAUSE = RESOURCES + 'pause_48x32.png'
ICO_STOP = RESOURCES + 'stop_48x32.png'
ICO_NEXT = RESOURCES + 'next_48x32.png'
ICO_PREVIOUS = RESOURCES + 'prev_48x32.png'
ICO_VOLUME = RESOURCES + 'vol_48x32.png'
ICO_VOLUME_UP = RESOURCES + 'vol_up_48x32.png'
ICO_VOLUME_DOWN = RESOURCES + 'vol_down_48x32.png'
ICO_VOLUME_MUTE = RESOURCES + 'vol_mute_48x32.png'
ICO_VOLUME_MUTE_ACTIVE = RESOURCES + 'vol_mute_active_48x32.png'
