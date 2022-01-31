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
**screen_blank.py**: Blank screen.
=======================================================
"""
from gui_screens import *
logging.info("ScreenBlank definition")

class ScreenBlank(Screen):
    """ Screen for blanking
    """

    def __init__(self, screen_surface):
        Screen.__init__(self, screen_surface)

    def show(self):
        return super(ScreenBlank, self).show()  # Draw screen
