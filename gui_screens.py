"""
======================================================================
**gui_screens.py**: Building blocks for creating screens and dialogues
======================================================================
"""

__author__ = 'Mark Zwart'
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
import asyncio

from gui_widgets import *
from settings import *

""" Mouse related variables """
GESTURE_MOVE_MIN = 50  # Minimum movement in pixels to call it a move
GESTURE_CLICK_MAX = 15  # Maximum movement in pixels to call it a click
GESTURE_PRESS_MIN = 500  # Minimum time to call a click a long press
# Gesture enumeration
GESTURE_NONE = -1
GESTURE_CLICK = 0
GESTURE_SWIPE_LEFT = 1
GESTURE_SWIPE_RIGHT = 2
GESTURE_SWIPE_UP = 3
GESTURE_SWIPE_DOWN = 4
GESTURE_LONG_PRESS = 5
GESTURE_DRAG_VERTICAL = 6
GESTURE_DRAG_HORIZONTAL = 7

# Standard icons
ICO_INFO = RESOURCES + 'icon_info.png'
ICO_WARNING = RESOURCES + 'icon_warning.png'
ICO_ERROR = RESOURCES + 'icon_warning.png'

#: Time-out period before screen goes blank (milliseconds)
BLANK_PERIOD = 40000 # 300000


class GestureDetector(object):
    """ Class for detecting mouse gestures
    """
    def __init__(self):
        self.gesture = GESTURE_NONE
        self.x_start = 0
        self.y_start = 0
        self.x_moved = 0
        self.y_moved = 0
        self.drag_length = 0
        self.press_duration = 0
        self.x_start, self.y_start = pygame.mouse.get_pos()

    def capture_gesture(self, event):
        """ Mouse event loop, runs from mouse down to mouse up event.

            :param event: pygame event
        """

        if event.type != pygame.MOUSEBUTTONDOWN:
            return GESTURE_NONE

        gesture_ended = False

        self.x_start, self.y_start = pygame.mouse.get_pos()  # Get click position (= start position for swipe)
        pygame.mouse.get_rel()  # Start tracking mouse movement
        mouse_down_time = pygame.time.get_ticks()

        while not gesture_ended:
            for event in pygame.event.get():

                if event.type == pygame.MOUSEBUTTONUP:  # Gesture end
                    self.press_duration = pygame.time.get_ticks() - mouse_down_time
                    self.x_moved, self.y_moved = pygame.mouse.get_rel()  # Movements since start gesture
                    self.gesture = self.__determine_gesture_type()  # Determines the kind of gesture used
                    gesture_ended = True

        return self.gesture

    def __determine_gesture_type(self):
        """ Determines the kind of gesture.

            :return: The type of gesture [:py:const:GESTURE_CLICK, :py:const:GESTURE_SWIPE_DOWN, :py:const:GESTURE_SWIPE_UP, :py:const:GESTURE_SWIPE_LEFT, :py:const:GESTURE_SWIPE_RIGHT]
        """
        x = self.x_moved
        y = self.y_moved
        if self.press_duration < GESTURE_PRESS_MIN:
            if abs(x) <= GESTURE_MOVE_MIN:
                if abs(y) <= GESTURE_MOVE_MIN:
                    if abs(x) < GESTURE_CLICK_MAX and abs(y) < GESTURE_CLICK_MAX:
                        return GESTURE_CLICK  # Tap (click)
                    else:
                        return -1  # No idea what the user did
                elif y > GESTURE_MOVE_MIN:  # Down swipe
                    return GESTURE_SWIPE_DOWN
                elif y < -GESTURE_MOVE_MIN:  # Up swipe
                    return GESTURE_SWIPE_UP
            elif abs(y) <= GESTURE_MOVE_MIN:
                if x > GESTURE_MOVE_MIN:  # Left swipe
                    return GESTURE_SWIPE_LEFT
                elif x < -GESTURE_MOVE_MIN:  # Right swipe
                    return GESTURE_SWIPE_RIGHT
        elif self.press_duration >= GESTURE_PRESS_MIN:
            if abs(x) <= GESTURE_MOVE_MIN:
                if abs(y) <= GESTURE_MOVE_MIN:
                    if abs(x) < GESTURE_CLICK_MAX and abs(y) < GESTURE_CLICK_MAX:
                        return GESTURE_LONG_PRESS  # Long press
                    else:
                        return -1  # No idea what the user did
                elif abs(y) > GESTURE_MOVE_MIN:
                    return GESTURE_DRAG_VERTICAL  # Vertical drag
            elif abs(y) <= GESTURE_MOVE_MIN:
                if abs(x) > GESTURE_MOVE_MIN:
                    return GESTURE_DRAG_HORIZONTAL  # Horizontal drag
        else:
            pass
            return GESTURE_NONE


class ScreenControl(object):
    """ Manages screens of type Screen.
        Handles screen switching, clicking and swiping and mpd status updating.

        :ivar screen_list: List containing all screen objects
        :ivar current_index: Points to current screen in screen_list
    """

    def __init__(self):
        self.screen_list = []
        self.current_index = 0

    def show(self):
        """ Show the current screen """
        while self.current_index >= 0:
            if self.current_index < len(self.screen_list):
                self.current_index = self.screen_list[self.current_index].show()

    def add_screen(self, screen, event_hook_function=None):
        """ Adds screen to list """
        self.screen_list.append(screen)
        added_index = len(self.screen_list) - 1
        if event_hook_function is not None:
            self.screen_list[added_index].hook_event = event_hook_function


class Screen(object):
    """ Basic screen used for displaying widgets. This type of screen should be used for the entire program.

        :param screen_or_surface: The screen's rectangle where the screen is drawn on

        :ivar components: Dictionary holding the screen's widgets with a tag_name as key and the widget as value
        :ivar color: The screen's background color, default = :py:const:BLACK
    """

    def __init__(self, screen_or_surface):
        if isinstance(screen_or_surface, pygame.Surface):
            self.parent_screen = None
            self.surface = screen_or_surface
        elif isinstance(screen_or_surface, Screen):
            self.parent_screen = screen_or_surface
            self.surface = screen_or_surface.surface
            self.hook_event = self.parent_screen.hook_event
        self.loop_active = True
        self.components = {}  # Interface dictionary
        self.color = BLACK
        self.gesture_detect = GestureDetector()

    def add_component(self, widget):
        """ Adds components to component list, thus ensuring a component is found on a mouse event.

            :param widget: The widget that should be added to the dictionary
        """
        self.components[widget.name] = widget

    async def show(self):
        self.loop_active = True
        """ Displays the screen. """
        if self.parent_screen is not None:
            self.parent_screen.active = False
        self.surface.fill(self.color)
        for key, value in self.components.items():
            if value.visible:
                value.draw()
        pygame.display.flip()
        task_loop = asyncio.create_task(self.loop())
        await task_loop

    def redraw(self):
        self.surface.fill(self.color)
        for key, value in self.components.items():
            if value.visible:
                value.draw()
        pygame.display.flip()

    def update(self):
        pass

    def close(self):
        if self.parent_screen is not None:
            self.parent_screen.active = True
            self.parent_screen.hook_event = self.hook_event
        self.loop_active = False

    async def loop(self):
        """ Loops for events """
        while self.loop_active:
            pygame.time.wait(PYGAME_EVENT_DELAY)
            task_update = asyncio.create_task(self.update())
            await task_update
            for event in pygame.event.get():  # Do for all events in pygame's event queue
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()

    def process_mouse_event(self, event):
        """ Processes mouse events. """
        if event.type != pygame.MOUSEBUTTONDOWN and event.type != pygame.MOUSEBUTTONDOWN:
            return None
        gesture = self.gesture_detect.capture_gesture(event)
        x = self.gesture_detect.x_start
        y = self.gesture_detect.y_start

        if gesture == GESTURE_CLICK:  # Fire click function
            return self.on_click(x, y)  # Relay tap/click to active screen
        # Relay vertical swiping to active screen controls
        elif gesture == GESTURE_SWIPE_UP or gesture == GESTURE_SWIPE_DOWN:
            x = self.gesture_detect.x_start
            y = self.gesture_detect.y_start
            self.on_swipe(x, y, gesture)

    async def hook_event(self):
        return False

    def on_click(self, x, y):
        """ Determines which component was clicked and fires its click function in turn

            :param x: The horizontal click position.
            :param y: The vertical click position.

            :return: The tag_name of the clicked component.
        """
        for key, component in self.components.items():
            in_x_range = component.x_pos <= x <= component.x_pos + component.width
            in_y_range = component.y_pos <= y <= component.y_pos + component.height
            if component.visible and in_x_range and in_y_range:
                if isinstance(component, WidgetContainer):
                    return component.on_click(x, y)
                else:
                    component.on_click(x, y)
                    return key

    def on_swipe(self, x, y, swipe_type):
        """ Relays swipe to ItemList components for next(up)/previous(down) swipes for ItemLists.

            :param x: The horizontal start position of the swipe move.
            :param y: The vertical start position of the swipe move.
            :param swipe_type: The type of swipe movement done.
        """
        for key, component in self.components.items():
            if isinstance(component, ItemList):
                in_x_range = component.x_pos <= x <= component.x_pos + component.width
                in_y_range = component.y_pos <= y <= component.y_pos + component.height
                if component.visible and in_x_range and in_y_range:
                    if swipe_type == GESTURE_SWIPE_UP:
                        component.show_next_items()
                    if swipe_type == GESTURE_SWIPE_DOWN:
                        component.show_prev_items()


class ScreenModal(Screen):
    """ Screen with its own event capture loop.
        :param screen_or_surface: The display's rectangle where the screen is drawn on
        :param title: The title displayed at the top of the screen

        :ivar title: The title displayed at the top of the screen
    """

    def __init__(self, screen_or_surface, title):
        Screen.__init__(self, screen_or_surface)
        self.title = title
        self.window_x = 0
        self.window_y = 0
        self.window_width = SCREEN_WIDTH
        self.window_height = SCREEN_HEIGHT
        self.return_object = None
        self.title_color = CREAM
        self.outline_shown = True
        self.outline_color = CREAM

    def show(self):
        self.__draw_window()
        if self.parent_screen is not None:
            self.parent_screen.active = False
        for key, value in self.components.items():
            if value.visible:
                value.draw()
        pygame.display.flip()
        self.loop()
        return self.return_object

    def __draw_window(self):
        """ Draws window border and title. """
        # Draws backdrop screen
        if self.window_width < SCREEN_WIDTH or self.window_height < SCREEN_HEIGHT:
            backdrop = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            backdrop.set_alpha(128)
            backdrop.fill(BLACK)
            SCREEN.blit(backdrop, (0, 0))
        # Drawing window
        window_rect = Rect(self.window_x, self.window_y, self.window_width, self.window_height)
        pygame.draw.rect(self.surface, BLACK, window_rect)
        # Draw outline
        if self.outline_shown:
            pygame.draw.rect(self.surface, self.outline_color, window_rect, 1)
        # Window title bar
        title_rect = Rect(self.window_x, self.window_y, self.window_width, 20)
        pygame.draw.rect(self.surface, self.title_color, title_rect)
        font_height = FONT.size("Tg")[1]
        font_width = FONT.size(self.title)[0]
        image = FONT.render(self.title, True, BLACK)
        self.surface.blit(image, (title_rect.centerx - font_width / 2, title_rect.centery - font_height / 2))
        pygame.display.flip()


class ScreenMessage(ScreenModal):
    """ A screen that displays a message.

        :param screen_or_surface: The display's rectangle where the screen is drawn on
        :param caption: The title displayed at the top of the screen
        :param text: Text displayed in the screen
        :param message_type: Determines the lay-out of the screen [information, warning, error]
    """

    def __init__(self, screen_or_surface, caption, text, message_type=None):
        ScreenModal.__init__(self, screen_or_surface, caption)
        if message_type == 'information':
            self.add_component(
                Picture('pic_icon', self.surface, self.window_x + 5, self.window_y + 30, 48, 48, ICO_INFO))
            self.title_color = GREEN
        elif message_type == 'warning':
            self.add_component(
                Picture('pic_icon', self.surface, self.window_x + 5, self.window_y + 30, 48, 48, ICO_WARNING))
            self.title_color = YELLOW
        elif message_type == 'error':
            self.add_component(
                Picture('pic_icon', self.surface, self.window_x + 5, self.window_y + 30, 48, 48, ICO_ERROR))
            self.title_color = RED
        else:
            self.title_color = BLUE
        x = self.window_x + 55
        y = self.window_y + 30
        width = self.window_width - x - 5
        height = self.window_height - y - 32
        self.add_component(Memo('memo_text', self.surface, x, y, width, height, text))
        self.add_component(ButtonText('btn_ok', self.surface, self.window_x + self.window_width - 60,
                                      self.window_y + self.window_height - 37, 55, 32, "OK"))
        self.components['btn_ok'].button_color = CREAM

    def on_click(self, x, y):
        tag_name = super(ScreenModal, self).on_click(x, y)
        if tag_name == 'btn_ok':
            self.close()


class ScreenYesNo(ScreenModal):
    """ A screen that displays a message.

        :param screen_or_surface: The display's rectangle where the screen is drawn on
        :param caption: The title displayed at the top of the screen
        :param text: Text displayed in the screen
    """

    def __init__(self, screen_or_surface, caption, text):
        ScreenModal.__init__(self, screen_or_surface, caption)
        self.window_x = 70
        self.window_y = 60
        self.window_width -= 2 * self.window_x
        self.window_height -= 2 * self.window_y
        self.outline_shown = True
        self.add_component(
            Picture('pic_icon', self.surface, self.window_x + 5, self.window_y + 30, 48, 48, ICO_WARNING))
        self.title_color = CREAM
        width = self.window_width - 58
        height = self.window_height - self.window_y - 32
        self.add_component(Memo('memo_text', self.surface, self.window_x + 55, self.window_y + 32, width, height, text))
        self.add_component(ButtonText('btn_yes', self.surface, self.window_x + self.window_width - 60,
                                      self.window_y + self.window_height - 37, 55, 32, "Yes"))
        self.components['btn_yes'].button_color = CREAM
        self.add_component(
            ButtonText('btn_no', self.surface, self.window_x + 5, self.window_y + self.window_height - 37, 55, 32,
                       "No"))
        self.components['btn_no'].button_color = CREAM

    def on_click(self, x, y):
        tag_name = super(ScreenModal, self).on_click(x, y)
        if tag_name == 'btn_yes':
            self.return_object = 'yes'
            self.close()
        elif tag_name == 'btn_no':
            self.return_object = 'no'
            self.close()
