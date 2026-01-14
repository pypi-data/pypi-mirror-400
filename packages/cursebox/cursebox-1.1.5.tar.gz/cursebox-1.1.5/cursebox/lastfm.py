#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Last.fm lulz for Cursebox."""

import copy
import json
import os
from random import shuffle
import time
from urllib import parse, request


# Define the basics for Last.fm API requests.
BASE_URL = "https://ws.audioscrobbler.com/2.0/"
DEFAULT_PARAMS = {
    "format": "json",
    "api_key": "855c88c650ba9f4a2757ba3063799633",
}

def get_lms_track(lms, lfm_track):
    """Find the correct track in LMS library, if it exists."""
    lms_tracks = [
        t for t in
        lms.search(lfm_track.get("name")).get(lms.ITEM_TYPE_TRACK)
        if t[1] == lfm_track.get("name")
    ]
    for t in lms_tracks:
        track_data = lms.get_track_details(t[0])
        if track_data.get("artist") == lfm_track.get("artist").get("name"):
            return t
    return None

def loved_tracks_to_playlist(lms, username):
    """
    Get loved tracks from Last.fm and create a playlist from them.

    Or at least try. It may not be possible to find all tracks in the
    LMS library.
    """

    # Get a copy of the default params and modify them for loved tracks.
    params = copy.copy(DEFAULT_PARAMS)
    params.update({
        "method": "user.getlovedtracks",
        "user": username,
        "limit": 1,
    })

    print("Gettings loved tracks from Last.fm...")

    # Get a single track, to know the total.
    response = request.urlopen("{}?{}".format(
        BASE_URL,
        parse.urlencode(params),
    ))

    # Extract the total.
    total = json.loads(
        response.read()
    ).get("lovedtracks").get("@attr").get("total")
    params.update({"limit": int(total)})

    # Get all tracks.
    response = request.urlopen("{}?{}".format(
        BASE_URL,
        parse.urlencode(params),
    ))
    data = json.loads(response.read())

    print("Found {} loved tracks on Last.fm.".format(total))
    print("Looking up tracks in LMS library:")

    # Iterate over tracks to see if they are in the LMS library.
    pos = 0
    found = 0
    lfm_tracks = data.get("lovedtracks").get("track")
    shuffle(lfm_tracks)
    for t in lfm_tracks:
        pos += 1
        print("Looking for {}/{}: {} by {}...".format(
            pos,
            total,
            t.get("name"),
            t.get("artist").get("name"))
        )
        lms_track = get_lms_track(lms, t)
        if pos == 1:
            lms.clear_playlist()
        if lms_track is not None:
            print("Found!")
            found += 1
            lms.add_track_by_id(lms_track[0])
        if found == 1:
            lms.play_pause()
        else:
            print("Not found :(")

    print()
    print("Found {} of {} loved tracks in LMS library.".format(
        found,
        total,
    ))

    print()
    print()
    print()
    print("     ******************************")
    print("     * ♪ Now, get up and dance! ♪ *")
    print("     ******************************")
    print()
    time.sleep(2.5)
    print("                    Brought to you by...")
    print()

    with open(
        os.path.join(os.path.dirname(__file__), "./resources/logo.txt")
    ) as f:
        logo_lines = f.readlines()
    for l in logo_lines:
        print("{}".format(l.rstrip()))

    print()
    print()
