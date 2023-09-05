import asyncio
import sys
from tqdm import tqdm

from capture_audio import *
from mpd_client import *


async def main():
    audio_spectrometer = AudioSpectrometer()
    task_connect = asyncio.create_task(mpd.connect())
    is_connected = await task_connect
    if not is_connected:
        print("Couldn't connect to the mpd server " + mpd.host + " on port " + str(
            mpd.port) + "! Check settings in file pi-jukebox.conf or check is server is running 'systemctl status mpd'.")
        sys.exit()

    pbar = tqdm(total=100, desc="Song progress: ")
    abar = tqdm(total=1000, desc="Amplitude: ")
    while True:
        task_get_status = asyncio.create_task(mpd.status_get())
        if await task_get_status:
            print(mpd.now_playing.title)
        try:
            event = mpd.events.popleft()
            playing = mpd.now_playing
            if event == 'time_elapsed':
                #pbar.update(playing.time_percentage)
                print("Time elapsed: " + str(playing.time_percentage))
            if event == 'playing_file':
                print('Title: ' + mpd.now_playing.title)
                print('Artist: ' + mpd.now_playing.artist)
            if event == 'album_change':
                file_img_cover = await mpd.now_playing.get_cover_art()
                print('Cover file: ' + file_img_cover)
        except IndexError:
            pass
        amplitude = round(audio_spectrometer.listen())
        # abar.update(amplitude)
        print("Amplitude: " + str(amplitude))


if __name__ == "__main__":
    asyncio.run(main())