import curses
import dataclasses
import glob
import itertools
import logging
import math
from pathlib import Path
import random
import textwrap
import typing

from cursebox.components import screen


logger = logging.getLogger(__file__)


@dataclasses.dataclass
class Logo:
    """
    A Cursebox ASCII logo as text lines and the dimensions of it.

    Logos rendered via <https://patorjk.com/software/taag/>. So far, gone
    through all until "Cosmike" and picked the good ones.
    """
    lines: list[str]
    height: int
    width: int
    message: str | None
    file_name: str

    @classmethod
    def _default_exclude_list(cls) -> list[str]:
        """Get the file names to exclude by default."""
        return [
            "logo.txt",
            "logo2.txt",
        ]

    @classmethod
    def get_variants(
        cls,
        height: int,
        width: int,
        message: str = "",
        exclude: list[str] | None = None,
    ) -> list[typing.Self]:
        """Get variants of the logo fitting inside the provided dimensions."""
        logger.debug(
            "Getting logo varaints that fit a screen size of "
            f"{width}x{height} and the message: \"{message}\"."
        )

        if exclude is None:
            exclude = cls._default_exclude_list()

        variants: list[Logo] = []
        for path in glob.glob(
            str(Path(__file__).parent.parent / "resources" / "logo*.txt"),
        ):
            file_name = path.split("/")[-1]
            if file_name in exclude:
                logger.debug(f"Excluding {file_name}")
            else:
                variant = Logo.from_file(
                    message=message,
                    file_name=file_name,
                )
                if variant.width > width or variant.height > height:
                    logger.debug(
                        f"Skipping {file_name}: Logo too big for the screen.",
                    )
                else:
                    logger.debug(f"Including {file_name} of size {variant.width}x{variant.height}.")
                    variants.append(variant)

        return variants

    @classmethod
    def get_random(
        cls,
        height: int,
        width: int,
        message: str = "",
        exclude: list[str] | None = None,
    ) -> typing.Self:
        return random.choice(Logo.get_variants(
            height=height,
            width=width,
            message=message,
            exclude=exclude,
        ))

    @classmethod
    def from_file(
        cls,
        *,
        file_name: str,
        message: str = "",
    ) -> typing.Self:
        """Prepare the logo from the file on disk."""
        with open(Path(__file__).parent.parent / "resources" / file_name) as f:
            lines = f.readlines()

        logo_width = max([len(line) for line in lines])

        if message:
            # Wrap message in centered lines fitting the logo width.
            message_lines = [
                f"{line:^{logo_width}}"
                for line
                in textwrap.wrap(message, logo_width)
            ]
            lines.append("")
            lines.extend(message_lines)

        return Logo(
            # Make all lines the same length.
            lines=[
                f"{line:<{logo_width}}"
                for line in lines
            ],
            height=len(lines),
            width=logo_width,
            message=message,
            file_name=file_name,
        )

    @classmethod
    def pick_random(
        cls,
        message: str,
        max_height: int,
        max_width: int,
    ) -> str | None:
        """
        Pick a random logo that will fit within the given size.

        If no logos are found, try again without the message.
        """


class StaticSplashScreen(screen.Screen):
    """Show a static splash screen."""

    # The message to show below the logo.
    message: str

    # The name of the logo file to use.
    logo_file_name: str

    def __init__(
        self,
        *,
        logo_file_name: str,
        message: str = "",
    ) -> None:
        """Initialize the splash screen."""
        self.takes_input = False
        self.frame_duration = None
        self.message = message
        self.logo_file_name = logo_file_name

    def render(self) -> None:
        """Render a static splash screen."""
        logo = Logo.from_file(
            message=self.message,
            file_name=self.logo_file_name,
        )
        self.logo_file_name = logo.file_name
        line = itertools.count(0)
        y_position = (self.height - logo.height) // 2
        x_position = (self.width - logo.width) // 2
        for logo_line in logo.lines:
            logo_line = f"{logo_line: <{logo.width}}"
            logo_y = y_position + next(line)
            if (
                0 <= logo_y < self.height - 1
                and 0 <= len(logo_line) <= self.width
            ):
                self.addstr(logo_y, x_position, logo_line)


class AnimatedSplashScreen(screen.Screen):
    """Show an animated splash screen."""

    # The message to show below the logo.
    message: str

    # The name of the logo file to use.
    logo_file_name: str

    # Keep track of how many frames have been rendered.
    frame_count: int

    def __init__(
        self,
        *,
        logo_file_name: str,
        message: str = "",
        ) -> None:
        """Initialize the splash screen."""
        self.takes_input = False
        self.frame_duration = .02
        self.frame_count = 0
        self.message = message
        self.logo_file_name = logo_file_name

    def get_line_parts(
        self,
        line: str,
        progress: int,
        colors: list[int],
        section_width: int,
    ) -> list[tuple[str, int]]:
        """Split the given line into colored parts, based on the progress."""

        # Prepare to collect string parts.
        parts = []
        cursor = progress
        remaining_line = line

        for index, color in enumerate(colors):
            # We don't want to do negative indexing of the string.
            if cursor < 0:
                cursor = 0
            if index == len(colors) - 1:
                line_part = remaining_line
            else:
                line_part = remaining_line[cursor:]
                remaining_line = remaining_line[:cursor]
            parts.insert(
                0,
                (
                    line_part,
                    curses.color_pair(color),
                )
            )

            if cursor == 0 or not remaining_line:
                break
            cursor -= section_width

        return parts


    def render(self) -> None:
        """Render a static splash screen."""
        logo = Logo.from_file(
            message=self.message,
            file_name=self.logo_file_name,
        )
        line = itertools.count(0)
        y_position = (self.height - logo.height) // 2
        x_position = (self.width - logo.width) // 2

        self.frame_duration = .1 / math.sqrt(logo.width)

        colors = [0, 201, 202, 203, 204, 205, 206, 0]
        colors = [0, 101, 102, 103, 102, 101, 0]
        section_width = 4

        # We need enough steps to let the effect roll over the logo with all
        # provided colors, each in their section width.
        total_steps = logo.height + logo.width + len(colors) * section_width
        y = itertools.count(0)
        for line_number, logo_line in enumerate(logo.lines):
            line_y = y_position + next(y)
            effect_position = self.frame_count - line_number

            # Only render the line if it fits within the screen.
            if (
                0 <= line_y < self.height - 1
                and 0 <= len(logo_line) <= self.width
            ):
                # Get the line parts for the effect.
                line_parts = self.get_line_parts(
                    line=logo_line,
                    progress=effect_position,
                    colors=colors,
                    section_width=section_width,
                )
                # Render each part of the line, starting from the calculated
                # x-position.
                part_x = x_position
                for (chars, color) in line_parts:
                    self.addstr(
                        line_y,
                        part_x,
                        chars,
                        color,
                    )
                    part_x += len(chars)


                """
                self.addstr(
                    logo_y,
                    x_position,
                    "{}*{}".format(
                        logo_line[: line_pos - 1], logo_line[line_pos:]
                    ),
                    curses.color_pair(202),
                )
                """

        if self.frame_count == total_steps:
            self.frame_count = -1
        else:
            self.frame_count += 1
