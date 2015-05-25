#! /usr/bin/python
# -*- coding=utf-8 -*-

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

import sys, xml, config


class CLI:
    def __init__(self):
        self.client = config.client
        self.data = xml.Data()
        self.engines = config.engines

    def Search(self, pattern, cat='all'):
        for engine in self.engines:
            engine.search(pattern, cat)
            
            COUNT=len(engine.list)
            
            if COUNT>0:
                print
                print config.search_C02 + engine.shortname + " (" +config.search_C03+ "TOT " + str(COUNT) + config.search_C02 + "):"
                print config.search_C04 + "[" + engine.url + "]" + config.search_CEND
                    
                for i in engine.list:
                    print config.search_C01 + i.id + "  " + config.search_CEND + i.name
                self.data.insert(engine, "search")
                print config.search_C02 + "END "+ engine.shortname +" SEARCH" + config.search_CEND

    def cachedSearch(self, pattern):
        self.data.load()
        for i in self.data.root:
            print
            print config.search_C02 + i.attrib['shortname'].encode('utf8') + config.search_CEND
            for z in i:
                name = z.find("./key[@name]").text
                if config.tools().search_words_casei(pattern,name):
                    print config.search_C01 + z.attrib['id'].encode('utf8') + " " + config.search_CEND + name
            print config.search_C02 + "END "+ i.attrib['shortname'].encode('utf8') +" SEARCH" + config.search_CEND

                    
    def listdb(self):
        self.data.load()
        for i in self.data.root:
            print i.attrib['name'].encode('utf8')
            for z in i:
                name = z.find("./key[@name]").text
                print z.attrib['id'].encode('utf8') + "  " + name
        
    def get(self, id):
        self.data.load()
        type = id.split("-")[0]
        trueid = id.split("-")[1]

        for engine in self.engines:
            if type == engine.shortname:
                datalist = self.data.getList(engine.name)
                item = datalist.getItem(trueid)

                dwinfo= []

                if not item.isVoid():
                    print config.search_C05 + item.getAttr('id') + config.search_C02 + "/" + config.search_C05 + item.getAttr('src') + config.search_C02 + "/" + config.search_C05 + item.getAttr('type') + config.search_CEND
                    magnet = item.getKey("magnet")
                    torrent = item.getKey("torrent-link")
                    
                    if magnet.isVoid() and torrent.isVoid():
                        link = item.getKey("link").getTxt()
                        details = engine.get_detail_data(link)
                        hash = item.getKey("hashvalue")
                        date = item.getKey("date")

                        if date.isVoid():
                            if not details.date==None:
                                newdate = item.addKey("date",details.date)

                        if magnet.isVoid():
                            if not details.magnet==None:
                                newmagnet = item.addKey("magnet",details.magnet)
                                dwinfo.append(details.magnet)
                            else:
                                dwinfo.append(None)
                        else:
                            dwinfo.append(magnet.getTxt())

                        if torrent.isVoid():
                            if not details.torrent_link==None:
                                newtorrent = item.addKey("torrent-link",details.torrent_link)
                                dwinfo.append(details.torrent_link)
                            else:
                                dwinfo.append(None)
                        else:
                            dwinfo.append(torrent.getTxt())

                        if hash.isVoid():
                            if not details.hashvalue==None:
                                newhash = item.addKey("hashvalue",details.hashvalue)
                                dwinfo.append(details.hashvalue)
                            else:
                                dwinfo.append(None)
                        else:
                            dwinfo.append(hash.getTxt())

                        dwinfo.append(link)

                        for i in item.elem:
                            if i.attrib['name'] == "size":
                                print config.search_C02 + i.attrib['name'].encode('utf8') + ": " + config.search_CEND + config.tools().sizeof(int(i.text))
                            else:
                                print config.search_C02 + i.attrib['name'].encode('utf8') + ": " + config.search_CEND + i.text

                        self.data.write()
                    else:
                        for i in item.elem:
                            if i.attrib['name'] == "size":
                                print config.search_C02 + i.attrib['name'].encode('utf8') + ": " + config.search_CEND + config.tools().sizeof(int(i.text))
                            else:
                                print config.search_C02 + i.attrib['name'].encode('utf8') + ": " + config.search_CEND + i.text

                        newmagnet = item.getKey("magnet")
                        newtorrent = item.getKey("torrent-link")
                        newhash = item.getKey("hashvalue")
                        link = item.getKey("link")

                        if not newmagnet.key == None:
                            dwinfo.append(newmagnet.getTxt())
                        else:
                            dwinfo.append(None)

                        if not newtorrent.key == None:
                            dwinfo.append(newtorrent.getTxt())
                        else:
                            dwinfo.append(None)

                        if not newhash.key == None:
                            dwinfo.append(newhash.getTxt())
                        else:
                            dwinfo.append(None)
                        dwinfo.append(link.getTxt())

                return dwinfo

    def download(self, id, way=None):
        import subprocess
        zoink="https://zoink.it/torrent/"
        torcache="http://torcache.net/torrent/"

        dwinfo = self.get(id)
        if way == None:
            if not dwinfo[0] == None:
                url = dwinfo[0]
            elif not dwinfo[1] == None:
                url = dwinfo[1]
            else:
                print "error: no magnet or torrent link"

        elif way == "mag":
            if not dwinfo[0] == None:
                url = dwinfo[0]
            else:
                print "error: no magnet  link"

        elif way == "tor":
            if not dwinfo[1] == None:
                url = dwinfo[1]
            else:
                print "error: no torrent link"

        elif way == "torcache":
            if not dwinfo[2] == None:
                url = torcache + dwinfo[2].upper() + ".torrent"
            else:
                print "error: no hashvalue"

        elif way == "zoink":
            if not dwinfo[2] == None:
                url = zoink + dwinfo[2].upper() + ".torrent"
            else:
                print "error: no hashvalue"
            
        print
        print config.search_C05 + self.client + " " + url + config.search_CEND
        subprocess.call([self.client, url])

    def webpage(self, id):
        import subprocess
        dwinfo = self.get(id)
        subprocess.call(["w3m", dwinfo[3]])
        
    def lscat(self):
        for engine in self.engines:
            engine.lscat()

    def help(self):
        print "search \"words\" - normal search"
        print "  or "
        print "search \"words\" - [cat] normal search in specific category"
        print "csearch \"words\" - search in cached file"
        print "get \"id\" - show details of id (id example ICN-123454)"
        print "web \"id\" - show webpage of id (id example ICN-123454)"
        print "dw \"id\" [mag|tor|torcache|zoink|NULL]- download id (id example ICN-123454)" 
        print "listdb - list db" #todo mettere warning con y/n
        print "export filename - export db in pretty xml"
        print "lscat - list category for engine"


if __name__ == "__main__":
    do = CLI()

    if len(sys.argv) == 1:
        do.help()
    else:
        if sys.argv[1] == "search":
            if len(sys.argv) == 3:
                do.Search(sys.argv[2])
            elif len(sys.argv) == 4:
                do.Search(sys.argv[2],sys.argv[3])
            else:
                print "bad parameters"
        elif sys.argv[1] == "get":
            do.get(sys.argv[2])
        elif sys.argv[1] == "web":
            do.webpage(sys.argv[2])
        elif sys.argv[1] == "dw":
            if len(sys.argv) == 3:
                do.download(sys.argv[2])
            elif len(sys.argv) == 4:
                do.download(sys.argv[2],sys.argv[3])
            else:
                print "bad parameters"
        elif sys.argv[1] == "listdb":
            do.listdb()
        elif sys.argv[1] == "csearch":
            do.cachedSearch(sys.argv[2])
        elif sys.argv[1] == "export":
            do.data.load()
            do.data.export()
        elif sys.argv[1] == "lscat":
            do.lscat()
        elif sys.argv[1] == "help":
            do.help()
        else:
            print "not valid options: " + sys.argv[1]
            print "try help"
        
        


