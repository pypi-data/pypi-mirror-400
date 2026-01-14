import argparse
import curses
import logging
import time
import typing

from cursebox import lms
from cursebox.components import screen
from cursebox.components import splash


logger = logging.getLogger(__name__)


class Cursebox:
    """The main curses application."""

    window: curses.window
    height: int
    width: int

    screens: list[screen.Screen]

    def __init__(
        self,
        *,
        window: curses.window,
        arguments: argparse.Namespace,
        debug: bool = False,
    ) -> None:
        """Initialize the Cursebox application."""
        self.window = window
        self.arguments = arguments
        self.debug = debug
        self.screens = []
        self.update_boundaries()

    def update_boundaries(self) -> (int, int):
        """Update window boundaries based on external availability."""
        self.height, self.width = self.window.getmaxyx()
        for screen in self.screens:
            screen.height = self.height
            screen.width = self.width
        return (self.width, self.height)

    def add_screen(
        self,
        screen_type: screen.Screen,
        screen_arguments: dict[str, typing.Any] = {},
    ) -> screen.Screen:
        """Add a screen to the screen stack."""
        new_screen = screen_type(**screen_arguments)
        new_screen.height = self.height
        new_screen.width = self.width
        new_screen.addstr = self.window.addstr
        self.screens.append(new_screen)

        return new_screen

    def remove_screen(self) -> screen.Screen | None:
        """Remove the active screen from the stack, if any."""
        if self.screens:
            return self.screens.pop()

        return None


    def clear(self) -> None:
        """
        Clear the window.

        Overriding this in order to make more things happen upon clearing.
        """
        self.window.clear()

    def render(
        self: typing.Self,
        *,
        clear: bool = False
    ) -> None:
        """Render the window."""
        if clear:
            self.clear()
        self.screens[-1].render()
        if self.debug:
            debug_info = f"[{self.width},{self.height} - {len(self.screens)} screen(s)]"
            self.window.addstr(
                0,
                self.width - len(debug_info),
                debug_info,
            )
        self.window.refresh()

    def run(self) -> None:
        """The main loop for the curses application."""
        # Hide the cursor.
        curses.curs_set(0)

        tag_line = "Squeezeboxes at your fingertips!"
        logo = splash.Logo.get_random(
            message=tag_line,
            height=self.height,
            width=self.width,
        )
        logger.debug(f"Using logo {logo.file_name}")

        # Add an initial splash screen to the screen stack.
        self.add_screen(
            screen_type=splash.StaticSplashScreen,
            screen_arguments={
                "message": "Connecting to LMS...",
                "logo_file_name": logo.file_name,
            },
        )

        # Do an initial rendering while waiting for the LMS connection.
        self.render()

        # Set up LMS client.
        self.client = lms.LMSClient(
            host=self.arguments.server,
            port=self.arguments.port,
        )
        # Connect to LMS.
        self.client.connect(
            username=self.arguments.username,
            password=self.arguments.password,
        )

        # Remove this when the above LMS things are working as expected.
        time.sleep(1)

        # Replace the splash screen in the screen stack with an animated one.
        self.remove_screen()
        splash_screen = self.add_screen(
            screen_type=splash.AnimatedSplashScreen,
            screen_arguments={
                "message": tag_line,
                "logo_file_name": logo.file_name,
            },
        )

        # Animate the splash screen.
        while splash_screen.frame_count != -1:
            self.render(clear=False)
            time.sleep(splash_screen.frame_duration)

        time.sleep(1)

        leave = True
        while not leave:
            key = self.window.getkey()
            if key == "q":
                leave = True
            if key == "KEY_RESIZE":
                self.update_boundaries()
            self.render()
