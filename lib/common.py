#! /usr/bin/python
# -*- coding=utf-8 -*-

#bt-tools - tools to interact with some bittorrent sites by commandline
#Copyright (C) 2015-2016 varogami <varogami@altervista.org>

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

import subprocess, time
import utils

class Item:
    def __init__(self, row, debug = False):
        self.category = row[7]
        self.name = row[4]
        self.id = row[0]
        self.module = row[1]
        self.leech = row[10]
        self.seed = row[11]
        self.completed = row[12]
        self.size = row[8]
        self.url_module = row[2]
        self.id_module = row[3]
        self.url_item = row[5]
        self.inserted_date = row[6]
        self.torrent_date = row[9]
        self.magnet = row[13]
        self.url_torrent = row[14]
        self.hash = row[15]
        self.extra_info = row[16]
        self.html = row[17]

class Func:
    def __init__(self, color, modules, debug = False):
        self.color = color
        self.modules = modules
        self.__debug = debug

    def __isMode(self, value):
        result = False
        if value == "m1":
            result = True
        return result


    def print_item(self, id, i, config, mod):
        self.__print_item(id, i.name, self.getCategory(config, i.type, mod), i.leech, i.seed, i.compl, i.get_human_size())

    def print_item_db(self, row, config):
        size = utils.sizeof(row[8])
        cat = row[1] + " | " + self.getCategory(config, row[7], row[1])
        self.__print_item( str(row[0]), row[4], cat, str(row[10]), str(row[11]), str(row[12]), size )
        

    def print_item_db_detail(self, row, config):
        i = Item(row)
        size = utils.sizeof(i.size)
        cat = self.getCategory(config, i.category, i.module)
        print self.color.magenta + i.name + self.color.base
        self.__print_item_attribute("id", str(i.id))
        self.__print_item_attribute("module", i.module)
        self.__print_item_attribute("category", cat)
        self.__print_item_attribute("leech", str(i.leech))
        self.__print_item_attribute("seed", str(i.seed))
        self.__print_item_attribute("completed", str(i.completed))
        self.__print_item_attribute("size", size)
        self.__print_item_attribute("url_module", i.url_module)
        self.__print_item_attribute("id_module", str(i.id_module))
        self.__print_item_attribute("url_item", i.url_item)
        self.__print_item_attribute("inserted_date", str(i.inserted_date))
        self.__print_item_attribute("torrent_date", str(i.torrent_date))
        self.__print_item_attribute("magnet", i.magnet)
        self.__print_item_attribute("url_torrent", i.url_torrent)
        self.__print_item_attribute("hash", i.hash)
        
        if i.extra_info is None:
            self.__print_item_attribute("extra_info", "not present")
        else:
            self.__print_item_attribute("extra_info", "present")
            
        if i.html is None:
            self.__print_item_attribute("html", "not present")
        else:
            self.__print_item_attribute("html", "present")
            
        
    def __print_item(self, id_item, name, category, leech, seed, completed, size):
        print self.color.magenta + str(id_item) + " | " + category + \
            self.color.base + " " + name + \
            self.color.yellow  + "  " + "[l" + leech + " s" + seed + " c" + completed + "] " + size + self.color.base
        
    def __print_item_attribute(self, name, value):
        print self.color.yellow + name + ": " + self.color.base + str(value)
                                           
    def print_error(self, string):
        print self.color.red + string + self.color.base
                           
    def print_warning(self, string):
        print self.color.yellow + string + self.color.base

    def lscat(self):
        listcat = {}
        listcatsorted = []
        #build list
        for mod, obj in self.modules.iteritems():
            for key, value in obj['cats'].iteritems():
                if key in listcat:
                    oldkey = listcat[key]
                    listcat[key] = oldkey + " " + mod
                else:
                    listcatsorted.append(key)
                    listcat[key] = mod

        #sort list
        listcatsorted.sort()

        #print list
        COUNT=0
        for i in listcatsorted:
            print i + ": " + self.color.blu + listcat[i] + self.color.base
            COUNT = COUNT+1
        print
        print "total number of category:" + str(COUNT)

    def getCategory(self, config, category, mod):
        cats = config['module'][mod]['cats']
        for name, external_category in cats.iteritems():
            if external_category == category:
                return name
        
    def __launch_client(self, result, config):
        print self.color.cyan + "launching:"
        #url[:config["output_string_limit"]]
        print config["torrent_client"] + " " + "test" + "..." + self.color.base
        #subprocess.call([config["torrent_client"], "test"])
        #fix a bug with qbittorrent
        time.sleep(5)
        print
        
    def __get_item(self, db, id):
        try:
            val = int(id)
            result = db.get_item(id)
            if result is None:
                self.print_error("\"" + id + "\" not found")
            return result
        except ValueError:
            self.print_error("\"" + id + "\" not is number")
            return None

    def download(self, config, db, id, mode):
        if self.__isMode(mode):
            if id != mode:
                if mode == "m1":
                    result = self.__get_item(db, id)
                    if result is not None:
                        self.print_item_db(result, config)
                        self.__launch_client(result, config)
        else:
            result = self.__get_item(db, id)                    
            if result is not None:
                self.print_item_db(result, config)
                self.__launch_client(result, config)
    def info(self, config, db, id):
        result = self.__get_item(db, id)
        if result is not None:
            self.print_item_db_detail(result, config)

    def get_item_url(self, db, id):
        i = Item(self.__get_item(db, id))
        return i.url_item

    def get_item_mod(self, db, id):
        i = Item(self.__get_item(db, id))
        return i.module

    def update_item(self, db, item, id):
        item.id = id
        db.update_item(item)
    
    def getRss(self, cat, modname):
        engine = self.engines[modname]
        engine.getFeed(cat)
        self.data.insert(engine, "rss", True, not engine.rss_light_download )
        if config.rss_daemon_download_filtered:
            items_to_download = self.data.filter(engine, cat, True)
            if not items_to_download == None:
                for item in items_to_download:
                    if not config.filter_download_file_only:
                        self.download(engine.shortname + "-" + item.id) #not efficent way - but less code
                    else:
                        file_got = engine.get_torrent_file(item, config.download_dir)
                        self.data.add_item_to_filter_coda(item)
                        #if not file_got: # check if downloaded torrent successful
                        #    self.data.add_item_to_filter_coda(item)


    def makeRss(self, cat, modname):
        self.data.exportRssByXml(self.engines[modname], cat)

 
