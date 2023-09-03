import asyncio
import sys
from PIL import Image, ImageFilter, ImageEnhance

from settings import *
from mpd_client import *
from capture_audio import *
from gui_screens import *


class ScreenPlayer(Screen):
    """ Screen cover art
    """
    def __init__(self, screen_surface):
        Screen.__init__(self, screen_surface)
        self.timer = pygame.time.get_ticks
        self.blank_screen_time = self.timer() + BLANK_PERIOD
        self.file_img_cover = 'default_cover_art.png'
        self.coverart_color = 0
        self.amplitude = 0
        self.audio_spectrometer = AudioSpectrometer(block_time=INPUT_BLOCK_TIME,
                                                    sound_rate=INPUT_SOUND_RATE)
        self.create_background()
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

    def create_background(self):
        image = Image.open(self.file_img_cover)
        image = image.resize((SCREEN_WIDTH, SCREEN_WIDTH))
        image = image.crop((0, (SCREEN_WIDTH - SCREEN_HEIGHT)/2, SCREEN_WIDTH, SCREEN_WIDTH - (SCREEN_WIDTH - SCREEN_HEIGHT)/2))
        image = image.filter(ImageFilter.GaussianBlur(8))
        image = ImageEnhance.Brightness(image).enhance(0.6)
        image.save('background.png')

    def show(self):
        """ Displays the screen. """
        self.file_img_cover = mpd.now_playing.get_cover_art()
        self.components['pic_cover_art'].picture_set(self.file_img_cover)
        self.create_background()
        self.components['lbl_track_title'].text_set('    ' + mpd.now_playing.title + '    ')
        self.components['lbl_track_title'].adjust_to_caption_size()
        self.components['lbl_track_artist'].text_set('    ' + mpd.now_playing.artist + '    ')
        self.components['lbl_track_artist'].adjust_to_caption_size()
        self.apply_color_theme()
        return super(ScreenPlayer, self).show()

    async def update(self):
        task_mpd = asyncio.create_task(self.update_mpd())
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
                self.create_background()
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

    def draw_cover_art(self):
        left_position = 40
        hor_length = SCREEN_WIDTH - 40
        top_position = 0
        vert_length = SCREEN_HEIGHT  # - 5
        if hor_length > vert_length:
            cover_size = vert_length
        else:
            cover_size = hor_length
        self.file_img_cover = mpd.now_playing.get_cover_art()
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

    # async def hook_event(self):
    #     try:
    #         mpd.status_get()
    #         mpd_control_status = mpd.player_control_get()
    #         is_playing = mpd_control_status != 'pause' and mpd_control_status != 'stop'
    #         if is_playing:
    #             self.blank_screen_time = self.timer() + BLANK_PERIOD
    #             self.show()
    #         elif not is_playing and self.timer() > self.blank_screen_time: #and self.current_index != 1:
    #             self.surface.fill((0,0,0))
    #             pygame.display.flip()
    #             while not is_playing:
    #                 pygame.event.get()
    #                 mpd.status_get()
    #                 mpd_control_status = mpd.player_control_get()
    #                 is_playing = mpd_control_status != 'pause' and mpd_control_status != 'stop'
    #             self.blank_screen_time = self.timer() + BLANK_PERIOD
    #             self.show()
    #     except:
    #         pass

    async def update_mpd(self):
        mpd.status_get()
        mpd_control_status = mpd.player_control_get()
        is_playing = mpd_control_status != 'pause' and mpd_control_status != 'stop'
        if is_playing:
            self.blank_screen_time = self.timer() + BLANK_PERIOD
            task_show = asyncio.create_task(self.show())
            await task_show
        elif not is_playing and self.timer() > self.blank_screen_time: #and self.current_index != 1:
            self.surface.fill((0,0,0))
            pygame.display.flip()
            while not is_playing:
                pygame.event.get()
                mpd.status_get()
                mpd_control_status = mpd.player_control_get()
                is_playing = mpd_control_status != 'pause' and mpd_control_status != 'stop'
            self.blank_screen_time = self.timer() + BLANK_PERIOD
            task_show = asyncio.create_task(self.show())
            await task_show


def main():
    if not mpd.connect():
        print("Couldn't connect to the mpd server " + mpd.host + " on port " + str(
            mpd.port) + "! Check settings in file pi-jukebox.conf or check is server is running 'systemctl status mpd'.")
        sys.exit()
    pygame.init()
    screen = pygame.display.set_mode([800, 480])
    screen_player = ScreenPlayer(screen)
    asyncio.run(screen_player.show())

if __name__ == "__main__":
    main()
