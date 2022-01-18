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
=======================================================
**screen_player.py**: Playback screen.
=======================================================
"""

import sys, pygame
from pygame.locals import *
import time
import subprocess
import os
import glob
from gui_widgets import *
from gui_screens import *
from mpd_client import *
from settings import *


class ScreenPlaying(Screen):
    """ Screen cover art

        :param screen_rect: The display's rectangle where the screen is drawn on.
    """

    def __init__(self, screen_surface):
        Screen.__init__(self, screen_surface)
        # Cover art
        self.draw_cover_art()
        # Player specific labels
        self.add_component(LabelText('lbl_track_artist', self.surface, 0, 0, SCREEN_WIDTH, 18))
        self.components['lbl_track_artist'].set_alignment(HOR_LEFT, VERT_MID)
        self.components['lbl_track_artist'].background_alpha_set(160)
        self.add_component(LabelText('lbl_track_title', self.surface, 0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 18))
        self.components['lbl_track_title'].set_alignment(HOR_LEFT, VERT_MID)
        self.components['lbl_track_title'].background_alpha_set(160)
        self.add_component(Slider2('slide_time', self.surface, 0, SCREEN_HEIGHT - 3, SCREEN_WIDTH, 3))

    def show(self):
        """ Displays the screen. """
        self.components['pic_cover_art'].picture_set('test.img')
        self.components['lbl_track_title'].text_set(mpd.now_playing.title)
        self.components['lbl_track_artist'].text_set(mpd.now_playing.artist)
        self.components['lbl_track_artist'].visible = True
        return super(ScreenPlaying, self).show()  # Draw screen

    def update(self):
        while True:
            try:
                event = mpd.events.popleft()
                playing = mpd.now_playing
                print(event)
                if event == 'time_elapsed':
                    self.components['slide_time'].draw(playing.time_percentage)
                if event == 'playing_file':
                    img_cover = mpd.now_playing.get_cover_art()
                    with open('test.img', 'wb') as img:
                        img.write(img_cover)
                    self.components['pic_cover_art'].picture_set('test.img')
                    self.components['lbl_track_artist'].text_set(playing.artist)
                    self.components['lbl_track_title'].text_set(playing.title)
            except IndexError:
                break

    def on_click(self, x, y):
        tag_name = super(ScreenPlaying, self).on_click(x, y)
        plyr_status = mpd.player_control_get()
        if tag_name == 'pic_cover_art':
            if mpd.player_control_get() == 'play':
                mpd.player_control_set('pause')
                self.components['lbl_track_artist'].visible = True
            else:
                mpd.player_control_set('play')
                self.components['lbl_track_artist'].visible = False
        plyr_status = mpd.player_control_get()
        return 0

    def draw_cover_art(self):
        left_position = 40
        hor_length = SCREEN_WIDTH - 40
        top_position = 0
        vert_length = SCREEN_HEIGHT  # - 5
        if hor_length > vert_length:
            cover_size = vert_length
        else:
            cover_size = hor_length

        img_cover = mpd.now_playing.get_cover_art()
        with open('test.img', 'wb') as img:
            img.write(img_cover)  # write artwork to new image
        self.add_component(Picture('pic_cover_art',
                                   self.surface, left_position, top_position, cover_size, cover_size,
                                   'test.img'))


class ScreenVolume(ScreenModal):
    """ Screen setting volume

        :param screen_rect: The display's rectangle where the screen is drawn on.
    """

    def __init__(self, screen):
        ScreenModal.__init__(self, screen, "Volume")
        self.window_x = 15
        self.window_y = 52
        self.window_width -= 2 * self.window_x
        self.window_height -= 2 * self.window_y
        self.outline_shown = True
        self.title_color = FIFTIES_GREEN
        self.outline_color = FIFTIES_GREEN

        self.add_component(ButtonIcon('btn_mute', self.surface, ICO_VOLUME_MUTE, self.window_x + 5, self.window_y + 25))
        self.components['btn_mute'].x_pos = self.window_x + self.window_width / 2 - self.components[
            'btn_mute'].width / 2
        self.add_component(
            ButtonIcon('btn_volume_down', self.surface, ICO_VOLUME_DOWN, self.window_x + 5, self.window_y + 25))
        self.add_component(
            ButtonIcon('btn_volume_up', self.surface, ICO_VOLUME_UP, self.window_width - 40, self.window_y + 25))
        self.add_component(
            Slider('slide_volume', self.surface, self.window_x + 8, self.window_y + 63, self.window_width - 18, 30))
        self.components['slide_volume'].progress_percentage_set(mpd.volume)
        self.add_component(
            ButtonText('btn_back', self.surface, self.window_x + self.window_width / 2 - 23, self.window_y + 98, 46, 32,
                       "Back"))
        self.components['btn_back'].button_color = FIFTIES_TEAL

    def on_click(self, x, y):
        tag_name = super(ScreenModal, self).on_click(x, y)
        if tag_name == 'btn_mute':
            mpd.volume_mute_switch()
            self.components['slide_volume'].progress_percentage_set(mpd.volume)
        elif tag_name == 'btn_volume_down':
            mpd.volume_set_relative(-10)
            self.components['slide_volume'].progress_percentage_set(mpd.volume)
        elif tag_name == 'btn_volume_up':
            mpd.volume_set_relative(10)
            self.components['slide_volume'].progress_percentage_set(mpd.volume)
        elif tag_name == 'slide_volume':
            mpd.volume_set(self.components['slide_volume'].progress_percentage)
        elif tag_name == 'btn_back':
            self.close()
        if mpd.volume == 0 or mpd.volume_mute_get():
            self.components['btn_mute'].set_image_file(ICO_VOLUME_MUTE_ACTIVE)
        else:
            self.components['btn_mute'].set_image_file(ICO_VOLUME_MUTE)
        self.components['btn_mute'].draw()
