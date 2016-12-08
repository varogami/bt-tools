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
import module

class Func:
    def __init__(self, color, modules, debug = False):
        self.color = color
        self.modules = modules
        self.__debug = debug

    def build_item(self, row):
        item = module.Item()
        item.id = row[0]
        item.module = row[1]
        item.link_module = row[2]
        item.id_module = row[3]
        item.name = row[4]
        item.link = row[5]
        item.idate = row[6]
        item.type = row[7]
        item.size = row[8]
        item.date = row[9]
        item.leech = row[10]
        item.seed = row[11]
        item.compl = row[12]
        item.magnet = row[13]
        item.torrent_link = row[14]
        item.hashvalue = row[15]
        item.data = row[16]
        item.html = row[17]
        return item
    
    def __isMode(self, value):
        result = False
        if value == "m1":
            result = True
        return result

    def print_item(self, id, i, config, mod):
        self.__print_item(id, i.name, self.getCategory(config, i.type, mod), i.leech, i.seed, i.compl, i.get_human_size())

    def print_item_db(self, row, config):
        i = self.build_item(row)
        cat = i.module + " | " + self.getCategory(config, i.type, i.module)
        self.__print_item( str(i.id), i.name, cat, str(i.leech), str(i.seed), str(i.compl), i.get_human_size() )

    def print_item_db_detail(self, row, config):
        i = self.build_item(row)
        cat = self.getCategory(config, i.type, i.module)
        print self.color.magenta + i.name + self.color.base
        self.__print_item_attribute("id", str(i.id))
        self.__print_item_attribute("module", i.module)
        self.__print_item_attribute("category", cat)
        self.__print_item_attribute("leech", str(i.leech))
        self.__print_item_attribute("seed", str(i.seed))
        self.__print_item_attribute("completed", str(i.compl))
        self.__print_item_attribute("size", i.get_human_size())
        self.__print_item_attribute("url_module", i.link_module)
        self.__print_item_attribute("id_module", str(i.id_module))
        self.__print_item_attribute("url_item", i.link)
        self.__print_item_attribute("inserted_date", str(i.idate))
        self.__print_item_attribute("torrent_date", str(i.date))
        self.__print_item_attribute("magnet", i.magnet)
        self.__print_item_attribute("url_torrent", i.torrent_link)
        self.__print_item_attribute("hash", i.hashvalue)
        
        if i.data is None:
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

    def get_item(self, db, id):
        return self.build_item(self.__get_item(db, id))

    def update_item(self, db, conf, json, id):
        i = self.get_item(db, id)
        engine = conf.load_mod(i.module, json['module'][i.module], conf.getLogDir(), json['user_agent'])
        final_item = engine.get_detail_data(i)
        db.update_item(final_item)
    
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

 
