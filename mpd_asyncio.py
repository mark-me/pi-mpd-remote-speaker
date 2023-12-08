import asyncio
import sys
import curses
from curses import wrapper

from capture_audio import *
from mpd_client import *


async def main_screen(stdscr):
    audio_spectrometer = AudioSpectrometer()
    task_connect = asyncio.create_task(mpd.connect())
    is_connected = await task_connect
    if not is_connected:
        print("Couldn't connect to the mpd server " + mpd.host + " on port " + str(
            mpd.port) + "! Check settings in file pi-jukebox.conf or check is server is running 'systemctl status mpd'.")
        sys.exit()

    stdscr.clear()    
    while True:
        stdscr.clear()
        task_get_status = asyncio.create_task(mpd.status_get())
        if await task_get_status:
            stdscr.addstr(10, 10, mpd.now_playing.title)
        try:
            event = mpd.events.popleft()
            playing = mpd.now_playing
            if event == 'time_elapsed':
                stdscr.addstr(12, 10, "Time elapsed: " + str(playing.time_percentage))
            if event == 'playing_file':
                stdscr.addstr(14, 10, 'Title: ' + mpd.now_playing.title)
                stdscr.addstr(15, 10, 'Artist: ' + mpd.now_playing.artist)
            if event == 'album_change':
                file_img_cover = await mpd.now_playing.get_cover_art()
                stdscr.addstr(16, 10, 'Cover file: ' + file_img_cover)
        except IndexError:
            pass
        amplitude = round(audio_spectrometer.listen())

        stdscr.addstr(17, 10, "Amplitude: " + str(amplitude))

def main(stdscr) -> None:
    return asyncio.run(main_screen(stdscr=stdscr))

if __name__ == "__main__":
    wrapper(main)