from multiprocessing import Value
from multiprocessing import Process
from ctypes import c_wchar_p
from mpd_client import *


def get_mpd_status(status):
    mpd_status = mpd.status_get()
    mpd_control_status = mpd.player_control_get()
    is_playing = mpd_control_status != 'pause' and mpd_control_status != 'stop'
    if is_playing:
        print("Playing")
    elif not is_playing:
        print("Not playing")
    status.value = mpd_status

if __name__ == "__main__":
    mpd_status = Value(c_wchar_p, 'stop')

    while True:
        process = Process(target=get_mpd_status, args=(mpd_status,))
        # start the process
        process.start()
        print(mpd_status.value)
        print('test')
