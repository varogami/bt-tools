# bt-tools
tools to interact with some bittorrent sites and show result (conky, command line, ncurses and others front end in the future).
Thought to low resource system and like safe database when torrent site close, (have only a one database to feed and search result).


## install
Clone the git and copy al directory on your prefer path. Then edit config.bash and config.py with your new path and config.py with your preferences.

## Search Tools
**bt-search**    command line to search bittorrent on some site ( for now tntvillage.org, ilcorsaronero.info, btdigg.org and kickasstorrent)

## Rss Tools
**bt-rss-fix**            build rss usable by bittorrent client from site that not have rss or rss not work with client (for now work only with ilcorsaronero.info)

**bt-rss-daemon**         daemon of bt-rss-fix or bt-daemon-core

**bt-rss-daemon-core**    daemon for build your own rss feed by downloaded 

## Conky Tools
**bt-conky**            generate conky code from rss downloaded with rss tools

**bt-conky-daemon**     daemon to update feed

see **conky.conf** example to use it


## Misc Tools
**bt-download**  command line to download result of bt-search or downloaded feed

**bt-info**      show details of single torrent (get it from bt-search or downloaded feed)

**bt-utils**     other utils
