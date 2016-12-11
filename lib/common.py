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
    def __init__(self, config):
        self.color = config.getColors()
        self.__conf = config
        self.__json = config.getJson()
        self.__db = config.getDb()
        self.__debug = config.getDebug()
        
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
    
    def print_item(self, id, i, mod_config):
        self.__print_item(id, i.name, self.getCategory(mod_config, i.type), i.leech, i.seed, i.compl, i.get_human_size())

    def print_item_db(self, row, mod_config):
        i = self.build_item(row)
        cat = i.module + " | " + self.getCategory(mod_config, i.type)
        self.__print_item( str(i.id), i.name, cat, str(i.leech), str(i.seed), str(i.compl), i.get_human_size() )

    def print_item_db_detail(self, i, config):
        cat = self.getCategory(config, i.type)
        print self.color.magenta + i.name + self.color.base
        self.__print_item_attribute("id", str(i.id))
        self.__print_item_attribute("module", i.module)
        self.__print_item_attribute("category", cat)
        self.__print_item_attribute("leech", str(i.leech))
        self.__print_item_attribute("seed", str(i.seed))
        self.__print_item_attribute("completed", str(i.compl))
        self.__print_item_attribute("size", i.get_human_size())
        self.__print_item_attribute("link_module", i.link_module)
        self.__print_item_attribute("id_module", str(i.id_module))
        self.__print_item_attribute("link", i.link)
        self.__print_item_attribute("inserted_date", str(i.idate))
        self.__print_item_attribute("date", str(i.date))
        self.__print_item_attribute("magnet", i.magnet)
        self.__print_item_attribute("torrent_link", i.torrent_link)
        self.__print_item_attribute("hashvalue", i.hashvalue)
        
        if i.data is None:
            self.__print_item_attribute("extra_info", "not present")
        else:
            self.__print_item_attribute("extra_info", "present")
            
        if i.html is None:
            self.__print_item_attribute("html", "not present")
        else:
            self.__print_item_attribute("html", "present")
        
    def __print_item(self, id_item, name, category, leech, seed, completed, size):
        limit = self.__json["output_string_limit"]
        if len(name) > limit:
            trunk_name = name[:limit] + "..."
        else:
            trunk_name = name
        print self.color.magenta + str(id_item) + " | " + category + \
            self.color.base + " " + trunk_name + \
            self.color.yellow  + "  " + "[l" + str(leech) + " s" + str(seed) + " c" + str(completed) + "] " + size + self.color.base
        
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
        for name in self.__conf.module.list:
            if self.__conf.module.loadConf(name):
                module_config = self.__conf.module.getJson()
                for key, value in module_config['cats'].iteritems():
                    if key in listcat:
                        oldkey = listcat[key]
                        listcat[key] = oldkey + " " + name
                    else:
                        listcatsorted.append(key)
                        listcat[key] = name

        #sort list
        listcatsorted.sort()

        #print list
        COUNT=0
        for i in listcatsorted:
            print i + ": " + self.color.blu + listcat[i] + self.color.base
            COUNT = COUNT+1
        print
        print "total number of category:" + str(COUNT)

    def getCategory(self, config, category):
        cats = config['cats']
        for name, external_category in cats.iteritems():
            if external_category == category:
                return name
                    
    def __get_item(self, id):
        try:
            val = int(id)
            result = self.__db.get_item(id)
            if result is None:
                self.print_error("\"" + id + "\" not found")
            return result
        except ValueError:
            self.print_error("\"" + id + "\" not is number")
            return None

    def __launch_client(self, url):
        print self.color.cyan + "launching:"
        limit = self.__json["output_string_limit"]
        client = self.__json["torrent_client"] 
        print  client + " " + url[:limit] + "..." + self.color.base
        subprocess.call([client, url])
        #fix a bug with qbittorrent
        time.sleep(5)
        print        
        
    def __download(self, item):
        if item.magnet is not None:
            self.__launch_client(item.magnet)
            return True
        elif item.torrent_link is not None:
            self.__launch_client(item.torrent_link)
            return True
        else:
            return False

    def __isMode(self, value):
        result = False
        if value == "hash":
            result = True
        return result        
        
    def download(self, id, mode):
        if self.__isMode(mode):
            if id != mode:
                if mode == "hash":
                    pass
        else:
            item = self.get_item(id)                    
            if item is not None:
                mod_json = self.__conf.module.getModJson(item.module)
                self.print_item(id, item, mod_json)
                if not self.__download(item):
                    up_result = self.update_item(id)
                    self.__download(up_result)
                    
                
    def info(self, id):
        item = self.get_item(id)
        mod_json = self.__conf.module.getModJson(item.module)
        if item is not None:
            self.print_item_db_detail(item, mod_json)

    def get_item(self, id):
        return self.build_item(self.__get_item(id))

    def update_item(self, id):
        i = self.get_item(id)
        mod_json = self.__conf.module.getModJson(i.module)
        engine = self.__conf.load_mod(i.module, mod_json)
        final_item = engine.get_detail_data(i)
        self.__db.update_item(final_item)
        return final_item
    
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

 
