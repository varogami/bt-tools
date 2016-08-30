#! /usr/bin/python
# -*- coding=utf-8 -*-

#bt-tools - tools to interact with some bittorrent sites by commandline
#Copyright (C) 2015 varogami <varogami@autistici.org>

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
from modules import utils
from lib import rssfilter_qbt as qbt
import os, config, shutil, time

class Data:
    def __init__(self):
        self.file = config.dbfile
        self.root = etree.Element("bittorrent-db")
        self.debug = config.debug
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
        #write pretty xml file
        if self.debug:
            self.export()

    def load(self):
        if os.path.isfile(self.file):
            self.tree = etree.parse(self.file)
            self.root = self.tree.getroot()
        else:
            print config.color_red + self.file + " not exist" + config.color_base

            
    def insert(self, data, src, verbose = False, download_detail = False):
        self.countAdd=0
        category=data.cat
        #create list of inserted iteb to use with filter
        if config.rss_daemon_download_filtered:
            self.list_inserted = []
        #update db
        if os.path.isfile(self.file):
            self.load()
            resultlist = self.getList(data.name)
                
            #website not present in db - add new list and add item
            if resultlist.doc is None:
                resultlist = self.addList(data.name, data.shortname, data.url)

                for i in data.list:
                    if download_detail:
                        data.get_detail_data(i)
                    self._add_item(resultlist, i, src, category, verbose)
            else:
                #add item to list if not present
                for i in data.list:
                    seekitem = resultlist.getItem(i.id)
                    if seekitem.elem is None:
                        if download_detail:
                            data.get_detail_data(i)
                        self._add_item(resultlist, i, src, category, verbose)
                        

        #create db file if not exist
        else:
            resultlist = self.addList(data.name, data.shortname, data.url)
            for i in data.list:
                if download_detail:
                    data.get_detail_data(i)
                self._add_item(resultlist, i, src, category, verbose)
                
        if self.countAdd > 0:
            self.write()
            print config.color_cyan + \
              str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " - bt-tools: [" + \
              data.shortname+ "] type \"" + \
              data.cat + "\" - added " + \
              str(self.countAdd) + " items on database" + config.color_base


    def _add_item(self, list, data, src, cat, verbose = False):
        if config.rss_daemon_download_filtered:
            self.list_inserted.append(data)
        item = list.addItem(data.id, src, cat, data.idate)
        item.addKey("name", data.name)
        item.addKey("link", data.link)
        self._if_exist_add_key(item, data.date, "date")
        self._if_exist_add_key(item, data.size, "size")
        self._if_exist_add_key(item, data.seed, "seed")
        self._if_exist_add_key(item, data.leech, "leech")
        self._if_exist_add_key(item, data.hashvalue, "hashvalue")
        self._if_exist_add_key(item, data.magnet, "magnet")
        self._if_exist_add_key(item, data.torrent_link, "torrent-link")
        self._if_exist_add_key(item, data.torrent_link_alt1, "torrent-link_alt1")
        self._if_exist_add_key(item, data.torrent_link_alt2, "torrent-link_alt2")
        self._if_exist_add_key(item, data.files, "files")
        self._if_exist_add_key(item, data.compl, "completed")
        self._if_exist_add_key(item, data.descr, "description")
        self.countAdd = self.countAdd + 1
        if verbose:
            print config.color_green + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  + " - bt-tools: downloaded item  \"" + data.name + "\"" + config.color_base

    def filter(self, engine, cat, verbose = False):
        words_filtered = []
            
        #get words by file
        filter_file_name = config.rssdir + "ALL-" + cat + "-filters.txt"
        if os.path.isfile(filter_file_name):
            filter_file = open(filter_file_name, "r")
            for line in filter_file:
                words_filtered.append(line.replace("\n",""))
            filter_file.close()

        #get qbittorent words by rss-conf file
        if config.rss_daemon_download_filtered_qbt:
            #update/create qbt filter files
            qbt.Func().write_rules()
            qbt_file_name = config.rssdir + engine.shortname + "-" + cat + "-filters-qbt.txt"
            if os.path.isfile(qbt_file_name):
                qbt_file = open(qbt_file_name, "r")
                for line in qbt_file:
                    words_filtered.append(line.replace("\n",""))
                qbt_file.close()

        if not len(words_filtered) == 0:
            #sort and remove duplicate to the final filter list
            words_filtered.sort()
            tmp_list = []
            tmp_list.append(words_filtered[0])
            TC = 0
            for i in words_filtered:
                if not tmp_list[TC] == i:
                    tmp_list.append(i)
                    TC = TC+1

            #filter item added in filter list
            words_filtered = tmp_list
            items_to_download = []
            for item in self.list_inserted:
                for seek in words_filtered:
                    if utils.search_words_case_insens(seek,item.name):
                        if verbose:
                            print config.color_blu + \
                              str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  + \
                              " - bt-tools: filter \"" + seek + \
                              "\" - item \"" + item.name + "\"" + config.color_base
                        items_to_download.append(item)
                        break
            return items_to_download
        else:
            return None

    def add_item_to_filter_coda(self, item):
        coda_file = open(config.filter_coda_file, "a")
        coda_file.write(item.magnet+"\n")
        coda_file.close()

                
    def _if_exist_add_key(self, XMLitem, value, name):
        if not value is None:
            XMLitem.addKey(name, value)

    def getKeyRaw(self, name, obj):
        value = obj.find("./key[@name='" + name + "']")
        if value == None:
            return "X"
        else:
            return value.text
        
    def export(self):
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(self.file, parser)
        tree.write(self.export_filename, pretty_print=True)

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
        
        #TODO - limit 
        #config.rssLimit
        for i in rsslist:
            #get xml data
            name = i.xpath("./key[@name='name']")[0].text
            link = i.xpath("./key[@name='link']")[0].text
            size = utils.sizeof(float(i.xpath("./key[@name='size']")[0].text))
            date = i.xpath("./key[@name='date']")[0].text
            hashvalue = i.xpath("./key[@name='hashvalue']")[0].text

            uhash = hashvalue.upper()
            torcaheURI = utils.get_url_by_hash(hashvalue,utils.link_torcache)
            magneturi = utils.get_mag_by_hash(hashvalue)

            #write rss
            rssitem =  etree.SubElement(channel,"item")
            title = etree.SubElement(rssitem, "title")
            title.text = name
            desctxt = "<br/><b>Magnet:</b><a href='"+magneturi+"' target=_blank>link</a><br/><b>Size:</b>"+size+"<br/><b>Date:</b>"+date+""
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

        rsstree = etree.ElementTree(rssroot)
        rsstree.write(rssfile,xml_declaration=True, encoding='utf-8')

        if self.debug:
            outfilename = self.rssdir + "pretty-" + filename + "-" + category + ".rss"
            parser = etree.XMLParser(remove_blank_text=True)
            tree = etree.parse(rssfile, parser)
            tree.write(outfilename, pretty_print=True)


    def exportConky(self, namelist, cat, chars, row):
        print "${" + config.conky_color1 + "}${font " + config.conky_font_bold + "}" + namelist + " - " + cat + "${" + config.conky_color1 + "}${font " + config.conky_font + "}"        
        color1="${" + config.conky_color_line_even + "}  "
        color2="${" + config.conky_color_line_odd + "}  "

        itemlist = self.getList(namelist)
        if not itemlist.doc == None:
            rsslist = itemlist.doc.xpath("./item[@src='rss'][@type='"+cat+"']")
            if not len(rsslist) == 0:
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
            else:
                print "no items"
        else:
            print "no items"
 
    def _backup(self):
        DATE=datetime.now().strftime("%Y%m%d-%H")
        BK1 = self.logdir + DATE + "-database.xml"
        BK2 = self.logdir + DATE + "-database-pretty.xml"
        if not os.path.isfile(BK1):
            if os.path.isfile(config.dbfile):
                shutil.copy(config.dbfile, BK1)
            if os.path.isfile(config.export_file):
                shutil.copy(config.export_file, BK2)



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

    def delItem(self, id):
        print "Todo"

    
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

