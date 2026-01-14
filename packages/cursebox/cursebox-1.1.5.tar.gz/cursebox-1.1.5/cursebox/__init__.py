import argparse
import logging
import pathlib
import queue
import sys

from cursebox import lms
from cursebox.v1 import main as main1
from cursebox.v2 import main as main2


logger = logging.getLogger()

parser = argparse.ArgumentParser(
    prog="cursebox",
    description=(
        "A TUI for Lyrion Music Server. Squeezeboxes at your fingertips!"
    ),
    epilog=(
        "Prodiving no arguments will simply launch Cursebox (requires a "
        "configuration file in the default location)."
    ),
)
parser.add_argument(
    "-c",
    "--config",
    help=(
        "Path to configuration file. Optional. "
        "Default location is ~/.cursebox.conf"
    ),
    default="~/.cursebox.conf",
)
parser.add_argument(
    "-s",
    "--server",
    help=(
        "Hostname of the Lyrion Music Server to connect to."
    ),
)
parser.add_argument(
    "-p",
    "--port",
    help=(
        "Port number of the Lyrion Music Server to connect to. "
        "Optional, defaults to 9090."
    ),
    type=int,
    default=9090,
)
parser.add_argument(
    "-u",
    "--username",
    help=(
        "Username used for authentication with Lyrion Music Server. Optional."
    ),
)
parser.add_argument(
    "-P",
    "--password",
    help=(
        "Password used for authentication with Lyrion Music Server. Optional."
    ),
)
parser.add_argument(
    "-b",
    "--player_id",
    help=(
        "ID (MAC address) of the Squeezebox to connect to. Optional."
    ),
)
parser.add_argument(
    "-v",
    "--version",
    help=(
        "Print the Cursebox version."
    ),
)
parser.add_argument(
    "--logging-level",
    help=(
        "Set the logging level."
    ),
    default="WARNING",
)
parser.add_argument(
    "-V",
    "--check_version",
    help=(
        "Check online, during startup, whether a newer version is available. "
        "Optional -- no check is done by default. Not for the paranoid, as an "
        "HTTPS request to pypi.python.org (which is usually also where "
        "Cursebox is installed from) is done if this is enabled."
    ),
    action="store_true",
)
parser.add_argument(
    "-v2",
    action="store_true",
    help=(
        "Launch Cursebox version 2 (experimental)."
    ),
)
parser.add_argument(
    "action",
    help=(
        "Perform a specific action witout launching Cursebox."
    ),
    nargs="?",
    choices=[
        "create-config",
        "playlist",
        "random",
        "lastfm",
        "interactive",
        "tail",
    ],
)
parser.add_argument(
    "action_parameters",
    help=(
        "Further parameters for the actions."
    ),
    nargs="*",
)
arguments = parser.parse_args()

logging.basicConfig(level=arguments.logging_level, filename=pathlib.Path.home() / "cursebox.log")
logging.debug("*" * 79)
logging.debug("NEW RUN")
logging.debug("*" * 79)

def main():
    """Run cursebox."""
    if arguments.v2:
        main2(arguments=arguments)
        sys.exit(0)
    elif arguments.action == "tail":
        listener = lms.LMSListener(
            host=arguments.server,
            port=arguments.port,
        )
        print(f"Connecting to {arguments.server}...")
        listener.connect(
            username=arguments.username,
            password=arguments.password,
        )
        print("Listening to all events from LMS:\n")
        listener.listen()
        while not listener.gracefully_stop:
            try:
                event = listener.queue.get(block=True, timeout=1)
                print(event)
            except queue.Empty:
                pass
            except KeyboardInterrupt:
                print("Disconnecting...")
                listener.stop_listening()
                listener.disconnect()
                print("Disconnected.")
        sys.exit(0)
    else:
        main1()

if __name__ == "__main__":
    main()
