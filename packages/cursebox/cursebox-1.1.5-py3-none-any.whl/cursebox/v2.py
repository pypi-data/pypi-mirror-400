#!/usr/bin/env python3

import argparse
import curses

from cursebox.components.main import Cursebox
from cursebox.components.splash import Logo


def start_cursebox(
    window: curses.window,
    *,
    arguments: argparse.Namespace
) -> None:
    """Start the Cursebox TUI."""
    curses.use_default_colors()
    # T-theme.
    curses.init_color(101, 490, 784, 973)
    curses.init_pair(101, 101, -1)
    curses.init_color(102, 963, 668, 726)
    curses.init_pair(102, 102, -1)
    curses.init_color(103, 1000, 1000, 1000)
    curses.init_pair(103, 103, -1)

    # P-theme.
    curses.init_color(201, 831, 208, 110)
    curses.init_pair(201, 201, -1)
    curses.init_color(202, 937, 592, 165)
    curses.init_pair(202, 202, -1)
    curses.init_color(203, 961, 957, 321)
    curses.init_pair(203, 203, -1)
    curses.init_color(204, 173, 510, 161)
    curses.init_pair(204, 204, -1)
    curses.init_color(205, 306, 161, 980)
    curses.init_pair(205, 205, -1)
    curses.init_color(206, 451, 0, 525)
    curses.init_pair(206, 206, -1)

    application = Cursebox(
        window=window,
        arguments=arguments,
        debug=True,
    )
    application.run()


def main(*, arguments: argparse.Namespace) -> None:
    """Wrap the Cursebox TUI in curses."""
    curses.wrapper(
        start_cursebox,
        arguments=arguments,
    )
