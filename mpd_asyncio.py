import asyncio
import sys

from mpd_client import *


async def main():
    if not mpd.connect():
        print("Couldn't connect to the mpd server " + mpd.host + " on port " + str(
            mpd.port) + "! Check settings in file pi-jukebox.conf or check is server is running 'systemctl status mpd'.")
        sys.exit()

    task_get_status = asyncio.create_task(mpd.status_get())
    if await task_get_status:
        print("Got it!")
    else:
        print("Not there")


if __name__ == "__main__":
    asyncio.run(main())