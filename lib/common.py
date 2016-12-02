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

class Func:
    def __init__(self, color, modules, debug = False):
        self.color = color
        self.modules = modules
        self.__debug = debug

    def isMode(self, value):
        result = False
        if value == "m1":
            result = True
        if value == "m2":
            result = True
        if value == "m3":
            result = True
        return result
        
                                           
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

    def _launch_client(self, url):
        print config.color_cyan + "launching:"
        print self.client + " " + url[:config.output_string_limit] + "..." + config.color_base
        subprocess.call([self.client, url])

    def old_get(self, id):
        self.data.load()
        website,trueid = id.split("-")
        isValidType = False
        
        #find element's engine
        for engine in self.engines.values():
            if website == engine.shortname:
                isValidType = True
                #get element's data by database
                datalist = self.data.getList(engine.name)
                item = datalist.getItem(trueid)
                voiditem = engine.makeVoidItem()
                downloaded_info= {}

                if not item.isVoid():
                    if self.__debug:
                        #print first fields
                        print \
                            config.color_yellow + item.getAttr('id') + \
                            config.color_blu + "/" + \
                            config.color_yellow + item.getAttr('src') + \
                            config.color_blu + "/" + \
                            config.color_yellow + item.getAttr('type') + \
                            config.color_blu + "         inserted on db: " + \
                            config.color_yellow + item.getAttr('date') + \
                            config.color_base

                    #get remaining data
                    magnet = item.getKey("magnet")
                    torrent = item.getKey("torrent-link")
                    bt_link_alt1 = item.getKey("torrent-link-alt1")
                    bt_link_alt2 = item.getKey("torrent-link-alt2")
                    hash = item.getKey("hashvalue")
                    
                    #check if data have valid elements else get by internet
                    if magnet.isVoid() and torrent.isVoid() and bt_link_alt1.isVoid() and bt_link_alt2.isVoid() and hash.isVoid():
                        link = item.getKey("link").getTxt()
                        voiditem.link = link
                        engine.get_detail_data(voiditem)
                        date = item.getKey("date")
                        url_alt1 = None
                        url_alt2 = None
                        gen_magnet = None
                        
                        #set hash if have it by internet  - add on db
                        if not voiditem.hashvalue == None:
                            newhash = item.addKey("hashvalue",voiditem.hashvalue)
                            downloaded_info["hashvalue"] = voiditem.hashvalue
                            gen_magnet = utils.get_mag_by_hash(voiditem.hashvalue)
                            url_alt1 = utils.get_url_by_hash(voiditem.hashvalue, utils.link_torcache)
                            url_alt2 = utils.get_url_by_hash(voiditem.hashvalue, utils.link_zoink)
                        else:
                            downloaded_info["hashvalue"] = None

                        #set magnet on db and output dict
                        if not voiditem.magnet == None:
                            downloaded_info["magnet"] = voiditem.magnet
                        else:
                            downloaded_info["magnet"] = gen_magnet
              
                        if not downloaded_info["magnet"] == None:
                            newmagnet = item.addKey("magnet",downloaded_info["magnet"])

                        #set torrent link on db and output dict
                        if not voiditem.torrent_link == None:
                            newtorrent = item.addKey("torrent-link",voiditem.torrent_link)
                            downloaded_info["torrent-link"] = voiditem.torrent_link
                        else:
                            downloaded_info["torrent-link"] = None
 
                        #set torcache and zoink link
                        if not url_alt1 == None:
                            newtorrent_alt1 = item.addKey("torrent-link-alt1",url_alt1)
                            downloaded_info["torrent-link-alt1"] = url_alt1

                        if not url_alt2 == None:
                            newtorrent_alt2 = item.addKey("torrent-link-alt2",url_alt2)
                            downloaded_info["torrent-link-alt2"] = url_alt2
                            
                        if date.isVoid():
                            if not voiditem.date==None:
                                newdate = item.addKey("date",voiditem.date)

                        downloaded_info["link"] = link

                        if verbose:
                            #print remaining data
                            for i in item.elem:
                                if i.attrib['name'] == "size":
                                    print config.color_blu + i.attrib['name'].encode('utf8') + ": " + config.color_base + utils.sizeof(int(i.text))
                                else:
                                    print config.color_blu + i.attrib['name'].encode('utf8') + ": " + config.color_base + i.text
                        else:
                            print item.getKey("name").getTxt()
                            
                        #write new data got by internet
                        self.data.write()
                    else:
                        if verbose:
                            #if item have magnet or torrent file get and print all
                            for i in item.elem:
                                if i.attrib['name'] == "size":
                                    print config.color_blu + i.attrib['name'].encode('utf8') + ": " + config.color_base + utils.sizeof(int(i.text))
                                else:
                                    print config.color_blu + i.attrib['name'].encode('utf8') + ": " + config.color_base + i.text
                        else:
                            print item.getKey("name").getTxt()
                            
                        link = item.getKey("link")

                        if not magnet.key == None:
                            downloaded_info["magnet"] = magnet.getTxt()
                        else:
                            downloaded_info["magnet"] = None

                        if not torrent.key == None:
                            downloaded_info["torrent-link"] = torrent.getTxt()
                        else:
                            downloaded_info["torrent-link"] = None

                        if not hash.key == None:
                            downloaded_info["hashvalue"] = hash.getTxt()
                        else:
                            downloaded_info["hashvalue"] = None
        
                        if not bt_link_alt1.key == None:
                            downloaded_info["torrent-link-alt1"] = bt_link_alt1.getTxt()
                        else:
                            downloaded_info["torrent-link-alt1"] = None

                        if not bt_link_alt2.key == None:
                            downloaded_info["torrent-link-alt2"] = bt_link_alt1.getTxt()
                        else:
                            downloaded_info["torrent-link-alt2"] = None
                            
                        downloaded_info["link"] = link.getTxt()
                else:
                    self.print_error("not found id \"" + id + "\"")
                return downloaded_info
        if not isValidType:
           self.print_error("not valid website code \"" + website + "\"")

    def old_download(self, id):
        #download, add items on database and generate link by hash if exist
        dwinfo = self.get(id, False)

        #to get torrent-link first
        if dwinfo["torrent-link"] == None:
            self.print_warning("warning: no torrent link")
        else:
            self._launch_client(dwinfo["torrent-link"])
            #fix a bug with qbittorrent - magnet substitute torrent info - if magnet not have info clean info on download
            time.sleep(5)

        for key, url in dwinfo.items():
            if not key == "link":
                if not key == "hashvalue":
                    if not key == "torrent-link":
                        if url == None:
                            self.print_warning("warning: no " + key + " link")
                        else:
                            self._launch_client(url)
                            #bug qbittorrent
                            time.sleep(5)
    def download(self, id, mode = None):
        if mode is None:
            print "get id:" + str(id)
        else:
            if mode == "m1":
                print "get with m1 way id:" + str(id)
