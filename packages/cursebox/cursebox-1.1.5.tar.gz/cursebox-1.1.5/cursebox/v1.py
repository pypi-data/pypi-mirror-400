#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import code
import curses
from datetime import datetime, timedelta
import getopt
import itertools
import json
import locale
import math
import os
import sys
import time
from urllib import request
from urllib.error import HTTPError

from cursebox import lastfm
from cursebox.lms import LMSClient
from cursebox.version import VERSION


DEFAULT_CONFIG_PATH = "~/.cursebox.conf"
DEFAULT_CONFIG = {
    "server": {
        "password": None,
        "port": 9090,
        "username": None,
        "host": "localhost",
    },
    "selected_player": {"id": "00:00:00:00:00:00", "name": "My Squeezebox"},
    "general": {"check_version": 0},
}

ERROR_MANDATORY_OPTIONS_MISSING = 2
ERROR_INVALID_LASTFM_ARGUMENTS = 3
ERROR_UNKNOWN_ARGUMENT = 4
ERROR_CONFIG_FILE_ALREADY_EXISTS = 5
ERROR_CONFIG_FILE_NOT_FOUND = 6
ERROR_INVALID_RANDOM_ARGUMENTS = 7

BACKSPACE_CODES = [curses.KEY_BACKSPACE, 127]
SPLASH_MINIMUM_TIME = .5


def format_time(time, max_in_context=0):
    """
    Formats a time in seconds nicely (e.g. 105.983 to 1:46).

    Providing a `max_in_context` allows the formatter to know whether
    to return minutes as 2 digits, making sure that a list of formatted
    times all have the same string length.
    """
    seconds = int(round(time % 60))
    minutes = int(math.floor(time / 60))
    hours = int(math.floor(minutes / 60))
    if hours:
        return "{}:{:02d}:{:02d}".format(
            hours, minutes - hours * 60, seconds
        )

    if max_in_context >= 600:
        return "{:02d}:{:02d}".format(minutes, seconds)

    return "{}:{:02d}".format(minutes, seconds)


class Cursebox:
    """
    Cursebox is a curses based interface for controlling Squeezeboxes via the
    Lyrion Media Server CLI.
    """

    # These are in milliseconds.
    SCREEN_UPDATE_DELAY = 1000
    SEARCH_DELAY = 250

    SCREEN_TYPE_NEW_MUSIC = "new music"
    SCREEN_TYPE_SEARCH = "search"
    SCREEN_TYPE = (SCREEN_TYPE_NEW_MUSIC, SCREEN_TYPE_SEARCH)

    def __init__(self, window):
        """
        Cursebox should be instantiated with a curses window.
        """
        self.window = window
        self.search_results_cache = {}
        self.client = None
        self.root = os.path.dirname(__file__)
        self.check_version = False
        self.current_version_available = None

    def get_wch(self):
        """
        Wrapper around `curses.window.cet_wch()`.

        This one doesn't raise an error in nodelay mode.
        """
        try:
            return self.window.get_wch()
        except curses.error:
            return None

    def clear_slate(self, from_row=1):
        """
        Clear the entire window from a given row.
        """
        self.window.move(from_row, 0)
        self.window.clrtobot()

    def render_list(self, items, first_line, length=None, highlight=None):
        """Render a list of items, including an optional hightlight."""
        line = first_line
        # Handle the case of an empty list.
        if not items:
            self.window.addstr(line, 0, "(Empty)")
            return
        # Set a list length if not specified, and make sure we're not trying to
        # draw outside the canvas.
        y, x = self.window.getmaxyx()
        if length is None:
            length = y - first_line
        if first_line + length > y:
            length = y - first_line
        # For now, cut the list if it's too long. Later on, we want to
        # implement some sort of scrolling (#15).
        for item in items[0:length]:
            if (
                type(highlight) is int
                and highlight % len(items) == line - first_line
            ):
                style = curses.A_REVERSE
            else:
                style = 0
            self.window.addstr(line, 0, item, style)
            line = line + 1

    @property
    def allow_play_from_the_top(self):
        """Find out whether 'play from the top' should be an option."""
        now_playing_data = self.client.get_now_playing()
        if now_playing_data.get("mode") != "stop":
            return False
        current_track = self.client.get_current_track_playlist_index()
        current_playlist_tracks = self.client.get_current_playlist_tracks()
        return current_track + 1 == len(current_playlist_tracks)

    def perform_search(self, query):
        """
        Perform a search in LMS and cache all results, for better performance.
        """
        if query in self.search_results_cache.keys():
            results = self.search_results_cache.get(query)
        else:
            results = self.client.search(query)
            self.search_results_cache[query] = results
        return results

    def show_results(self, row, query, item_type, highlight=None):
        """
        Show a list of search results, optionally with a highligted item.
        """
        assert item_type in self.client.ITEM_TYPES, (
            "Unknown search item " 'type "%s"' % item_type
        )
        self.window.move(row, 0)
        self.window.clrtobot()
        self.window.refresh()
        if query:
            results = self.perform_search(query)
            if results.get(item_type):
                items = results.get(item_type)
                y, x = self.window.getmaxyx()
                self.render_list(
                    [" * {}".format(i[1]) for i in items],
                    row,
                    highlight=highlight
                )
            else:
                self.window.addstr(row, 0, "(nothing found)")

    def start_screen(self):
        """
        Show the start screen.
        """
        self.window.nodelay(1)
        self.clear_slate()
        player_name = self.client.get_player_name()
        volume = self.client.get_volume_level()
        if volume < 0:
            volume = "Muted"
        else:
            volume = "{}%".format(volume)
        now_playing_data = self.client.get_now_playing()
        if now_playing_data.get("mode") == "play":
            if now_playing_data.get("remote"):
                now_playing = now_playing_data.get("current_title")
            else:
                now_playing = now_playing_data.get("title")
                if now_playing_data.get("album"):
                    now_playing = "{} - {}".format(
                        now_playing, now_playing_data.get("album")
                    )
                if now_playing_data.get("artist"):
                    now_playing = "{} - {}".format(
                        now_playing, now_playing_data.get("artist")
                    )
        else:
            now_playing = ""
        shuffle_state = self.client.get_shuffle_state()
        repeat_state = self.client.get_repeat_state()
        shuffle_label = ["Off", "Songs", "Albums"][shuffle_state]
        repeat_label = ["Off", "Song", "Playlist"][repeat_state]
        line = itertools.count(1)
        self.window.addstr(next(line), 0, "")
        if now_playing:
            now_playing_line = next(line)
            now_playing_label = "Now playing: "
            self.window.addstr(now_playing_line, 0, now_playing_label)
            duration = now_playing_data.get("duration")
            position = now_playing_data.get("time")
            if not any((duration, position)) or duration == 0:
                self.window.addstr(
                    now_playing_line, len(now_playing_label), now_playing
                )
            else:
                progress = position / duration
                steps = len(now_playing)
                current_step = int(steps * progress)
                self.window.addstr(
                    now_playing_line,
                    len(now_playing_label),
                    now_playing[:current_step],
                    curses.A_STANDOUT,
                )
                self.window.addstr(
                    now_playing_line,
                    len(now_playing_label) + current_step,
                    now_playing[current_step:],
                )
            if position:
                if duration:
                    now_playing_time = "[{}/{}]".format(
                        format_time(position), format_time(duration)
                    )
                else:
                    now_playing_time = "[{}]".format(
                        format_time(position)
                    )
                self.window.addstr(
                    now_playing_line,
                    len(now_playing_label + now_playing) + 1,
                    now_playing_time,
                )

        self.window.addstr(next(line), 0, "Player:   {}".format(player_name))
        self.window.addstr(next(line), 0, "Volume:   {}".format(volume))
        self.window.addstr(
            next(line),
            0,
            "[R]epeat: {}  [S]huffle: {}".format(repeat_label, shuffle_label),
        )
        self.window.addstr(next(line), 0, "")
        self.window.addstr(next(line), 0, "Select action:")
        if self.allow_play_from_the_top:
            self.window.addstr(next(line), 0, "[g]       Play from the top")
        self.window.addstr(
            next(line),
            0,
            "[Space]   {}".format(
                "Pause" if now_playing_data.get("mode") == "play" else "Play"
            ),
        )
        self.window.addstr(next(line), 0, "[h]/[l]   Previous/next track")
        self.window.addstr(next(line), 0, "[p]       Show current playlist")
        self.window.addstr(next(line), 0, "[/]       Search")
        self.window.addstr(next(line), 0, "[n]       New music")
        self.window.addstr(next(line), 0, "[f]       Favorites")
        self.window.addstr(next(line), 0, "[r]       Play random album")
        self.window.addstr(
            next(line), 0, "[j]/[k]   Descrease/increase volume"
        )
        self.window.addstr(next(line), 0, "[v]       Volume settings")
        self.window.addstr(next(line), 0, "[c]       Change player")
        self.window.addstr(next(line), 0, "[q]       Quit")

        if self.check_version:
            next(line)
            if self.current_version_available is None:
                self.window.addstr(
                    next(line), 0, "Unable to check online for newer versions."
                )
            elif VERSION != self.current_version_available:
                self.window.addstr(
                    next(line),
                    0,
                    "Version {} of Cursebox is available (your version is {}).".format(
                        self.current_version_available, VERSION
                    ),
                )
                self.window.addstr(next(line), 0, "Read about how to upgrade:")
                self.window.addstr(
                    next(line),
                    0,
                    "https://git.data.coop/gorgonzo.la/"
                    "cursebox/src/branch/main/README.md#upgrading",
                )
                self.window.addstr(
                    next(line), 0, "Check the changelog to see what's new:"
                )
                self.window.addstr(
                    next(line),
                    0,
                    "https://git.data.coop/gorgonzo.la"
                    "/cursebox/src/branch/main/CHANGELOG.md",
                )

        mac_debug = False
        last_redraw = datetime.now()
        while 1:
            # Get key press.
            c = self.get_wch()
            if c and mac_debug:
                raise Exception(
                    "Key: {}, type: {}, ord: {}".format(
                        c, type(c), ord(c) if type(c) == str else "N/A"
                    )
                )
            if c == "D":
                mac_debug = True
            # Play/pause.
            if c == " ":
                self.client.play_pause()
                # Reload start screen to update now playing info.
                self.start_screen()
                break
            if c == "R":
                self.client.toggle_repeat()
                # Reload start screen to update the state.
                self.start_screen()
                break
            if c == "S":
                self.client.toggle_shuffle()
                # Reload start screen to update the state.
                self.start_screen()
                break
            # Play from the top.
            if c == "g" and self.allow_play_from_the_top:
                self.client.play_playlist_track_index(0)
                self.start_screen()
                break
            # Skip to previous/next track.
            if c in ["h", "l"]:
                (
                    self.client.play_previous()
                    if c == "h"
                    else self.client.play_next()
                )
                self.start_screen()
                break
            # Show current playlist.
            elif c == "p":
                self.current_playlist_screen()
                break
            # Search.
            elif c == "/":
                self.pre_search_screen()
                break
            # New music.
            elif c == "n":
                self.list_new_music()
                break
            # Favorites.
            elif c == "f":
                self.list_favorites()
                break
            # Random album.
            elif c == "r":
                self.play_random_album()
                self.start_screen()
                break
            # Incrase/descrease volume.
            if c in ["j", "k"]:
                step = 2.5
                self.client.change_volume(step if c == "k" else -step)
                self.start_screen()
                break
            # Change volume.
            elif c == "v":
                self.volume_screen()
                break
            # Change player.
            elif c == "c":
                self.player_selection_screen()
                break
            # Quit.
            elif c == "q":
                self.client.disconnect()
                break
            # Ehh... Dunno.
            else:
                pass
            # Update the screen one in a while, in case some info has changed.
            if datetime.now() - last_redraw >= timedelta(
                milliseconds=self.SCREEN_UPDATE_DELAY
            ):
                self.start_screen()
                break

    def pre_search_screen(self):
        """
        Show the pre search screen, allowing the user to choose the type of
        search to perform.
        """
        self.clear_slate()
        self.window.addstr(2, 0, "Choose type of search:")
        self.window.addstr(3, 0, "[c]          Contributor (artist)")
        self.window.addstr(4, 0, "[a]          Album")
        self.window.addstr(5, 0, "[t]          Track")
        self.window.addstr(6, 0, "[q]          Quit")
        self.window.addstr(7, 0, "[Backspace]  Return home")
        while 1:
            # Get key press.
            c = self.get_wch()
            # Search by type.
            if c in ("a", "c", "t"):
                self.search_screen(
                    {
                        "a": self.client.ITEM_TYPE_ALBUM,
                        "c": self.client.ITEM_TYPE_CONTRIBUTOR,
                        "t": self.client.ITEM_TYPE_TRACK,
                    }.get(c)
                )
                break
            # Go back to start.
            elif c in BACKSPACE_CODES:
                self.start_screen()
                break
            # Quit.
            elif c == "q":
                self.client.disconnect()
                break
            # Unknown input.
            else:
                pass

    def volume_screen(self):
        """Change the player volume."""
        volume = self.client.get_volume_level()
        if volume < 0:
            volume = "Muted"
        else:
            volume = "{}%".format(volume)
        self.clear_slate()
        self.window.addstr(2, 0, "Volume: {}".format(volume))
        self.window.addstr(3, 0, "")
        self.window.addstr(
            4,
            0,
            "[m]          {}".format(
                "Unmute" if volume == "Muted" else "Mute"
            ),
        )
        self.window.addstr(5, 0, "[j]/[k]      Descrease/increase volume")
        self.window.addstr(
            6, 0, "[0]...[9]    1 = 10%, 2 = 20%, ..., 0 = 100%"
        )
        self.window.addstr(7, 0, "[q]          Quit")
        self.window.addstr(8, 0, "[Backspace]  Return home")
        while 1:
            # Get key press.
            c = self.get_wch()
            # Toggle mute.
            if c == "m":
                self.client.toggle_mute()
                self.volume_screen()
                break
            # Incrase/descrease.
            if c in ["j", "k"]:
                step = 2.5
                self.client.change_volume(step if c == "k" else -step)
                self.volume_screen()
                break
            # Fixed 1/10 steps.
            if c in [str(i) for i in range(10)]:
                step = int(c)
                # Make the 0-key turn to 100%.
                if step == 0:
                    self.client.set_volume(100)
                else:
                    self.client.set_volume(step * 10)
                self.volume_screen()
                break
            # Go back to start.
            elif c in BACKSPACE_CODES:
                self.start_screen()
                break
            # Quit.
            if c == "q":
                self.client.disconnect()
                break

    def playlist_action_screen(self, item_type, item_id, parent_items=[]):
        """
        Show the playlist action screen, allowing the user to play or queue an
        item, or -- for contributors and artists -- go 1 level deeper.
        """
        # Prepare the screen.
        line = itertools.count(1)
        next(line)
        self.clear_slate()

        # Get details about the item in question.
        if item_type == self.client.ITEM_TYPE_CONTRIBUTOR:
            item_info = self.client.get_contributor_details(item_id)
            self.window.addstr(
                next(line),
                0,
                "Contributor: {}".format(item_info.get("artist")),
            )
        elif item_type == self.client.ITEM_TYPE_ALBUM:
            item_info = self.client.get_album_details(item_id)
            self.window.addstr(
                next(line), 0, "Album: {}".format(item_info.get("album"))
            )
            self.window.addstr(
                next(line), 0, "By:    {}".format(item_info.get("artist"))
            )
        elif item_type == self.client.ITEM_TYPE_TRACK:
            item_info = self.client.get_track_details(item_id)
            self.window.addstr(
                next(line), 0, "Track: {}".format(item_info.get("title"))
            )
            self.window.addstr(
                next(line), 0, "By:    {}".format(item_info.get("artist"))
            )
            if item_info.get("album"):
                self.window.addstr(
                    next(line), 0, "From:  {}".format(item_info.get("album"))
                )
        next(line)

        # Render the action screen.
        self.window.addstr(next(line), 0, "Choose what to do:")
        self.window.addstr(
            next(line), 0, "[a]         Add to playlist (queue)"
        )
        self.window.addstr(next(line), 0, "[p]         Play now")
        if item_type == self.client.ITEM_TYPE_ALBUM:
            self.window.addstr(next(line), 0, "[t]         Select track")
        elif item_type == self.client.ITEM_TYPE_CONTRIBUTOR:
            self.window.addstr(next(line), 0, "[s]         Select album")
        self.window.addstr(next(line), 0, "[q]         Quit")
        return_label = "home"
        if parent_items:
            return_label = {
                self.client.ITEM_TYPE_ALBUM: "to album",
                self.client.ITEM_TYPE_CONTRIBUTOR: "to contributor",
                self.client.ITEM_TYPE_TRACK: "to track",
                self.SCREEN_TYPE_NEW_MUSIC: "to new music",
                self.SCREEN_TYPE_SEARCH: "to search",
            }.get(parent_items[-1][0])
        self.window.addstr(
            next(line), 0, "[Backspace] Return {}".format(return_label)
        )
        while 1:
            # Get key press.
            c = self.get_wch()
            # Quit.
            if c == "q":
                self.client.disconnect()
                break
            # Play immediately.
            elif c == "p":
                self.client.load_item_by_type_and_id(item_type, item_id)
                self.notify(f"Playing {item_type} now.")
            # Add to playlist.
            elif c == "a":
                self.client.add_item_by_type_and_id(item_type, item_id)
                self.notify(f"Added {item_type} to playlist.")
            # For albums, select track
            elif c == "t" and item_type == self.client.ITEM_TYPE_ALBUM:
                parent_items.append((item_type, item_id))
                self.album_track_screen(item_id, parent_items)
                break
            # For contributors, select album
            elif c == "s" and item_type == self.client.ITEM_TYPE_CONTRIBUTOR:
                parent_items.append((item_type, item_id))
                self.contributor_album_screen(
                    item_info.get("artist"),
                    item_id,
                    parent_items,
                )
                break
            # Return to previous.
            elif c in BACKSPACE_CODES:
                self.go_to_parent(parent_items)
                break

    def album_track_screen(self, album_id, parent_items=[]):
        """
        Show the tracks of an album, allowing the user to choose which track to
        queue/play.
        """
        self.clear_slate()
        tracks = self.client.get_album_tracks(album_id)
        self.window.addstr(2, 0, "Select a track:")
        highlight = None
        self.render_list(
            [t.get("title") for t in tracks], 3, highlight=highlight
        )
        track = None
        while 1:
            # Update selected track.
            if highlight is not None:
                track = tracks[highlight]
            # Get key press.
            c = self.get_wch()
            if type(c) is str and ord(c) in [curses.KEY_ENTER, 10, 13]:
                if highlight is not None:
                    self.playlist_action_screen(
                        self.client.ITEM_TYPE_TRACK,
                        track.get("id"),
                        parent_items,
                    )
                    break
                self.start_screen()
                break
            # Handle Tab and Shift+Tab properly. These are used for
            # highlighting search result to be played.
            elif c == "\t" or c == 353:
                if highlight is None:
                    highlight = 0 if c == "\t" else -1
                else:
                    highlight = highlight + (1 if c == "\t" else -1)
                # Make sure the highlight index is positive.
                highlight = highlight % len(tracks)
                highlight = highlight + len(tracks)
                highlight = highlight % len(tracks)
                # Render list.
                self.render_list(
                    [t.get("title") for t in tracks], 3, highlight=highlight
                )
            # Play immediately.
            elif c == "p":
                if track is not None:
                    self.client.load_item_by_type_and_id(
                        self.client.ITEM_TYPE_TRACK, track.get("id")
                    )
                    self.start_screen()
                    break
            # Add to playlist.
            elif c == "a":
                if track is not None:
                    self.client.add_item_by_type_and_id(
                        self.client.ITEM_TYPE_TRACK, track.get("id")
                    )
                    self.start_screen()
                    break
            # Return to album action screen.
            elif c in BACKSPACE_CODES:
                self.go_to_parent(parent_items)
            # Quit.
            if c == "q":
                self.client.disconnect()
                break

    def contributor_album_screen(
            self,
            contributer_name,
            contributor_id,
            parent_items=[],
        ):
        """
        Show the albums of a contributor, allowing the user to choose which
        album to queue/play.
        """
        self.clear_slate()

        albums = self.client.get_contributor_albums(contributor_id)
        if not albums:
            self.clear_slate()
            self.notify(
                f"No albums found by {contributer_name} :(",
                wait_for_confirmation=True,
            )
            self.go_to_parent(parent_items)
            return

        max_name_length = max([len(a.get("title")) for a in albums])
        self.window.addstr(2, 0, f"Select an album by {contributer_name}:")
        highlight = None
        label_template = f"{{:{max_name_length}}}  {{}}"
        for a in albums:
            a["label"] = label_template.format(
                a.get("title"),
                a.get('year') if a.get("year") else " -- ",
            )
        self.render_list(
            [a.get("label") for a in albums],
            3,
            highlight=highlight,
        )
        album = None
        while 1:
            # Update album.
            if highlight is not None:
                album = albums[highlight]
            # Get key press.
            c = self.get_wch()
            if type(c) is str and ord(c) in [curses.KEY_ENTER, 10, 13]:
                if highlight is not None:
                    self.playlist_action_screen(
                        self.client.ITEM_TYPE_ALBUM,
                        album.get("id"),
                        parent_items,
                    )
            # Handle Tab and Shift+Tab properly. These are used for
            # highlighting search result to be played.
            elif c in ["\t", 353, "j", "k"]:
                if highlight is None:
                    highlight = 0 if c in ["\t", "j"] else -1
                else:
                    highlight = highlight + (1 if c in ["\t", "j"] else -1)
                # Make sure the highlight index is positive.
                highlight = highlight % len(albums)
                highlight = highlight + len(albums)
                highlight = highlight % len(albums)
                # Render list.
                self.render_list(
                    [a.get("label") for a in albums], 3, highlight=highlight
                )
            # Play immediately.
            elif c == "p":
                if album is not None:
                    self.client.load_item_by_type_and_id(
                        self.client.ITEM_TYPE_ALBUM, album.get("id")
                    )
                    self.notify("Playing album")
            # Add to playlist.
            elif c == "a":
                if album is not None:
                    self.client.add_item_by_type_and_id(
                        self.client.ITEM_TYPE_ALBUM, album.get("id")
                    )
                    self.notify("Album added to playlist")
            # Select track.
            elif c == "t":
                if album is not None:
                    self.album_track_screen(album.get("id"))
                    break
            # Return to contributor action menu.
            elif c in BACKSPACE_CODES:
                self.go_to_parent(parent_items)
                break
            # Quit.
            if c == "q":
                self.client.disconnect()
                break

    def play_random_album(self):
        """Play a random album."""
        album = self.client.get_random_album()
        self.client.load_item_by_type_and_id(
            self.client.ITEM_TYPE_ALBUM, album.get("id")
        )

    def list_new_music(self, highlight=None):
        """Show the most recently added albums."""
        self.clear_slate()
        albums = self.client.get_most_recent_albums()
        line = itertools.count(2)
        self.window.addstr(next(line), 0, "Select an album:")
        self.window.addstr(
            next(line), 0, "[j]/[k]  Move highlight down/up"
        )
        next(line)
        list_line = next(line)
        items = [
            " * {} by {}".format(a.get("title"), a.get("artist")) for a in albums
        ]
        y, x = self.window.getmaxyx()
        self.render_list(items, list_line, highlight=highlight)
        album = None
        while 1:
            # Update album.
            if highlight is not None:
                album = albums[highlight]
            # Get key press.
            c = self.get_wch()
            if type(c) is str and ord(c) in [curses.KEY_ENTER, 10, 13]:
                if highlight is not None:
                    self.playlist_action_screen(
                        self.client.ITEM_TYPE_ALBUM,
                        album.get("id"),
                        [(self.SCREEN_TYPE_NEW_MUSIC, highlight)],
                    )
                    break
                self.start_screen()
                break
            # Navigate and highlight items in the list with j/k.
            elif c in ["j", "k"]:
                if highlight is None:
                    highlight = 0 if c == "j" else -1
                else:
                    highlight = highlight + (1 if c == "j" else -1)
                y, x = self.window.getmaxyx()
                # Make sure the highlight index is positive.
                highlight = highlight % len(albums)
                highlight = highlight + len(albums)
                highlight = highlight % len(albums)
                # Render list.
                self.render_list(items, list_line, highlight=highlight)
            # Play immediately.
            elif c == "p":
                if album is not None:
                    self.client.load_item_by_type_and_id(
                        self.client.ITEM_TYPE_ALBUM, album.get("id")
                    )
                    self.start_screen()
                    break
            # Add to playlist.
            elif c == "a":
                if album is not None:
                    self.client.add_item_by_type_and_id(
                        self.client.ITEM_TYPE_ALBUM, album.get("id")
                    )
                    self.start_screen()
                    break
            # Select track.
            elif c == "t":
                if album is not None:
                    self.album_track_screen(album.get("id"))
                    break
            # Return to start screen.
            elif c in BACKSPACE_CODES:
                self.start_screen()
                break
            # Quit.
            if c == "q":
                self.client.disconnect()
                break

    def list_favorites(self, item_id=None, title=None):
        """Show a favorites listing, with support for hierarchies."""
        self.clear_slate()
        favorites = self.client.get_favorites(item_id)
        # Append sublevel indicator.
        max_length = max([len(f.get("name")) for f in favorites])
        for f in favorites:
            if f.get("hasitems") > 0:
                f["original_name"] = f.get("name")
                f["name"] = "{:{}}>".format(f.get("name"), max_length + 2)
        # Make sure we have a title.
        if not title:
            title = "Select a favorite"
        line = itertools.count(2)
        self.window.addstr(next(line), 0, "{}:".format(title))
        self.window.addstr(
            next(line), 0, "[j]/[k]  Move highlight down/up"
        )
        next(line)
        highlight = None
        items = [" * {}".format(f.get("name")) for f in favorites]
        y, x = self.window.getmaxyx()
        list_line = next(line)
        self.render_list(items, list_line, highlight=highlight)
        favorite = None
        while 1:
            # Update favorite.
            if highlight is not None:
                favorite = favorites[highlight]
            # Get key press.
            c = self.get_wch()
            if type(c) is str and ord(c) in [curses.KEY_ENTER, 10, 13]:
                if highlight is not None:
                    # Show another listing if this favorite has sub items.
                    if favorite.get("hasitems") > 0:
                        self.list_favorites(
                            favorite.get("id"), favorite.get("original_name")
                        )
                    # Show actions for the favorite.
                    else:
                        self.favorite_action_screen(favorite)
                    break
                self.start_screen()
                break
            # Navigate and highlight items in the list with j/k.
            elif c in ["j", "k"]:
                if highlight is None:
                    highlight = 0 if c == "j" else -1
                else:
                    highlight = highlight + (1 if c == "j" else -1)
                y, x = self.window.getmaxyx()
                # Make sure the highlight index is positive.
                highlight = highlight % len(favorites)
                highlight = highlight + len(favorites)
                highlight = highlight % len(favorites)
                # Render list.
                self.render_list(items, list_line, highlight=highlight)
            # Play immediately.
            elif c == "p":
                if favorite is not None and favorite.get("hasitems") == 0:
                    self.client.load_favorite(favorite.get("id"))
                    self.start_screen()
                    break
            # Add to playlist.
            elif c == "a":
                if favorite is not None and favorite.get("hasitems") == 0:
                    self.client.queue_favorite(favorite.get("id"))
                    self.start_screen()
                    break
            # Return to start screen.
            elif c in BACKSPACE_CODES:
                self.start_screen()
                break
            # Quit.
            if c == "q":
                self.client.disconnect()
                break

    def favorite_action_screen(self, favorite):
        """
        Show the favorite action screen, allowing the user to play or queue a
        favorite.
        """
        self.clear_slate()
        self.window.addstr(2, 0, favorite.get("name"))
        self.window.addstr(3, 0, "Choose what to do:")
        self.window.addstr(4, 0, "[a]         Add to playlist (queue)")
        self.window.addstr(5, 0, "[p]         Play now")
        self.window.addstr(6, 0, "[q]         Quit")
        self.window.addstr(7, 0, "[Backspace] Return home")
        while 1:
            # Get key press.
            c = self.get_wch()
            # Quit.
            if c == "q":
                self.client.disconnect()
                break
            # Play immediately.
            elif c == "p":
                self.client.load_favorite(favorite.get("id"))
                self.start_screen()
                break
            # Add to playlist.
            elif c == "a":
                self.client.queue_favorite(favorite.get("id"))
                self.start_screen()
                break
            # Return home.
            elif c in BACKSPACE_CODES:
                self.start_screen()
                break

    def search_screen(self, item_type, query=""):
        """
        Show the search screen, allowing the user to search items of a
        previously specified type.
        """
        label = "Search {}:".format(item_type)
        self.clear_slate()
        line = itertools.count(2)
        query_line = next(line)
        self.window.addstr(query_line, 0, "{} {}".format(label, query))
        self.window.addstr(
            next(line),
            0,
            "[Tab]/[Shift]+[Tab]  Highlight next/previous result"
        )
        next(line)
        results_line = next(line)
        highlight = None
        last_keypress = datetime.now() if query else None
        while 1:
            # Get key press.
            c = self.get_wch()
            # If key is enter, play highligted item (if any) and return home.
            if type(c) is str and ord(c) in [curses.KEY_ENTER, 10, 13]:
                if highlight is not None:
                    results = self.search_results_cache.get(query).get(
                        item_type
                    )
                    # Make sure the highlight index is positive.
                    highlight = highlight % len(results)
                    highlight = highlight + len(results)
                    highlight = highlight % len(results)
                    item_id, item_name = results[highlight]
                    self.playlist_action_screen(
                        item_type,
                        item_id,
                        parent_items=[
                            (self.SCREEN_TYPE_SEARCH, query, item_type)
                        ],
                    )
                    break
                self.start_screen()
                break
            # Handle backspace properly.
            elif c in BACKSPACE_CODES:
                if not query:
                    self.pre_search_screen()
                    break
                query = query[:-1]
                self.window.addstr(query_line, len(label) + 1, query)
                self.window.clrtoeol()
                highlight = None
                last_keypress = datetime.now()
            # Handle Tab and Shift+Tab properly. These are used for
            # highlighting search result to be played.
            elif c == "\t" or c == 353:
                if highlight is None:
                    highlight = 0 if c == "\t" else -1
                else:
                    highlight = highlight + (1 if c == "\t" else -1)
                # Make sure to update immediately in this case.
                last_keypress = datetime.now() - timedelta(
                    milliseconds=self.SEARCH_DELAY
                )
            # Append key to query if it looks like a character was pressed.
            elif type(c) is str:
                query = query + c
                self.window.addstr(query_line, len(query) + len(label), c)
                highlight = None
                last_keypress = datetime.now()
            # Some other special key was pressed. Don't really know how to handle
            # these yet.
            else:
                pass
            # Delay search a bit, to improve the find-as-you-type experience.
            if last_keypress and datetime.now() - last_keypress >= timedelta(
                milliseconds=self.SEARCH_DELAY
            ):
                self.show_results(results_line, query, item_type, highlight)
                last_keypress = None
            self.window.refresh()

    def build_current_playlist_tracks(self, current_track):
        """
        Build a list of tracks for the current playlist screen.
        """
        # Get the playlist tracks.
        current_playlist_tracks = self.client.get_current_playlist_tracks()
        is_playing = self.client.get_now_playing().get("mode") == "play"

        # Determine whether to show 2 digits for minutes in the listing.
        longest_track = 0 if not current_playlist_tracks else max(
            [t.get("duration") for t in current_playlist_tracks]
        )

        # Format the track list.
        tracks = [
            " [{}] {} {}".format(
                format_time(t.get("duration"), longest_track),
                (
                    ("♪" if is_playing else "=")
                    if t.get("playlist index") == current_track
                    else "·"
                ),
                t.get("title"),
            )
            for t in current_playlist_tracks
            if t
        ]
        return tracks

    def current_playlist_screen(self):
        """
        Show the current playlist.

        Also indicate which track is currently playing, and allow the user to
        Tab navigate tracks, to play another track.
        """
        self.clear_slate()
        line = itertools.count(2)
        current_track = self.client.get_current_track_playlist_index()
        current_playlist_tracks = self.client.get_current_playlist_tracks()
        tracks = self.build_current_playlist_tracks(current_track)
        self.window.addstr(next(line), 0, "Actions:")
        self.window.addstr(next(line), 0, "[Space]      Toggle play/pause")
        self.window.addstr(next(line), 0, "[p]          Play highligted track")
        self.window.addstr(
            next(line), 0, "[D]          Remove highligted track"
        )
        self.window.addstr(
            next(line), 0, "[j]/[k]     Move highlight down/up"
        )
        self.window.addstr(
            next(line), 0, "[h]/[l]     Skip to previous/next track"
        )
        self.window.addstr(
            next(line), 0, "[J]/[K]     Move highlighted track down/up"
        )
        self.window.addstr(next(line), 0, "[Backspace]  Return home")
        self.window.addstr(next(line), 0, "[q]          Quit")
        next(line)
        self.window.addstr(next(line), 0, "Current playlist:")
        highlight = current_track
        playlist_line = next(line)
        self.render_list(tracks, playlist_line, highlight=highlight)
        while 1:
            # Get key press.
            c = self.get_wch()
            # Toggle play/pause.
            if c == " ":
                self.client.play_pause()
                tracks = self.build_current_playlist_tracks(current_track)
                self.render_list(
                    tracks, playlist_line, highlight=highlight
                )
            # Play highlighted track.
            if c == "p":
                if highlight is not None:
                    # Make sure the highlight index is positive.
                    highlight = highlight % len(tracks)
                    highlight = highlight + len(tracks)
                    highlight = highlight % len(tracks)
                    track = tracks[highlight]
                    self.client.play_playlist_track_index(highlight)
                    # Update current track and track listing.
                    current_track = (
                        self.client.get_current_track_playlist_index()
                    )
                    tracks = self.build_current_playlist_tracks(current_track)
                    self.render_list(
                        tracks, playlist_line, highlight=highlight
                    )
            # Remove highlighted track.
            if c == "D":
                if highlight is not None:
                    # Make sure the highlight index is positive.
                    highlight = highlight % len(tracks)
                    highlight = highlight + len(tracks)
                    highlight = highlight % len(tracks)
                    # Clear the entire window from beginning of the current
                    # playlist, as the list will be shorter after the track is
                    # removed, which would leave the last track of the previous
                    # playlist burned into the screen if we don't clear it.
                    self.window.move(playlist_line, 0)
                    self.window.clrtobot()
                    # Remove track and update the screen.
                    self.client.remove_track(highlight)
                    tracks = self.build_current_playlist_tracks(current_track)
                    self.render_list(
                        tracks, playlist_line, highlight=highlight
                    )
            # Handle j/k navigation. These are used for
            # highlighting search result to be played.
            elif c in ["j", "k"]:
                if highlight is None:
                    highlight = 0 if c == "j" else -1
                else:
                    highlight = highlight + (1 if c == "j" else -1)
                self.render_list(tracks, playlist_line, highlight=highlight)
            # Skip to previous/next track.
            elif c in ["h", "l"]:
                (
                    self.client.play_previous()
                    if c == "h"
                    else self.client.play_next()
                )
                # Update current track and track listing.
                current_track = self.client.get_current_track_playlist_index()
                tracks = self.build_current_playlist_tracks(current_track)
                self.render_list(tracks, playlist_line, highlight=highlight)
            # Remove highlighted track.
            if c in ["J", "K"]:
                if highlight is not None:
                    # Make sure the highlight index is positive.
                    highlight = highlight % len(tracks)
                    highlight = highlight + len(tracks)
                    highlight = highlight % len(tracks)
                    # Determine the new position of the highlighted track.
                    new_position = highlight + (-1 if c == "K" else 1)
                    # Only allow to move tracks to a position within the range
                    # of the current playlist.
                    if 0 <= new_position < len(tracks):
                        # Clear the entire window from beginning of the current
                        # playlist, as rearranging tracks will leave the last
                        # part of the longer track name burned into the screen,
                        # if we don't clear it.
                        self.window.move(playlist_line, 0)
                        self.window.clrtobot()
                        # Move track.
                        self.client.move_track(highlight, new_position)
                        # Update highlight and current track indexes,
                        # if necessary.
                        if current_track in [highlight, new_position]:
                            current_track = (
                                highlight
                                if current_track == new_position
                                else new_position
                            )
                        highlight = new_position
                        tracks = self.build_current_playlist_tracks(
                            current_track
                        )
                        self.render_list(
                            tracks, playlist_line, highlight=highlight
                        )
            # Quit.
            elif c == "q":
                self.client.disconnect()
                break
            # Return to home.
            elif c in BACKSPACE_CODES:
                self.start_screen()
                break

    def go_to_parent(self, parent_items=[]):
        """
        Go to the most recent parent screen.

        Or return home if no parents are found.
        """
        if not parent_items:
            self.start_screen()
            return
        else:
            parent = parent_items.pop()
            if parent[0] in self.client.ITEM_TYPES:
                parent_type, parent_id = parent
                self.playlist_action_screen(
                    parent_type, parent_id, parent_items
                )
            elif parent[0] == self.SCREEN_TYPE_SEARCH:
                _, query, parent_type = parent
                self.search_screen(parent_type, query)
            elif parent[0] == self.SCREEN_TYPE_NEW_MUSIC:
                _, highlight = parent
                self.list_new_music(highlight)
            else:
                raise ValueError(
                    'Unknown parent item type "{}".'.format(parent[0])
                )

    def player_selection_screen(self, message=None):
        """
        List players connected to LMS.

        Allows the user to choose which player to control. Optionally provide
        a message to be shown along with the menu, e.g. "Player XYZ is not
        available, please select another player."
        """
        self.clear_slate()
        players = self.client.get_players()
        menu_items = [
            " {} {}".format(
                (
                    "x"
                    if p.get("playerid") == self.client.default_player_id
                    else "*"
                ),
                p.get("name"),
            )
            for p in players
        ]
        line = itertools.count(2)
        if message:
            self.window.addstr(next(line), 0, message)
        self.window.addstr(next(line), 0, "Select a player:")
        self.window.addstr(
            next(line), 0, "[j]/[k]  Move highlight down/up"
        )
        next(line)
        list_line = next(line)
        idx = 0

        # Find position of currently selected player.
        highlight = None
        for player in players:
            if player.get("playerid") == self.client.default_player_id:
                highlight = idx
            idx += 1

        self.render_list(menu_items, list_line, highlight=highlight)
        while 1:
            # Get key press.
            c = self.get_wch()
            if type(c) is str and ord(c) in [curses.KEY_ENTER, 10, 13]:
                if highlight is not None:
                    # Make sure the highlight index is positive.
                    highlight = highlight % len(players)
                    highlight = highlight + len(players)
                    highlight = highlight % len(players)
                    player = players[highlight]
                    self.client.change_player_id(player.get("playerid"))
                    self.start_screen()
                    break
            # Navigate and highlight items in the list with j/k.
            elif c in ["j", "k"]:
                if highlight is None:
                    highlight = 0 if c == "j" else -1
                else:
                    highlight = highlight + (1 if c == "j" else -1)
                self.render_list(menu_items, list_line, highlight=highlight)
            # Quit.
            elif c == "q":
                self.client.disconnect()
                break
            # Return to home.
            elif c in BACKSPACE_CODES:
                self.start_screen()
                break

    def show_splash(self, message=None, animate=False):
        """
        Show a splash screen with the ASCII logo.

        Optionally show a message along with the logo, and optionally animate
        the logo.
        """
        # Read the logo data.
        with open(os.path.join(self.root, "./resources/logo.txt")) as f:
            logo_lines = f.readlines()

        if not animate:
            # Draw the static logo.
            line = itertools.count(0)
            for logo_line in logo_lines:
                self.window.addstr(next(line), 0, logo_line)

            # Show the version.
            self.window.addstr(next(line), 0, " {:^40}".format(VERSION))

            # Show message if provied.
            if message:
                next(line)
                self.window.addstr(next(line), 0, " {:^40}".format(message))
            self.window.refresh()
        else:
            # Animate the logo.
            steps = -1 + len(logo_lines) + len(logo_lines[0])
            for step in range(steps + 2):
                self.clear_slate(0)
                line = itertools.count(0)
                for l in range(len(logo_lines)):
                    logo_line = logo_lines[l]
                    line_pos = step - l
                    if 1 <= line_pos <= len(logo_line):
                        self.window.addstr(
                            next(line),
                            0,
                            "{} {}".format(
                                logo_line[: line_pos - 1], logo_line[line_pos:]
                            ),
                        )
                    else:
                        self.window.addstr(next(line), 0, logo_line)

                # Show version.
                self.window.addstr(next(line), 0, " {:^40}".format(VERSION))

                # Show message if provided.
                if message:
                    next(line)
                    self.window.addstr(
                        next(line), 0, " {:^40}".format(message)
                    )

                time.sleep(.015)
                self.window.refresh()

    def notify(self, message=None, wait_for_confirmation=False):
        """Show a notification at the top."""
        if wait_for_confirmation:
            self.clear_slate()
            self.window.addstr(0, 0, message)
            self.window.addstr(2, 0, "[Enter]  To continue")
            self.window.refresh()
            while 1:
                # Get key press.
                c = self.get_wch()
                # Quit.
                if c == "q":
                    self.client.disconnect()
                    break
                elif type(c) is str and ord(c) in [curses.KEY_ENTER, 10, 13]:
                    break

            self.window.addstr(0, 0, " " * len(message))
            self.window.addstr(0, 0, "CURSEBOX!")
            return

        for i in range(3):
            self.window.addstr(0, 0, message, curses.A_REVERSE)
            self.window.refresh()
            time.sleep(.05)
            self.window.addstr(0, 0, message)
            self.window.refresh()
            time.sleep(.05)
        self.window.addstr(0, 0, " " * len(message))
        self.window.addstr(0, 0, "CURSEBOX!", 0)
        self.window.refresh()


    def start(
        self,
        server_name,
        server_port,
        username,
        password,
        player_id,
        check_version,
    ):
        """
        Initialise and connect an LMS client and set up the curses application.
        """
        self.check_version = check_version
        # Prepare curses window.
        curses.curs_set(0)
        # Show splash screen.
        self.show_splash("Connecting to LMS...")
        # Set up LMS client.
        start_time = datetime.now()
        self.client = LMSClient(
            host=server_name,
            port=server_port,
            default_player_id=player_id,
        )
        # Connect to LMS.
        self.client.connect(username, password)
        # Check for newer version, if check is enabled.
        if self.check_version:
            try:
                with request.urlopen(
                    "https://pypi.python.org/pypi/cursebox/json", timeout=5
                ) as version_data:
                    version_data = json.loads(
                        version_data.read().decode("utf-8")
                    )
                    version_available = version_data.get("info").get("version")
                    self.current_version_available = version_available
            except HTTPError:
                self.current_version_available = None

        # Make sure splash screen is shown for at least a minimum amount
        # of time.
        splash_time = datetime.now() - start_time
        if splash_time.seconds == 0:
            splash_subsecond = splash_time.microseconds / 1000000
            if splash_subsecond < SPLASH_MINIMUM_TIME:
                time.sleep(SPLASH_MINIMUM_TIME - splash_subsecond)

        # Animate the logo as last part of the splash sequence.
        self.show_splash("Squeezeboxes at your fingertips!", True)

        # Set up window and show correct screen.
        self.clear_slate(0)
        self.window.addstr(0, 0, "CURSEBOX!")

        # If player ID is set and the specified player seems to be connected,
        # show the start screen. Otherwise show the player selected screen.
        if not self.client.default_player_id:
            self.player_selection_screen()
        elif not self.client.is_player_connected():
            self.player_selection_screen(
                "Player with the ID {} is not connected.".format(
                    self.client.default_player_id
                )
            )
        else:
            self.start_screen()


def usage():
    print(
        """Usage: cursebox [OPTIONS] [ARG]
Squeezebox and music library control. Squeezeboxes at your fingertips!

OPTIONS

The following options are recognised:

  -c, --config          Path to configuration file. Optional. Default location
                        is ~/.cursebox.conf
  -s, --server          Hostname of the LMS server to connect to.
  -p, --port            Port of the LMS server to connect to. Optional,
                        defaults to 9090.
  -u  --username        Username used for authentication with LMS. Optional.
  -P  --password        Password used for authentication with LMS. Optional.
  -b, --player_id       ID (MAC address) of the Squeezebox to connect to.
  -v, --version         Print the Cursebox version ({}).
  -V, --check_version   Check online, during startup, whether a newer version
                        is available. Optional -- no check is done by default.
                        Not for the paranoid, as an HTTPS request to
                        pypi.python.org (which is also where Cursebox is
                        installed from) is done if this is enabled.
  -h, --help            Show this help message. Obviously optional.

ARGUMENT(S)

Can be one of the following:

  create-config         Create a new default configuration file in
                        ~/.cursebox.conf (if it doesn't already exist).
  lastfm                Start Last.fm mode, which gives you some playlisting
                        options based on Last.fm user data.
  playlist              Print the current playlist of a player (-b/--player_id
                        option is required for this).
  random <type>         Play a random item of the specified type. Currently,
                        <type> can only be "album". (-b/--player_id option is
                        required for this).
  interactive           Start a Python REPL with an LMS instance loaded and
                        connected (mostly for debugging purposes).

Prodiving no arguments will simply launch Cursebox (requires a configuration
file in the default location).""".format(
            VERSION
        )
    )


def version_information():
    print("Cursebox {}".format(VERSION))


def create_default_config(config_path):
    """
    Creates a new default configuration file.

    At the given path, but only if the file doesn't already exist.
    """
    # Expand path if located in home directory.
    if "~" in config_path:
        config_path = os.path.expanduser(config_path)

    # Make sure there is no existing file on the given path.
    if os.path.exists(config_path):
        print(
            "The file `{}` already exists. Cursebox will not "
            "overwrite this.".format(config_path)
        )
        sys.exit(ERROR_CONFIG_FILE_ALREADY_EXISTS)

    # Create the config file.
    with open(config_path, "w") as config_file:
        config_file.write(json.dumps(DEFAULT_CONFIG, indent=4))
    print(
        "Configuration created in `{}`. Please edit to suit your "
        "own setup.".format(config_path)
    )
    sys.exit(0)


def start_cursebox(
    window,
    server_name,
    server_port,
    username,
    password,
    player_id,
    check_version,
):
    """A small helper function to get started."""
    curses.use_default_colors()
    cb = Cursebox(window)
    if server_port is None:
        server_port = DEFAULT_CONFIG.get("server").get("port")
    cb.start(
        server_name, server_port, username, password, player_id, check_version
    )


def main():
    """The main application."""
    # Read command line arguments.
    argv = sys.argv[1:]

    # Parse options.
    try:
        opts, args = getopt.getopt(
            argv,
            "c:s:p:u:P:b:hvV",
            [
                "config=",
                "server=",
                "port=",
                "username=",
                "password=",
                "player_id=",
                "help",
                "version",
                "check_version",
            ],
        )
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    # Handle options.
    config_check_version = None
    config_path = None
    server_name = None
    server_port = None
    player_id = None
    username = None
    password = None

    # Extract options.
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-v", "--version"):
            version_information()
            sys.exit()
        elif opt in ("-V", "--check_version"):
            config_check_version = True
        elif opt in ("-c", "--config"):
            config_path = arg
        elif opt in ("-s", "--server"):
            server_name = arg
        elif opt in ("-p", "--port"):
            server_port = arg
        elif opt in ("-b", "--player_id"):
            player_id = arg
        elif opt in ("-u", "--username"):
            username = arg
        elif opt in ("-P", "--password"):
            password = arg

    # Create config file if user asked for this.
    if args:
        if args[0] == "create-config":
            create_default_config(DEFAULT_CONFIG_PATH)
            sys.exit(0)

    # Read config file, if set and/or present.

    # Fall back to default config path, if file exists.
    if not config_path:
        default_config_path = DEFAULT_CONFIG_PATH
        if "~" in default_config_path:
            default_config_path = os.path.expanduser(default_config_path)
        if os.path.exists(default_config_path):
            config_path = default_config_path

    # Try to load config, if set.
    if config_path:
        # Check that config file exists.
        if "~" in config_path:
            config_path = os.path.expanduser(config_path)
        if not os.path.exists(config_path):
            print("Configuration file `{}` not found.".format(config_path))
            sys.exit(ERROR_CONFIG_FILE_NOT_FOUND)
        # Read config file.
        with open(config_path, "r") as config_file:
            config = json.loads(config_file.read())
        # Parse config options, but don't override if already specified by
        # as options.
        if "server" in config.keys():
            server_config = config.get("server")
            if not server_name:
                server_name = server_config.get("host", None)
            if not server_port:
                server_port = server_config.get("port", None)
                if not server_port:
                    server_port = 9090
            if not username:
                username = server_config.get("username", None)
            if not password:
                password = server_config.get("password", None)
        if "selected_player" in config.keys():
            player_config = config.get("selected_player")
            if not player_id:
                player_id = player_config.get("id", None)
        if "general" in config.keys():
            general_config = config.get("general")
            if config_check_version is None:
                config_check_version = general_config.get(
                    "check_version", False
                )

    # Make sure mandatory options are set.
    if server_name is None:
        usage()
        sys.exit(ERROR_MANDATORY_OPTIONS_MISSING)

    # Act upon arguments, if user specified any.
    if args:
        # Start interactive mode.
        if args[0] == "interactive":
            lms = LMSClient(
                host=server_name,
                port=(
                    server_port
                    if server_port
                    else DEFAULT_CONFIG.get("server").get("port")
                ),
                default_player_id=player_id,
            )
            lms.connect(username, password)
            code.interact(
                banner=(
                    "Welcome to the interactive LMS client. A client instance\n"
                    "is ready for you in the `lms` variable. Have fun!"
                ),
                local=dict(globals(), **locals()),
                exitmsg="Goodbye :)",
            )
            exit(0)

        # Last.fm mode.
        if args[0] == "lastfm":
            if len(args) != 3:
                print(
                    "Last.fm mode takes exactly 3 argument (including the "
                    '"lastfm" argument).'
                )
                print("Like this: cursebox lastfm <action> <username>")
                print("You provided {} argument(s).".format(len(args)))
                sys.exit(ERROR_INVALID_LASTFM_ARGUMENTS)

            action = args[1]
            lastfm_username = args[2]

            if action != "lovedtracks":
                print('Unknown Last.fm action "{}".'.format(action))
                print("Available actions are:")
                print(
                    "  lovedtracks     Create a playlist based on the loved "
                    "tracks of the provided Last.fm username."
                )
                sys.exit(ERROR_INVALID_LASTFM_ARGUMENTS)

            lms = LMSClient(
                host=server_name,
                port=(
                    server_port
                    if server_port
                    else DEFAULT_CONFIG.get("server").get("port")
                ),
                default_player_id=player_id,
            )
            lms.connect(username, password)
            lastfm.loved_tracks_to_playlist(lms, lastfm_username)
            sys.exit(0)

        # Playlist mode.
        if args[0] == "playlist":
            if not player_id:
                print(
                    "You must specify the player ID (`-b`, `--player_id`) "
                    "option to get a playlist."
                )
                sys.exit(ERROR_MANDATORY_OPTIONS_MISSING)
            lms = LMSClient(
                host=server_name,
                port=(
                    server_port
                    if server_port
                    else DEFAULT_CONFIG.get("server").get("port")
                ),
                default_player_id=player_id,
            )
            lms.connect(username, password)
            current_track = lms.get_current_track_playlist_index()
            current_playlist_tracks = lms.get_current_playlist_tracks()
            longest_track = max(
                [t.get("duration") for t in current_playlist_tracks]
            )
            is_playing = lms.get_now_playing().get("mode") == "play"
            print()
            print("Playlist of {}:".format(lms.get_player_name()))
            print()
            for t in current_playlist_tracks:
                if t:
                    print("[{}] {} {}".format(
                        format_time(t.get("duration"), longest_track),
                        (
                            ("♪" if is_playing else "=")
                            if t.get("playlist index") == current_track
                            else "·"
                        ),
                        t.get("title"),
                    ))
            print()
            exit(0)

        # Random mode
        if args[0] == "random":
            if len(args) != 2:
                print(
                    "random mode takes exactly 2 argument (including the "
                    '"random" argument).'
                )
                print("Like this: cursebox random <type>")
                print("You provided {} argument(s).".format(len(args)))
                sys.exit(ERROR_INVALID_RANDOM_ARGUMENTS)

            random_type = args[1]

            if random_type != "album":
                print('Unknown random type "{}".'.format(random_type))
                print("Available types are:")
                print("  album    Play a random album.")
                sys.exit(ERROR_INVALID_RANDOM_ARGUMENTS)

            lms = LMSClient(
                host=server_name,
                port=(
                    server_port
                    if server_port
                    else DEFAULT_CONFIG.get("server").get("port")
                ),
                default_player_id=player_id,
            )
            lms.connect(username, password)
            album = lms.get_random_album()
            lms.load_item_by_type_and_id(
                lms.ITEM_TYPE_ALBUM, album.get("id")
            )
            current_playlist_tracks = lms.get_current_playlist_tracks()
            artists = (set([t.get("artist") for t in current_playlist_tracks]))
            track_count = len(current_playlist_tracks)
            print('Playing album "{}" by {} ({} track{})'.format(
                album.get("album"),
                ", ".join(artists),
                track_count,
                "" if track_count == 1 else "s",
            ))
            sys.exit(0)

    # Default mode: Run cursebox.
    curses.wrapper(
        start_cursebox,
        server_name,
        server_port,
        username,
        password,
        player_id,
        config_check_version,
    )


if __name__ == "__main__":
    main()
