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

#module config
use_pwd = False
m_advanced_search = False #if True search have much result - False more speed - True not work
m_rss_light_download = False #True not work after last update
m_url = 'http://ilcorsaronero.info'
m_name = 'il corsaro nero'
m_shortname = 'ICN'
m_cats = {
    "all":"FAKE",
    "movie":"1",
    "movie_dvd":"20",
    "movie_screener":"19",
    "anime":"5",
    "tv":"15",
    "apps_linux":"8",
    "apps_mac":"9",
    "apps_win":"7",
    "music":"2",
    "books_audio":"18",
    "games_pc":"3",
    "games_playstation":"13",
    "games_xbox":"14",
    "hacking":"16",
    "other":"4",
    "books":"6"
            }
m_default_cat = "all"

import urllib, httplib2 
from BeautifulSoup import BeautifulSoup
import utils
from datetime import datetime, date

class Item:
    def __init__(self,name,date,weblink,size):
        self.name = name
        self.date = self._convert_date(date)
        self.link = m_url + weblink
        self.size = utils.getBytes(size)
        self.id = self.link.split("/")[4]
        self.magnet = None
        self.torrent_link = None
        self.files = None
        self.seed = None
        self.leech = None
        self.compl = None
        self.hashvalue = None
        self.idate = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S UTC")
        self.torrent_link_alt1 = None
        self.torrent_link_alt2 = None
        self.descr = None
        
    def _convert_date(self, string):
        if len(string) < 20:
            day,month,year = string.split('.')
            cdate = date(int("20"+year),int(month),int(day))
        else:
            day,month,year = string.split("  - ")[0].split('.')
            Hour,Min,Sec = string.split("  - ")[1].split(':')
            cdate = datetime(int("20"+year),int(month),int(day),int(Hour),int(Min),int(Sec))
        finaldate = cdate.strftime("%a, %d %b %Y %H:%M:%S CET")
        return finaldate
        

class Data:
    def __init__(self, debug = False):
        self.list = []
        self.adv = m_advanced_search
        self.url = m_url
        self.name = m_name
        self.shortname = m_shortname
        self.cats = m_cats
        self.cat = m_default_cat
        self.rss_light_download = m_rss_light_download
        self.debug = debug

    def makeVoidItem(self):
        void = Item("void","01.01.01","http://void/void/void/void","0")
        void.size = None # fix problem with bt-info update
        return void
                
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
        #self._get_data(content.decode("utf-8"))
        self._get_data(content)

    def _run_search_adv(self, pattern, cat):
        result=httplib2.Http()
        data=urllib.pathname2url(pattern)

        if cat=="all":
            uri=self.url + "/adv/" + data + ".html"
        else:
             uri=self.url + "/adv/" + self.cats[cat] + "/" + data + ".html"

        resp,content=result.request(uri, 'GET')

        #parsed = self._get_data(content.decode("utf-8"))
        parsed = self._get_data(content)

        footer = parsed.find('p',{'align':'center'})
        if not footer == None:
            links = footer.findAll('a')
            for link in links:
                if link.getText().find('successive') > 0:
                    uri = self.url + link.get('href')
                    result=httplib2.Http()
                    resp,content=result.request(uri, 'GET')
                    #self._get_data(content.decode("utf-8"))
                    self._get_data(content)

    def _get_data(self, html):
        parsedHtml = BeautifulSoup( html, convertEntities = BeautifulSoup.HTML_ENTITIES)

        dark_row_list = parsedHtml.findAll('tr',{'class':'odd'})
        light_row_list = parsedHtml.findAll('tr',{'class':'odd2'})

        LEND = len(dark_row_list)
        LENL = len(light_row_list)
        TOT = LEND + LENL + 1
        CD=0
        CL=0
        for i in range(1,TOT):
            if utils.isodd(i):
                self._extract_row_data(dark_row_list[CD])
                CD=CD+1
            else:
                self._extract_row_data(light_row_list[CL])
                CL=CL+1
        return parsedHtml


    def _extract_row_data(self, row_code):
        name = row_code.find('a',{'class':'tab'}).getText()
        weblink = row_code.find('a',{'class':'tab'}).get('href')
        size = row_code.find('font').getText()
        date = row_code.find('font',{'color':'#669999'}).getText()

        newitem = Item(name,date,weblink,size)
            
        infohash = row_code.find('input',{'class':'downarrow'}).get('value')
        newitem.hashvalue = infohash
        newitem.torrent_link_alt1 = utils.get_url_by_hash(infohash, utils.link_torcache )
        newitem.torrent_link_alt2 = utils.get_url_by_hash(infohash, utils.link_zoink )
        newitem.magnet = utils.get_mag_by_hash(infohash)
        
        if row_code.find('font',{'color':'#00CC00'}):
            newitem.seed = row_code.find('font',{'color':'#00CC00'}).getText()
        else:
            newitem.seed = "x"
        if row_code.find('font',{'color':'#0066CC'}):
            newitem.leech = row_code.find('font',{'color':'#0066CC'}).getText()
        else:
            newitem.leech = "x"
        self.list.append(newitem)

    def _get_rss(self,type):
        import feedparser
        uri=self.url+'/rsscat.php?cat='+self.cats[type]
        result=httplib2.Http()
        resp,content=result.request(uri, 'GET')
        parsedRss = feedparser.parse(content)        
        tmplist = []
        for i in parsedRss.entries:
            name = i['title']
            link = i['link']
            newitem = Item(name,'01.01.01',link,'0 byte')
            tmplist.append(newitem)
        return tmplist

    def _build_new_rss(self, rssdata):
        for rssitem in rssdata:
            count=0
            webitem = self.list[count]
            #find element from data get by website
            while webitem.id != rssitem.id:
                count = count+1
                webitem = self.list[count]
            #if element found set variables
            if webitem.id == rssitem.id:
                webitem.name = rssitem.name
        
    def get_detail_data(self, item_obj):
        try:
            result=httplib2.Http()
            resp,content=result.request(item_obj.link, 'GET')
            #parsedDetails = BeautifulSoup( content.decode("utf-8") ,convertEntities = BeautifulSoup.HTML_ENTITIES )
            parsedDetails = BeautifulSoup( content ,convertEntities = BeautifulSoup.HTML_ENTITIES )

            #get data
            magnet_raw = parsedDetails.find('a',{'class':'forbtn','target':'_blank'})
            if magnet_raw == None:
                magnet_raw = parsedDetails.find('a',{'class':'forbtn magnet','target':'_blank'})
            magnet = magnet_raw.get('href')
            name_m = magnet.split("&tr=")[0].split("&dn=")[1]
            name = urllib.unquote_plus(name_m)
        
            ## another way to get name 
            #name = parsedDetails.find('title').getText().encode("iso-8859-1")
            #string_to_del1="ilCorSaRoNeRo.info - "
            #string_to_del2=" - torrent ita download"
            #name = name.replace(string_to_del1, "")
            #name = name.replace(string_to_del2, "")

            tdodd = parsedDetails.findAll('tr',{'class':'odd'})
            tdodd2 = parsedDetails.findAll('tr',{'class':'odd2'})
        
            alltd = parsedDetails.findAll('td')
            if alltd[9].getText() == "Descrizione":
                description = alltd[10].getText()#.decode("iso-8859-1")
                #.decode("utf-8")
            else:
                description = None
         
            item_obj.magnet = magnet
            item_obj.name = name
            item_obj.leech = tdodd2[3].findAll('font')[1].getText()
            item_obj.seed = tdodd2[3].findAll('font')[0].getText()
            item_obj.compl = tdodd2[4].findAll('td')[1].getText().replace("x","")
            item_obj.date = item_obj._convert_date(tdodd[1].findAll('td')[1].getText())
            #item_obj.descr = description
        except Exception, e:
            print self.shortname + " error:  " + str(e)
            

        
    def search(self, pattern, type):
        self.cat=type
        try:
            if self.adv:
                self._run_search_adv(pattern, type)
            else:
                self._run_search(pattern, type)
        except Exception, e:
            print self.shortname + " error:  " + str(e)
            
    #build data object of single category by website(only 1 page)
    def getCategory(self, type):
        self.cat=type
        uri=self.url+"/cat/"+self.cats[type]
        result=httplib2.Http()
        resp,content=result.request(uri, 'GET')
        
        #self._get_data(content.decode("utf-8"))
        self._get_data(content)

    def getFeed(self, type):
        #try:
            if self.rss_light_download:
                #build data object by downloading rss feed
                feedlist = self._get_rss(type)
        
                #download web page of specific category and build data object (self.list)
                self.getCategory(type)

                #build new rss
                self._build_new_rss(feedlist)
            else:
                #download web page of specific category and build data object (self.list)
                self.getCategory(type)

        #except Exception, e:
        #    print self.shortname +" error:  " + str(e)

    def get_torrent_file(self, item, download_path):
        utils.get_torrent_file(item, self.shortname, download_path)
