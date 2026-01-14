from abc import (
    ABC,
    abstractmethod,
)
import typing


class Screen(ABC):
    """A screen is an interface with a limited focus."""

    # The dimensions of the screen.
    height: int
    width: int

    # Determines whether the application should forward user input.
    takes_input: bool = False

    # Determines whether the screen should be auto refreshed and how often.
    # None-values tells the application how long to wait (in seconds)
    # between refreshes of the screen.
    frame_duration: float | None

    # The `addstr` method from the window the screen belongs to.
    addstr: typing.Callable

    @abstractmethod
    def render(self) -> None:
        """Render the content of the screen."""

    def update_dimensions(self, height: int, width: int) -> None:
        """Update the dimensions of the screen."""
        self.height = height
        self.width = width
