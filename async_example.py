import asyncio
from mpd_client import *
from capture_audio import *
import sys

getting_mpd_status = False

async def get_mpd_status():
    getting_mpd_status = True
    mpd_status = mpd.status_get()
    control_status = mpd.player_control_get()
    getting_mpd_status = False
    return control_status

async def get_amplitude(audio):
    amplitude = audio.listen()
    return amplitude

async def main():
    if not mpd.connect():
        print("Couldn't connect to the mpd server " + mpd.host + " on port " + str(
            mpd.port) + "! Check settings in file pi-jukebox.conf or check is server is running 'systemctl status mpd'.")
        sys.exit()

    audio = AudioSpectrometer(idx_input_device=6)

    i = 0
    while True:
        # start the process
        amplitude_task = asyncio.create_task(get_amplitude(audio=audio))
        if not getting_mpd_status:
            mpd_task = asyncio.create_task(get_mpd_status())
        amplitude = await amplitude_task
        mpd_status = await mpd_task
        try:
            event = mpd.events.popleft()
        except IndexError:
            pass
        playing = mpd.now_playing
        print('Main - Round: ' + str(i))
        if event == 'time_elapsed':
            print(' - MPD elapsed: ' + str(playing.time_percentage))
        print(' - Amplitude: ' + str(amplitude))
        i = i + 1

if __name__ == "__main__":
    asyncio.run(main=main())
