
import asyncio
import sys

from settings import *
from mpd_client import *
from screen_player import *


async def main():
    if not mpd.connect():
        print("Couldn't connect to the mpd server " + mpd.host + " on port " + str(
            mpd.port) + "! Check settings in file pi-jukebox.conf or check is server is running 'systemctl status mpd'.")
        sys.exit()
    pygame.init()
    screen = pygame.display.set_mode([800, 480])
    screen_player = ScreenPlayer(screen)
    await screen_player.show()


if __name__ == "__main__":
    asyncio.run(main())
