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

from lxml import etree
from datetime import datetime
import os, config


def sizeof(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

class Data:
    def __init__(self):
        self.file = config.dbfile
        self.root = etree.Element("bittorrent-db")
        self.debug = config.debug
        self.cats = config.categories_change
        self.lockfile="/tmp/bt-tools.lock" 
        self.export_filename = config.export_file
        self.rssdir = config.rssdir
        self.logdir = config.logdir
                
    def addList(self, name, src, type):
        newlist = List(self.root)
        newlist.set(name, src, type)
        return newlist

    def getList(self, name):
        code = self.root.find("./list[@name='"+name+"']")
        list = List(self.root)
        list.load(code)
        return list


    def write(self):
        import time

        while os.path.isfile(self.lockfile):
            print "another process work - wait to write"
            time.sleep(10)

        #BACKUP in LOG
        if self.debug:
            self._backup()
        lock = open(self.lockfile, "w")
        lock.close()
        self._write()
        os.remove(self.lockfile)

    def _write(self):
        self.tree = etree.ElementTree(self.root)
        self.tree.write(self.file, xml_declaration=True, encoding='utf-8')
        if self.debug:
            #write pretty xml file
            self.export()

    def load(self):
        if os.path.isfile(self.file):
            self.tree = etree.parse(self.file)
            self.root = self.tree.getroot()
        else:
            print self.file + " not exist"

    def export(self):
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(self.file, parser)
        tree.write(export_filename, pretty_print=True)

    def exportRssByXml(self, engine, category):
        filename=engine.shortname
        namelist=engine.name
        rssfile= self.rssdir + filename + "-" + category + ".rss"
        namespace = {'torrent': 'http://xmlns.ezrss.it/0.1/'} 
        etree.register_namespace('torrent', 'http://xmlns.ezrss.it/0.1/')
        rssroot = etree.Element("rss", version="2.0", nsmap=namespace)
        channel = etree.SubElement(rssroot, "channel")

        self.load()
        itemlist = self.getList(namelist)
        title = etree.SubElement(channel,"title")
        title.text = itemlist.doc.attrib['name'] + " - " + category + " feed"
        link = etree.SubElement(channel,"link")
        link.text = itemlist.doc.attrib['url']
        desc= etree.SubElement(channel,"description")
        desc.text = itemlist.doc.attrib['name']

        rsslist = itemlist.doc.xpath("./item[@src='rss'][@type='"+category+"']")

        for i in rsslist:
            #get xml data
            name = i.xpath("./key[@name='name']")[0].text
            link = i.xpath("./key[@name='link']")[0].text
            size = sizeof(float(i.xpath("./key[@name='size']")[0].text))
            date = i.xpath("./key[@name='date']")[0].text
            hashvalue = i.xpath("./key[@name='hashvalue']")[0].text
            #if torrent not exist TODO
            uhash = hashvalue.upper()
            magneturi = "magnet:?xt=urn:btih:"+uhash
            torcaheURI="http://torcache.net/torrent/"+uhash+".torrent"

            #write rss
            rssitem =  etree.SubElement(channel,"item")
            title = etree.SubElement(rssitem, "title")
            title.text = name
            desctxt = "<br/>Magnet: <b><a href='"+magneturi+"' target=_blank>link</a></b><br/>Size: "+size+"<br/>Date: "+date+""
            desc = etree.SubElement(rssitem, "description")
            desc.text = etree.CDATA(desctxt)
            cat = etree.SubElement(rssitem, "category")
            cat.text = category
            rsslink = etree.SubElement(rssitem, "link")
            rsslink.text = link
            id = etree.SubElement(rssitem, "guid")
            id.text = link
            rssdate = etree.SubElement(rssitem, "pubDate")
            rssdate.text =  date
            hash = etree.SubElement(rssitem, "{http://xmlns.ezrss.it/0.1/}infoHash")
            hash.text = uhash
            magnet = etree.SubElement(rssitem, "{http://xmlns.ezrss.it/0.1/}magnetURI")
            magnet.text = etree.CDATA(magneturi)
            enclosure = etree.SubElement(rssitem, "enclosure", url=torcaheURI, type="application/x-bittorrent")  

        #print(etree.tostring(rssroot, pretty_print=True))
        rsstree = etree.ElementTree(rssroot)
        rsstree.write(rssfile,xml_declaration=True, encoding='utf-8')

        if self.debug:
            outfilename = self.rssdir + "pretty-" + filename + "-" + category + ".rss"
            parser = etree.XMLParser(remove_blank_text=True)
            tree = etree.parse(rssfile, parser)
            tree.write(outfilename, pretty_print=True)

    def exportRssByXml(self, engine, category):
        filename = engine.shortname
        namelist = engine.name
        rssfile = self.rssdir + filename + "-" +category + ".rss"
        namespace = {'torrent': 'http://xmlns.ezrss.it/0.1/'} 
        etree.register_namespace('torrent', 'http://xmlns.ezrss.it/0.1/')
        rssroot = etree.Element("rss", version="2.0", nsmap=namespace)
        channel = etree.SubElement(rssroot, "channel")

        self.load()
        itemlist = self.getList(namelist)
        title = etree.SubElement(channel,"title")
        title.text = itemlist.doc.attrib['name'] + " - " + category + " feed"
        link = etree.SubElement(channel,"link")
        link.text = itemlist.doc.attrib['url']
        desc= etree.SubElement(channel,"description")
        desc.text = itemlist.doc.attrib['name']

        rsslist = itemlist.doc.xpath("./item[@src='rss'][@type='"+category+"']")

        for i in rsslist:
            #get xml data
            name = i.xpath("./key[@name='name']")[0].text
            link = i.xpath("./key[@name='link']")[0].text
            size = sizeof(float(i.xpath("./key[@name='size']")[0].text))
            date = i.xpath("./key[@name='date']")[0].text
            hashvalue = i.xpath("./key[@name='hashvalue']")[0].text
            #if torrent not exist TODO
            uhash = hashvalue.upper()
            magneturi = "magnet:?xt=urn:btih:"+uhash
            torcaheURI="http://torcache.net/torrent/"+uhash+".torrent"

            #write rss
            rssitem =  etree.SubElement(channel,"item")
            title = etree.SubElement(rssitem, "title")
            title.text = name
            desctxt = "<br/>Magnet: <b><a href='"+magneturi+"' target=_blank>link</a></b><br/>Size: "+size+"<br/>Date: "+date+""
            desc = etree.SubElement(rssitem, "description")
            desc.text = etree.CDATA(desctxt)
            cat = etree.SubElement(rssitem, "category")
            cat.text = category
            rsslink = etree.SubElement(rssitem, "link")
            rsslink.text = link
            id = etree.SubElement(rssitem, "guid")
            id.text = link
            rssdate = etree.SubElement(rssitem, "pubDate")
            rssdate.text =  date
            hash = etree.SubElement(rssitem, "{http://xmlns.ezrss.it/0.1/}infoHash")
            hash.text = uhash
            magnet = etree.SubElement(rssitem, "{http://xmlns.ezrss.it/0.1/}magnetURI")
            magnet.text = etree.CDATA(magneturi)
            enclosure = etree.SubElement(rssitem, "enclosure", url=torcaheURI, type="application/x-bittorrent")  

        #print(etree.tostring(rssroot, pretty_print=True))
        rsstree = etree.ElementTree(rssroot)
        rsstree.write(rssfile,xml_declaration=True, encoding='utf-8')

        if self.debug:
            outfilename = self.rssdir + "pretty-" + filename + "-" + category + ".rss"
            parser = etree.XMLParser(remove_blank_text=True)
            tree = etree.parse(rssfile, parser)
            tree.write(outfilename, pretty_print=True)


    def exportConky(self, namelist, cat, chars, row):
        print "${color2}${font Sans Mono:bold:size=8}" + namelist + " - " + cat + "${color}${font Sans Mono:size=8}"        
        #color1="${color yellow}  "
        color1="${color4}  "
        color2="${color}  "

        itemlist = self.getList(namelist)
        rsslist = itemlist.doc.xpath("./item[@src='rss'][@type='"+cat+"']")

        count=len(rsslist)-1
        while count >= len(rsslist)-row:
            i = rsslist[count]
            #get xml data
            name = i.xpath("./key[@name='name']")[0].text
            count = count -1
            disp = count % 2
            if disp == 1:
                print color1 + name[:chars].encode('utf-8')
            else:
                print color2 + name[:chars].encode('utf-8')

 
    def _backup(self):
        import datetime, shutil
        DATE=datetime.datetime.now().strftime("%Y%m%d-%H")
        BK1 = self.logdir + DATE + "-database.xml"
        BK2 = self.logdir + DATE + "-database-pretty.xml"
        if not os.path.isfile(BK1):
            shutil.copy(config.dbfile, BK1)
            shutil.copy(config.export_file, BK2)


    def insert(self, data, src, verbose=False):
        self.verbose=verbose
        self.countAdd=0
        category=self.cats[data.cat]
        #update db
        if os.path.isfile(self.file):
            self.load()
            resultlist = self.getList(data.name)
                
            #add new list and add item if not exist
            if resultlist.doc is None:
                resultlist = self.addList(data.name, data.shortname, data.url)

                for i in data.list:
                    self._add_item(resultlist, i, src, category)
            else:
                #add item to list
                for i in data.list:
                    seekitem = resultlist.getItem(i.id)
                    if seekitem.elem is None:
                        self._add_item(resultlist, i, src, category)

        #create db dile
        else:
            resultlist = self.addList(data.name, data.shortname, data.url)
            for i in data.list:
                self._add_item(resultlist, i, src, category)
                
        if self.countAdd > 0:
            self.write()
            print config.xml_C03 + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " - [" + data.shortname+ "] type \"" +data.cat+ "\" - added " +str(self.countAdd) + " items on database" + config.xml_CEND


    def _add_item(self, list, data, src, cat):
        item = list.addItem(data.id, src, cat, data.idate)
        item.addKey("name", data.name)
        if self.verbose:
            print config.xml_C03 + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  + " - " + data.name + config.xml_CEND
        item.addKey("link", data.link)
        self._add_key(item, data.date, "date")
        self._add_key(item, data.size, "size")
        self._add_key(item, data.seed, "seed")
        self._add_key(item, data.leech, "leech")
        self._add_key(item, data.hashvalue, "hashvalue")
        self._add_key(item, data.magnet, "magnet")
        self._add_key(item, data.torrent_link, "torrent-link")
        self._add_key(item, data.files, "files")
        self._add_key(item, data.compl, "completed")
        self.countAdd = self.countAdd + 1

    def _add_key(self, XMLitem, value, name):
        if not value is None:
            XMLitem.addKey(name, value)

class List:
    def __init__(self, root):
        self.root = root

    def set(self, name, shortname, url):
        self.doc = etree.SubElement(self.root, "list")
        self.doc.set("name", name )
        self.doc.set("shortname", shortname)
        self.doc.set("url", url)

    def load(self, list):
        self.doc = list
        
    def addItem(self, id, src, type, idate):
        newitem = Item(self.doc)
        newitem.set(id, src, type, idate)
        return newitem

    def getItem(self, id):
        code = self.doc.find("./item[@id='"+id+"']")
        item = Item(self.doc)
        item.load(code)
        return item


class Item:
    def __init__(self, doc):
        self.doc = doc

    def set(self, id, src, type, idate):
        self.elem = etree.SubElement(self.doc, "item")
        self.elem.set("id", id)
        self.elem.set("src", src)
        self.elem.set("type", type)
        self.elem.set("date", idate)
        
    def load(self, code):
        self.elem = code

    def getAttr(self, name):
        return self.elem.attrib[name].encode('utf8')

    def isVoid(self):
        if self.elem is None:
            return True
        else:
            return False

    def addKey(self, name, value):
        newkey = Key(self.elem)
        newkey.set(name, value)

    def getKey(self, name):
        code = self.elem.find("./key[@name='"+name+"']")
        key = Key(self.elem)
        key.load(code)
        return key

    def updateKey(self, name, value):
        curkey = self.getKey(name)
        if not curkey is None:
            curkey.key.text = value
        else:
            self.addKey(name,value)

class Key:
    def __init__(self, elem):
        self.item = elem

    def set(self, name, value):
        self.key = etree.SubElement(self.item, "key")
        self.key.set("name", name)
        self.key.text = value

    def isVoid(self):
        if self.key is None:
            return True
        else:
            return False

    def getAttr(self, name):
        return self.key.attrib[name].encode('utf8')

    def getTxt(self):
        return self.key.text

    def load(self, code):
        self.key = code

