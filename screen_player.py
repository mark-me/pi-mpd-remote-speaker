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
import pygame

from gui_screens import *
from mpd_client import *
from settings import *
import numpy as np
logging.info("ScreenPlaying definition")


class ScreenPlaying(Screen):
    """ Screen cover art
    """

    def __init__(self, screen_surface):
        Screen.__init__(self, screen_surface)
        # Cover art
        # self.draw_cover_art()
        self.add_component(Picture('pic_cover_art',
                                   self.surface, (SCREEN_WIDTH/2)-(SCREEN_HEIGHT/2), 0, SCREEN_HEIGHT, SCREEN_HEIGHT,
                                   "default_cover_art.png"))
        # Player specific labels
        self.add_component(LabelText('lbl_track_title', self.surface, 0, SCREEN_HEIGHT - 42, SCREEN_WIDTH, 42))
        self.components['lbl_track_title'].set_alignment(HOR_LEFT, VERT_TOP)
        self.components['lbl_track_title'].background_alpha_set(180)
        self.add_component(Slider2('slide_time', self.surface, 0, SCREEN_HEIGHT - 10, SCREEN_WIDTH, 10))
        self.coverart_color = 0

    def show(self):
        """ Displays the screen. """
        self.components['pic_cover_art'].picture_set(mpd.now_playing.get_cover_art())
        self.components['lbl_track_title'].text_set('    ' + mpd.now_playing.artist + ' - ' + mpd.now_playing.title)
        self.apply_color_theme()
        return super(ScreenPlaying, self).show()  # Draw screen

    def update(self):
        while True:
            try:
                event = mpd.events.popleft()
                playing = mpd.now_playing
                logging.info("Update event: %s", event)

                if event == 'time_elapsed':
                    self.components['slide_time'].draw(playing.time_percentage)
                if event == 'playing_file':
                    self.components['lbl_track_title'].text_set('    ' + mpd.now_playing.title + ' - ' + mpd.now_playing.artist)
                if event == 'album_change':
                    file_img_cover = mpd.now_playing.get_cover_art()
                    self.components['pic_cover_art'].picture_set(file_img_cover)
                    self.apply_color_theme()
                if event == 'album_change' or event == 'playing_file':
                    super(ScreenPlaying, self).show()
            except IndexError:
                break

    def on_click(self, x, y):
        tag_name = super(ScreenPlaying, self).on_click(x, y)
        if tag_name == 'pic_cover_art':
            if mpd.player_control_get() == 'play':
                mpd.player_control_set('pause')
            else:
                mpd.player_control_set('play')
        return 0

    def draw_cover_art(self):
        left_position = 40
        hor_length = SCREEN_WIDTH - 40
        top_position = 0
        vert_length = SCREEN_HEIGHT
        if hor_length > vert_length:
            cover_size = vert_length
        else:
            cover_size = hor_length

        file_img_cover = mpd.now_playing.get_cover_art()

        self.add_component(Picture('pic_cover_art',
                                   self.surface, left_position, top_position, cover_size, cover_size,
                                   file_img_cover))

    def apply_color_theme(self):
        self.coverart_color = self.components['pic_cover_art'].color_clusters()
        self.color = self.coverart_color[1]
        self.components['slide_time'].bottom_color = self.color
        color_complimentary = np.subtract((255, 255, 255), self.color)
        luminance = (color_complimentary[0] * 0.2989 + color_complimentary[1] * 0.5870 + color_complimentary[2] * 0.1140) / 255
        if luminance < .5:
            color_font = (0, 0, 0)
        else:
            color_font = (255, 255, 255)

        self.components['slide_time'].background_alpha = 160
        self.components['slide_time'].progress_color = self.coverart_color[1] #color_complimentary
        self.components['lbl_track_title'].font_color = self.coverart_color[1] #color_font
        self.components['lbl_track_title'].background_color = self.color


class ScreenVolume(ScreenModal):
    """ Screen setting volume
    """

    def __init__(self, screen):
        ScreenModal.__init__(self, screen, "Volume")
        self.window_x = 15
        self.window_y = 52
        self.window_width -= 2 * self.window_x
        self.window_height -= 2 * self.window_y
        self.outline_shown = True
        self.title_color = GREEN
        self.outline_color = GREEN

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
        self.components['btn_back'].button_color = CREAM

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
