# Cursebox

_A TUI for Lyrion Music Server. Squeezeboxes at your fingertips!_

![Screenshot of what Cursebox looks like](screenshot.png)


## Motivation

The year is 2017, and time is ripe for a terminal interface (TUI) for
controlling the excellent, but unfortunately discontinued, range of
Squeezeboxes by Logitech (and before that, Slimdevices).

Despite the fact that
[the product line](https://en.wikipedia.org/wiki/Squeezebox_(network_music_player))
was officially killed by Logitech in 2012, the ecosystem still lives on,
stronger than ever. Various soft- and hardware projects for the ecosystem are
actively being developed, which truly emphasises the beauty and brilliance of
both the Squeezebox/LMS ecosystem in particular, and open source in general.

These days, software Squeezeboxes run on virtually any hardware available
capable of playing audio. Various programs and apps for easy control of
Squeezeboxes exist for almost any platform you can think of... Except for one
important but neglected platform: **The terminal**.

In October 2016, the **Cursebox** team set out on a mission to correct this
neglect and provide the terminal interface for Squeezeboxes we have all needed
for so many years.


## What does it do?

**Cursebox** is an interactive utility that allows you to control your
Squeezeboxes from the terminal. Building on top of the telnet interface
provided by the Lyrion Media Server (previously known as Logitech Media
Server), **Cursebox** makes searching, playing and queueing music from your
library a breeze. Playing your favorite songs is only a few keystrokes away,
thanks to the intuitive, keyboard-only, vi-like navigation provided
by **Cursebox**.

Simply launch **Cursebox**, type `/a` to search for an **a**lbum, then type
the first letters of the name of an album, `Tab` through the find-as-you-type
search results until the right album is highligted, press `Enter`, press `p`
and the album instantly starts **p**laying on your Squeezebox. All this can be
done in a matter of seconds. No more having to navigate to the web interface of
LMS to find your music by clicking around. Never again will you have the need
to find your Squeezebox control app of choice on your smartphone and tap
through menus and options.

Do you want to change the volume level? Use familiar `j`/`k` keys to de- and
increase the volume level. Or press `v` to go to the dedicated volume control
screen and simply press a number to change the volume level to any multiple
of 10%.

Pressing `space` toggles play/pause, and `p` gives you access to your current
playlist, in case you want to skip to another track.

And so on... It's all there at your fingertips, a few keystrokes away, right
at home, in the terminal.


### Features

 * Now playing overview.
 * Play/pause.
 * De- and increase volume level.
 * Navigate and manage current playlist.
 * Select which player to control.
 * Search for music (artists, albums, tracks).
 * Queue or play items.
 * List favorites.
 * List new music.
 * Toggle Repeat and Shuffle states.
 * Play random album.
 * Special modes:
   * Print the current playlist.
   * Build a playlist of loved tracks from a Last.fm user.
   * Interactive Python mode (LMS CLI shell).
   * Tailing all activity on LMS.


## The future

Currently, **Cursebox** has a somewhat basic (although slowly expanding) set of
features. There are still lots of things that would be nice to implement. But
it all takes time, and the **Cursebox** team decided to release early, with
support for the most often used features, rather than keeping this
fundamentally useful utility in the dark for ourselves.

We still have a daunting journey ahead of us, implementing further features.
But we also have the guts to take on the responsibility and turn our (and your)
dreams into reality.


## Installation and basic usage

Cursebox is [available from PyPI](https://pypi.python.org/pypi/cursebox). As
it's is written in Python, it's an advantage if you're familiar with how
Python works. Being a terminal application, thus having a somewhat tech savvy
target audience, we hope you're able to acquire the required knowledge about
Python if you don't already possess it.

You may install Cursebox globally, but it's recommended to create
a virtual environment for it.

Simply run `pip install cursebox`. Afterwards, a `cursebox` command should be
available to you. Run `cursebox --help` to see your options (see below).

If you feel a bit more adventurous, clone the repository to a location of your
own choice. Then run `./cursebox.py --help` (again, it's recommended to create
a virtual environment for Cursebox) to see your options:

```
usage: cursebox [-h] [-c CONFIG] [-s SERVER] [-p PORT] [-u USERNAME]
                [-P PASSWORD] [-b PLAYER_ID] [-v VERSION]
                [--logging-level LOGGING_LEVEL] [-V] [-v2]
                [{create-config,playlist,random,interactive,tail}]

A TUI for Lyrion Music Server. Squeezeboxes at your fingertips!

positional arguments:
  {create-config,playlist,random,interactive,tail}
                        Perform a specific action witout launching Cursebox.

options:
  -h, --help            show this help message and exit
  -c, --config CONFIG   Path to configuration file. Optional. Default
                        location is ~/.cursebox.conf
  -s, --server SERVER   Hostname of the Lyrion Music Server to connect to.
  -p, --port PORT       Port number of the Lyrion Music Server to connect to.
                        Optional, defaults to 9090.
  -u, --username USERNAME
                        Username used for authentication with Lyrion Music
                        Server. Optional.
  -P, --password PASSWORD
                        Password used for authentication with Lyrion Music
                        Server. Optional.
  -b, --player_id PLAYER_ID
                        ID (MAC address) of the Squeezebox to connect to.
                        Optional.
  -v, --version VERSION
                        Print the Cursebox version.
  --logging-level LOGGING_LEVEL
                        Set the logging level.
  -V, --check_version   Check online, during startup, whether a newer version
                        is available. Optional -- no check is done by
                        default. Not for the paranoid, as an HTTPS request to
                        pypi.python.org (which is usually also where Cursebox
                        is installed from) is done if this is enabled.
  -v2                   Launch Cursebox version 2 (experimental).

Prodiving no arguments will simply launch Cursebox (requires a configuration
file in the default location).
```

It is strongly advised to create a configuration file with your static settings
and, optionally, an `alias` that will run the script with the correct options
for you if any of these are dynamic (e.g. `player_id` based on your location)
or secret (e.g. `password`), to make everything even more smooth and easy.


## Upgrading

Run `pip install --upgrade cursebox` to get the most recent version
of **Cursebox**. Bugs are fixed and new features added along the way. So it's
a good idea to keep your **Cursebox** updated (as with any other software), to
be sure you're not missing out on something invaluable to you.


## `cursebox-ssh-server`

Cursebox also comes prepackaged as
[a Docker container image with an SSH server](https://git.data.coop/gorgonzo.la/cursebox-ssh-server).
If you're an SSH networking terminal wizard, this may be something for you!
