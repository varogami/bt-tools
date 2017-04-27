# bt-tools
tools to interact with some bittorrent sites and show result (conky, command line, ncurses and others front end in the future).
Thought to low resource system and safe datastore when torrent site closed, (have only a one database for all).


## install
Before to use it needs of python beautifulsoup, urllib and feedparser modules.
Clone the git and copy al directory on your prefer path. Then edit config.bash and config.py with your new path and config.py with your preferences.

## Search Tools
**bt-search**    command line to search bittorrent from some website

**bt-download**  command line to download result of bt-search or downloaded feed

## Rss Tools
**bt-rss**       get data of rss feed from torrent website


## Conky Tools
**bt-conky**     generate conky code of bittorrent new item from database

see **conky.conf** example to use it


## Misc Tools
**bt-info**      show details of single torrent (get it from bt-search or downloaded feed)

**bt-utils**     other utils
