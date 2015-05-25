#bt-tools - tools to interact with some bittorrent sites by commandline
#Copyright (C) 2015  varogami

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.



basedir = "/SCRIPTS/PATH"
dbfile = basedir + "/tmp/database.xml"
rssdir = basedir + "/rss/"
export_file = basedir + "/tmp/database-pretty.xml"
logdir = basedir + "/log/"
client = "qbittorrent-nox"

#modules username and password list
usernames = {
    "tnt":"YOUR USERNAME"
    }
passwords = {
    "tnt":"YOUR PASSWORD"
    }

#conky settings
conky_categories = ["anime", "film", "serie"]
conky_sites_to_show = [ 0, 4 ]
conky_chars_to_print = 90
conky_rows_to_print = 6

#rss-fix settings
rss_fix_get_list = {
    '4': ['anime', 'film', 'film-screen', 'film-dvd', 'serie', 'book-e', 'book-a']
    }
rss_fix_make_list = {
    '4': ['anime', 'film', 'serie', 'book' ]
    }

#rss-daemon settings - needed to use with conk
rss_daemon_get_list = {
    '4': ['anime', 'film', 'film-screen', 'film-dvd', 'serie', 'book-e', 'book-a'],
    '0': ['anime', 'film', 'serie']
    }
    
#rss_daemon_make_list = {
#    '4': ['anime', 'film', 'serie', 'book' ],
#    }
     
debug = False

mods_enabled = {
    "tnt":"true",
    "icn":"true",
    "kck":"true",
    "btdigg":"true"
    }

##DO NOT EDIT IF YOU DON'T KNOW WHAT DO
#colors for shell
search_C01 = '\033[95m'
search_C02 = '\033[94m'
search_C03 = '\033[92m'
search_C04 = '\033[93m'
search_C05 = '\033[91m'
search_CEND = '\033[0m'
xml_C03 = '\033[92m'
xml_CEND = '\033[0m'
#change name of categories
categories_change = {
    "all":"all",
    "film":"film",
    "film-dvd":"film",
    "film-screen":"film",
    "anime":"anime",
    "serie":"serie",
    "apps-linux":"apps",
    "apps":"apps",
    "musica":"musica",
    "book-a":"book",
    "book-e":"book",
    "cartoni":"anime",
    "fumetti":"book",
    "teatro":"film",
    "documentari":"film",
    "giochi":"apps"
}

    
#load modules from "modules" dir - DO NOT EDIT
import sys, os
moddir = basedir + '/modules'
sys.path.append(moddir)
engines = []

for f in os.listdir(moddir):
    if os.path.isfile(os.path.join(moddir,f)):
        if f.endswith('.py'):
            modname = f.replace('.py','')
            module = __import__(modname)
            if modname == 'base': 
                engines.append(module.BaseData())
                base = module
            else:
                try:
                    enabled = mods_enabled[modname]
                except:
                    enabled = "true"
                if enabled == "true": 
                    if module.use_pwd:
                        try:
                            usr = usernames[modname]
                            pwd = passwords[modname]
                            engines.append(module.Data(usr,pwd))
                        except:
                            print "error - not found username/password or erron on module " + modname
                    else:
                        engines.append(module.Data())
            

#utils
class tools:
    def search_words_casei(self, seek, string):
        return base.search_words_casei(seek, string)
    def sizeof(self,num):
        return base.sizeof(num)
