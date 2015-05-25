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

use_pwd = False
import urllib, datetime, httplib2, base
from BeautifulSoup import BeautifulSoup


class Item(base.BaseItem):
    def __init__(self,name,date,weblink,size):
        self.name = name
        self.date = self._convert_date(date)
        self.link = weblink
        self.size = base.getBytes(size)
        self.id = self.link.split("/")[4]
        self.magnet = None
        self.torrent_link = None
        self.files = None
        self.seed = None
        self.leech = None
        self.compl = None
        self.hashvalue = None
        self.idate = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

    def _convert_date(self, string):
        day,month,year=string.split('.')
        day=int(day)
        month=int(month)
        year=int("20"+year)
        date=datetime.date(year,month,day)
        finaldate=date.strftime("%a, %d %b %Y %H:%M:%S GMT")
        return finaldate

class Data(base.BaseData):
    def __init__(self):
        self.adv=True
        self.list = []
        self.url='http://ilcorsaronero.info'
        self.name='il corsaro nero'
        self.shortname='ICN'
        self.cats = {
            "film":"1",
            "film-dvd":"20",
            "film-screen":"19",
            "anime":"5",
            "serie":"15",
            "apps-linux":"8",
            "musica":"2",
            "book-a":"18",
            "book-e":"6"
            }
        self.cat="all"
        

    def _run_search(self,pattern,cat):
        result=httplib2.Http()
        if cat == "all":
            data={'search':pattern}
            data=urllib.urlencode(data)
            uri=self.url + "/argh.php?" + data
        else:
            data=urllib.pathname2url(pattern)
            uri=self.url + "/torrent-ita/" + self.cats[cat] + "/" + data + ".html"

        resp,content=result.request(uri, 'GET')

        self._get_data(content)

    def _run_search_adv(self, pattern, cat):
        result=httplib2.Http()
        data=urllib.pathname2url(pattern)

        if cat=="all":
            uri=self.url + "/adv/" + data + ".html"
        else:
             uri=self.url + "/adv/" + self.cats[cat] + "/" + data + ".html"

        resp,content=result.request(uri, 'GET')

        parsed = self._get_data(content)

        footer = parsed.find('p',{'align':'center'})
        if not footer == None:
            links = footer.findAll('a')
            for link in links:
                if link.getText().find('successive') > 0:
                    uri = self.url + link.get('href')
                    result=httplib2.Http()
                    resp,content=result.request(uri, 'GET')
                    self._get_data(content)

    def _get_data(self, html):
        parsedHtml = BeautifulSoup(html,convertEntities=BeautifulSoup.HTML_ENTITIES)

        list1 = parsedHtml.findAll('tr',{'class':'odd'})
        self._get_base_data(list1)

        list2 = parsedHtml.findAll('tr',{'class':'odd2'})
        self._get_base_data(list2)

        return parsedHtml


    def _get_base_data(self, parsedlist):
        for i in parsedlist:
            name = i.find('a',{'class':'tab'}).getText()
            weblink = i.find('a',{'class':'tab'}).get('href')
            size = i.find('font').getText()
            date = i.find('font',{'color':'#669999'}).getText()
            newitem = Item(name,date,weblink,size)
            
            infohash = i.find('input',{'class':'downarrow'}).get('value')
            newitem.hashvalue = infohash

            if i.find('font',{'color':'#00CC00'}):
                newitem.seed = i.find('font',{'color':'#00CC00'}).getText()
            else:
                newitem.seed = "x"
            if i.find('font',{'color':'#0066CC'}):
                newitem.leech = i.find('font',{'color':'#0066CC'}).getText()
            else:
                newitem.leech = "x"
            self.list.append(newitem)

    def _get_rss(self, code):
        import feedparser
        parsedRss = feedparser.parse(code)
        tmplist = []
        for i in parsedRss.entries:
            name = i['title']
            link = i['link']
            newitem = Item(name,'01.01.01',link,'0 byte')
            tmplist.append(newitem)
        return tmplist
        
    def get_detail_data(self, link):
        result=httplib2.Http()
        resp,content=result.request(link, 'GET')
        parsedDetails = BeautifulSoup(content,convertEntities=BeautifulSoup.HTML_ENTITIES)

        magnet = parsedDetails.find('a',{'class':'forbtn','target':'_blank'}).get('href')

        voidItem = Item("void","01.01.01","http://void/void/void/void","0 byte")
        voidItem.magnet = magnet

        return voidItem
        
    def search(self, pattern, type):
        self.cat=type
        if self.adv:
            self._run_search_adv(pattern, type)
        else:
            self._run_search(pattern, type)

    def getCategory(self, type):
        self.cat=type

        uri=self.url+"/cat/"+self.cats[type]
        result=httplib2.Http()
        resp,content=result.request(uri, 'GET')
        self._get_data(content)

    def getFeed(self, type):
        self.cat=type

        uri=self.url+'/rsscat.php?cat='+self.cats[type]
        result=httplib2.Http()
        resp,content=result.request(uri, 'GET')
        #trasforma il feed scaricato in oggetto dati
        feedlist = self._get_rss(content)
        #scarica la pagina web e trasforma in oggetto dati (self.list)
        self.getCategory(type)
        
        #TODO - cerca direttamente nella pagina web l'elemento specifico senza creare l'oggetto dati
        #TODO - mettere più info negli rss (modificare anche gli altri moduli
        #inserisce negli elementi dei feed i dati presi dal web
        for i in feedlist:
            count=0
            z=self.list[count]
            #trova l'elemento
            while z.id != i.id:
                count = count+1
                z=self.list[count]
            #trovato elemento setta i parametri ulteriori
            if z.id == i.id:
                i.size = z.size
                i.date = z.date
                i.hashvalue = z.hashvalue
                i.seed = z.seed
                i.leech = z.leech
                del self.list[count]
            
        self.list = feedlist
