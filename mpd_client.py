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
==================================================================
**mpd_client.py**: controlling and monitoring mpd via python-mpd2.
==================================================================
"""

import sys, pygame
import os
import mpd
import subprocess
from collections import deque
from mutagen import File

MPD_TYPE_ARTIST = 'artist'
MPD_TYPE_ALBUM = 'album'
MPD_TYPE_SONGS = 'title'

DEFAULT_COVER = 'default_cover_art.png'
TEMP_PLAYLIST_NAME = '_pi-jukebox_temp'

# reload(sys)
# sys.setdefaultencoding('utf8')


class MPDNowPlaying(object):
    """ Song information
    """
    def __init__(self, mpd_client=None):
        self.__mpd_client = mpd_client
        self.playing_type = ''
        self.__now_playing = None
        self.title = ""  # Currently playing song name
        self.artist = ""  # Currently playing artist
        self.album = ""  # Album the currently playing song is on
        self.file = ""  # File with path relative to MPD music directory
        self.art = None
        self.__time_current_sec = 0  # Currently playing song time (seconds)
        self.time_current = ""  # Currently playing song time (string format)
        self.__time_total_sec = 0  # Currently playing song duration (seconds)
        self.time_total = ""  # Currently playing song duration (string format)
        self.time_percentage = 0    # Currently playing song time as a percentage of the song duration
        self.music_directory = ""

    def now_playing_set(self, now_playing=None):
        if now_playing is not None:
            try:
                self.file = now_playing['file']
            except KeyError:
                return False
            if self.file[:7] == "http://":
                self.playing_type = 'radio'
            else:
                self.playing_type = 'file'

            if 'title' in now_playing:
                self.title = now_playing['title']  # Song title of current song
            else:
                self.title = os.path.splitext(os.path.basename(now_playing['file']))[0]
            if self.playing_type == 'file':
                if 'artist' in now_playing:
                    self.artist = now_playing['artist']  # Artist of current song
                else:
                    self.artist = "Unknown"
                if 'album' in now_playing:
                    self.album = now_playing['album']  # Album the current song is on
                else:
                    self.album = "Unknown"
                current_total = self.str_to_float(now_playing['time'])
                self.__time_total_sec = current_total
                self.time_total = self.make_time_string(current_total)  # Total time current
            elif self.playing_type == 'radio':
                if 'name' in now_playing:
                    self.album = now_playing['name']  # The radio station name
                else:
                    self.album = "Unknown"
                self.artist = ""
        elif now_playing is None:  # Changed to no current song
            self.__now_playing = None
            self.title = ""
            self.artist = ""
            self.album = ""
            self.file = ""
            self.time_percentage = 0
            self.__time_total_sec = 0
            self.time_total = self.make_time_string(0)  # Total time current

    def current_time_set(self, seconds):
        if self.__time_current_sec != seconds:  # Playing time current
            self.__time_current_sec = seconds
            self.time_current = self.make_time_string(seconds)
            if self.playing_type != 'radio':
                self.time_percentage = int(self.__time_current_sec / self.__time_total_sec * 100)
            else:
                self.time_percentage = 0
            return True
        else:
            return False

    def cover_art_get(self, dest_file_name="covert_art.jpg"):
        if self.file == "" or self.playing_type == 'radio':
            return DEFAULT_COVER
        try:
            music_file = File(self.music_directory + "/" + self.file)
        except IOError:
            return DEFAULT_COVER
        cover_art = None
        if 'covr' in music_file:
            cover_art = music_file.tags['covr'].data
        elif 'APIC:' in music_file:
            cover_art = music_file.tags['APIC:'].data
        else:
            return DEFAULT_COVER

        with open(dest_file_name, 'wb') as img:
            img.write(cover_art)  # write artwork to new image
        return dest_file_name

    def make_time_string(self, seconds):
        minutes = int(seconds / 60)
        seconds_left = int(round(seconds - (minutes * 60), 0))
        time_string = str(minutes) + ':'
        seconds_string = ''
        if seconds_left < 10:
            seconds_string = '0' + str(seconds_left)
        else:
            seconds_string = str(seconds_left)
        time_string += seconds_string
        return time_string

    def str_to_float(self, s):
        try:
            return float(s)
        except ValueError:
            return float(0)


class MPDController(object):
    """ Controls playback and volume
    """

    def __init__(self):
        self.mpd_client = mpd.MPDClient()
        self.host = '192.168.178.25'
        self.port = 6600
        self.update_interval = 1000  # Interval between mpc status update calls (milliseconds)
        self.volume = 0  # Playback volume
        self.playlist_current = []  # Current playlist song title
        self.__radio_mode = False
        self.now_playing = MPDNowPlaying()
        self.events = deque([])  # Queue of mpd events

        self.__now_playing = None  # Dictionary containing currently playing song info
        self.__now_playing_changed = False
        self.__player_control = ''  # Indicates whether mpd is playing, pausing or has stopped playing music
        self.__muted = False  # Indicates whether muted
        self.__last_update_time = 0   # For checking last update time (milliseconds)
        self.__status = None  # mpc's current status output

    def connect(self):
        """ Connects to mpd server.

            :return: Boolean indicating if successfully connected to mpd server.
        """
        try:
            self.mpd_client.connect(self.host, self.port)
            self.__music_directory = self.mpd_client.listmounts()
        except Exception:
            return False

        now_playing = MPDNowPlaying()
        now_playing.now_playing_set(self.mpd_client.currentsong())
        #self.__starts_with_radio()
        #lst_mounts = self.mpd_client.listmounts()
        #self.__music_directory = subprocess.check_output(['mpc', 'mount']).strip()

        # See if currently playing is radio station
        return True

    def __starts_with_radio(self):
        was_playing = False  # Indicates whether mpd was playing on start
        now_playing = MPDNowPlaying()
        try:
            now_playing.now_playing_set(self.mpd_client.currentsong())  # Get currently playing info
        except mpd.ConnectionError:
            self.mpd_client.connect(self.host, self.port)
            now_playing.now_playing_set(self.mpd_client.currentsong())
        if self.player_control_get() == 'play':
            was_playing = True
        if now_playing.playing_type == 'radio':
            station_url = now_playing.file  # If now playing is radio station temporarily store
            try:
                self.__radio_mode = False
            except Exception:
                pass
            self.__radio_mode = True  # Turn on radio mode
            self.mpd_client.addid(station_url)  # Reload station
            if was_playing:
                self.mpd_client.play(0)  # Resume playing

    def disconnect(self):
        """ Closes the connection to the mpd server. """
        self.mpd_client.close()
        self.mpd_client.disconnect()

    def music_directory_set(self, path):
        self.now_playing.music_directory = path
        self.__music_directory = path

    def __parse_mpc_status(self):
        """ Parses the mpd status and fills mpd event queue

            :return: Boolean indicating if the status was changed
        """
        current_seconds = 0
        current_total = 0
        try:
            now_playing = self.mpd_client.currentsong()
        except Exception:
            return False

        if self.__now_playing != now_playing and len(now_playing) > 0:  # Changed to a new song
            self.now_playing.now_playing_set(now_playing)
            if self.now_playing.playing_type == 'radio':
                self.__radio_mode = True
            else:
                self.__radio_mode = False
            self.__now_playing_changed = True
            if self.__now_playing is None or self.__now_playing.track_file != now_playing.track_file:
                self.events.append('playing_file')
            self.events.append('playing_time_percentage')

        try:
            status = self.mpd_client.status()
        except Exception:
            return False
        if self.__status == status:
            return False
        self.__status = status
        if self.__player_control != status['state']:
            self.__player_control = status['state']
            self.events.append('player_control')

        if self.__player_control != 'stop':
            if self.__playlist_current_playing_index != int(status['song']):  # Current playlist index
                self.__playlist_current_playing_index = int(status['song'])
                self.events.append('playing_index')
            if self.now_playing.current_time_set(self.str_to_float(status['elapsed'])):
                self.events.append('time_elapsed')
        else:
            if self.__playlist_current_playing_index != -1:
                self.__playlist_current_playing_index = -1
                self.events.append('playing_index')
                if self.now_playing.current_time_set(0):
                    self.events.append('time_elapsed')

        return True

    def str_to_float(self, s):
        try:
            return float(s)
        except ValueError:
            return float(0)

    def status_get(self):
        """ Updates mpc data, returns True when status data is updated. Wait at
            least 'update_interval' milliseconds before updating mpc status data.

            :return: Returns boolean whether updated or not.
        """
        self.mpd_client.ping()
        time_elapsed = pygame.time.get_ticks() - self.__last_update_time
        if pygame.time.get_ticks() > self.update_interval and time_elapsed < self.update_interval:
            return False
        self.__last_update_time = pygame.time.get_ticks() # Reset update
        return self.__parse_mpc_status()   # Parse mpc status output

    def current_song_changed(self):
        if self.__now_playing_changed:
            self.__now_playing_changed = False
            return True
        else:
            return False

    def get_cover_art(self, dest_file_name="covert_art.jpg"):
        return self.now_playing.cover_art_get()

    def player_control_set(self, play_status):
        """ Controls playback

            :param play_status: Playback action ['play', 'pause', 'stop', 'next', 'previous'].
        """
        if play_status == 'play':
            if self.__player_control == 'pause':
                self.mpd_client.play()
            else:
                self.mpd_client.pause(0)
        elif play_status == 'pause':
            self.mpd_client.pause(1)
        elif play_status == 'stop':
            self.mpd_client.stop()
        elif play_status == 'next':
            self.mpd_client.next()
        elif play_status == 'previous':
            self.mpd_client.previous()

    def player_control_get(self):
        """ :return: Current playback mode. """
        self.status_get()
        return self.__player_control

    def radio_mode_get(self):
        return self.__radio_mode


mpd = MPDController()
