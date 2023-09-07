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
import asyncio
import sys
from PIL import Image, ImageFilter, ImageEnhance

from settings import *
from mpd_client import *
from capture_audio import *
from gui_screens import *

logging.info("ScreenPlaying definition")


class ScreenPlayer(Screen):
    """ Screen cover art
    """
    def __init__(self, screen_surface):
        Screen.__init__(self, screen_surface)
        self.timer = pygame.time.get_ticks
        self.blank_screen_time = self.timer() + BLANK_PERIOD
        self.is_blank_screen = False
        self.file_img_cover = 'default_cover_art.png'
        self.coverart_color = 0
        self.amplitude = 0
        self.audio_spectrometer = AudioSpectrometer(block_time=INPUT_BLOCK_TIME,
                                                    sound_rate=INPUT_SOUND_RATE)
        self.add_component(Picture(name='pic_background', surface=self.surface,
                                   surface_pos=(0, 0), widget_dims =(SCREEN_WIDTH, SCREEN_HEIGHT), image_file='background.png'))
        picture_pos = (((SCREEN_WIDTH/2)-(SCREEN_HEIGHT/2) + 15), 25)
        self.add_component(Picture(name='pic_cover_art', surface=self.surface,
                                   surface_pos=picture_pos, widget_dims =(SCREEN_HEIGHT - 40, SCREEN_HEIGHT - 40),
                                   image_file=self.file_img_cover))
        self.add_component(LabelText(name='lbl_track_title', surface=self.surface,
                                     surface_pos=(0, 0), widget_dims=(SCREEN_WIDTH, 38), alignment=(HOR_LEFT, VERT_BOTTOM)))
        self.components['lbl_track_title'].background_alpha_set(180)
        self.add_component(Slider2(name='slide_time', surface=self.surface,
                                   surface_pos=(0, SCREEN_HEIGHT - 10), widget_dims=(SCREEN_WIDTH, 10)))
        self.add_component(LabelText(name='lbl_track_artist', surface=self.surface,
                                     surface_pos=(0, SCREEN_HEIGHT - 42), widget_dims=(SCREEN_WIDTH, 32), alignment=(HOR_RIGHT, VERT_TOP)))
        self.components['lbl_track_artist'].background_alpha_set(180)

    async def create_background(self):
        image = Image.open(self.file_img_cover)
        image = image.resize((SCREEN_WIDTH, SCREEN_WIDTH))
        image = image.crop((0, (SCREEN_WIDTH - SCREEN_HEIGHT)/2, SCREEN_WIDTH, SCREEN_WIDTH - (SCREEN_WIDTH - SCREEN_HEIGHT)/2))
        image = image.filter(ImageFilter.GaussianBlur(8))
        image = ImageEnhance.Brightness(image).enhance(0.6)
        image.save('background.png')

    async def show(self):
        """ Displays the screen. """
        self.file_img_cover = await mpd.now_playing.get_cover_art()
        self.components['pic_cover_art'].picture_set(self.file_img_cover)
        await self.create_background()
        self.components['pic_background'].picture_set('background.png')
        self.components['lbl_track_title'].text_set('    ' + mpd.now_playing.title + '    ')
        self.components['lbl_track_title'].adjust_to_caption_size()
        self.components['lbl_track_artist'].text_set('    ' + mpd.now_playing.artist + '    ')
        self.components['lbl_track_artist'].adjust_to_caption_size()
        self.apply_color_theme()
        return await super(ScreenPlayer, self).show()

    async def update(self):
        task_mpd = asyncio.create_task(self.hook_event())
        await task_mpd
        try:
            event = mpd.events.popleft()
            playing = mpd.now_playing
            if event == 'time_elapsed':
                self.components['slide_time'].progress_percentage_set(playing.time_percentage)
            if event == 'playing_file':
                self.components['lbl_track_title'].text_set('    ' + mpd.now_playing.title + '    ')
                self.components['lbl_track_title'].adjust_to_caption_size()
                self.components['lbl_track_artist'].text_set('    ' + mpd.now_playing.artist + '    ')
                self.components['lbl_track_artist'].adjust_to_caption_size()
            if event == 'album_change':
                self.file_img_cover = mpd.now_playing.get_cover_art()
                await self.create_background()
                self.components['pic_cover_art'].picture_set(self.file_img_cover)
                self.components['pic_background'].picture_set('background.png')
                self.apply_color_theme()
            if event == 'album_change' or event == 'playing_file':
                task_show = asyncio.create_task(super(ScreenPlayer, self).show())
                await task_show
        except IndexError:
            pass
        self.amplitude = self.audio_spectrometer.listen()
        self.update_spectrometer()
        self.redraw()

    def update_spectrometer(self):
        change_factor = round(self.amplitude / 400)
        x_size = 800 + change_factor
        y_size = 480 # + change_factor
        x_pos = round((change_factor) / 2)
        y_pos = 0
        self.components['pic_background'].position_size_set(x=x_pos, y=y_pos, width=x_size, height=y_size)

    async def draw_cover_art(self):
        left_position = 40
        hor_length = SCREEN_WIDTH - 40
        top_position = 0
        vert_length = SCREEN_HEIGHT  # - 5
        if hor_length > vert_length:
            cover_size = vert_length
        else:
            cover_size = hor_length
        self.file_img_cover = await mpd.now_playing.get_cover_art()
        self.add_component(Picture(name='pic_cover_art', surface=self.layer_foreground,
                                   surface_pos=(left_position, top_position), widget_dims=(cover_size, cover_size), image_file=self.file_img_cover))

    def apply_color_theme(self):
        self.coverart_color = self.components['pic_cover_art'].color_main()
        self.color = self.coverart_color[0]
        self.components['slide_time'].bottom_color = self.coverart_color[0]
        color_complimentary = np.subtract((255, 255, 255), self.color)
        luminance = (color_complimentary[0] * 0.2989 + color_complimentary[1] * 0.5870 + color_complimentary[2] * 0.1140) / 255
        if luminance < .5:
            color_font = (0, 0, 0)
        else:
            color_font = (255, 255, 255)
        self.components['slide_time'].background_alpha = 130
        self.components['slide_time'].progress_color = color_complimentary
        self.components['lbl_track_title'].font_color = color_font
        self.components['lbl_track_title'].background_color = self.color
        self.components['lbl_track_artist'].font_color = color_font
        self.components['lbl_track_artist'].background_color = self.color

    async def hook_event(self):
        await mpd.status_get()
        task_control = asyncio.create_task(mpd.player_control_get())
        mpd_control_status = await task_control
        is_playing = mpd_control_status != 'pause' and mpd_control_status != 'stop'
        if is_playing:
            self.blank_screen_time = self.timer() + BLANK_PERIOD
            if self.is_blank_screen:
                task_show = asyncio.create_task(self.show())
                await task_show
            else:
                self.redraw()
        elif not is_playing and self.timer() > self.blank_screen_time: #and self.current_index != 1:
            self.is_blank_screen = True
            self.surface.fill((0,0,0))
            pygame.display.flip()
            while not is_playing:
                pygame.event.get()
                await mpd.status_get()
                mpd_control_status = await mpd.player_control_get()
                is_playing = mpd_control_status != 'pause' and mpd_control_status != 'stop'
            self.blank_screen_time = self.timer() + BLANK_PERIOD
            task_show = asyncio.create_task(self.show())
            await task_show
