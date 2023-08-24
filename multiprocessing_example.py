import multiprocessing
from ctypes import c_wchar_p
from mpd_client import *
import sys


def get_mpd_status(lock, variable):
    if lock.acquire(False):
        print("I am in!")
        mpd_status = mpd.status_get()
        control_status = mpd.player_control_get()
        is_playing = control_status != 'pause' and control_status != 'stop'
        variable.value = control_status
        if is_playing:
            print("Playing")
        elif not is_playing:
            print("Not playing")
        lock.release()
        print("Gone out")

if __name__ == "__main__":
    lock = multiprocessing.Lock()
    mpd_status =  multiprocessing.Value(c_wchar_p, "None")
    if not mpd.connect():
        print("Couldn't connect to the mpd server " + mpd.host + " on port " + str(
            mpd.port) + "! Check settings in file pi-jukebox.conf or check is server is running 'systemctl status mpd'.")
        sys.exit()
    i = 0

    while True:
        # start the process
        process = multiprocessing.Process(target=get_mpd_status, args=(lock, mpd_status, ))
        process.start()
        print('Main - Round: ' + str(i) + ' - ' + mpd_status.value )
        i = i + 1
