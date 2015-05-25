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

import sys, xml, time, config


class Rss:
    def __init__(self):
        self.data = xml.Data()
        self.engines = config.engines

    def getData(self, cat, numEng):
        self._getdata(self.engines[numEng], cat)

    def _getdata(self, eng, cat):
        eng.getFeed(cat)
        self.data.insert(eng, "rss", True)

    def makeRss(self, cat, numEng):
        self.data.exportRssByXml(self.engines[numEng], cat)

    def lscat(self):
        for engine in self.engines:
            engine.lscat()
            
        print "internal"
        for i in self.data.cats:
            print self.data.cats[i]

    def lssite(self):
        COUNT=0
        for engine in self.engines:
            print engine.name
            print engine.shortname + " - ID:" + str(COUNT)
            print
            COUNT=COUNT+1

    def lsdb(self, cat):
        dim=19
        self.data.load()
        for i in self.data.root:
            print
            print i.attrib['name'].encode('utf8')
            rsslist = i.xpath("./item[@src='rss'][@type='"+cat+"']")

            if len(rsslist) > 19:
                limit=19
            else:
                limit = len(rsslist)-1

            count=len(rsslist)-1
            while count >= len(rsslist)-limit:
                z = rsslist[count]
                count = count -1
                name = z.find("./key[@name]").text
                print z.attrib['id'].encode('utf8') + "  " + name

    def help(self):
        print "getdata \"cat\" \"ID engine\"- get data by category and engine"
        print "makerss \"cat\" \"ID engine\"- build rss by category category"
        print "lscat - list category for each engine"
        print "lssite - list engine name and ID"
        print "lsdb <cat> - list rss feed in db"
        
if __name__ == "__main__":
    do = Rss()

    if len(sys.argv) == 1:
        do.help()
    else:
        if sys.argv[1] == "getdata":
            do.getData(sys.argv[2], int(sys.argv[3]))
        elif sys.argv[1] == "lscat":
            do.lscat()
        elif sys.argv[1] == "lssite":
            do.lssite()
        elif sys.argv[1] == "makerss":
            do.makeRss(sys.argv[2], int(sys.argv[3]))
        elif sys.argv[1] == "makeall":
            do.makeall()
        elif sys.argv[1] == "lsdb":
            do.lsdb(sys.argv[2])
        elif sys.argv[1] == "help":
            do.help()
        else:
            print "not valid options: " + sys.argv[1]
            print "try help"
        
        

