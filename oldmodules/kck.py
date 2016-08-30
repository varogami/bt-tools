#bt-tools - tools to interact with some bittorrent sites by commandline
#modified by qbittorrent ( http://www.qbittorrent.org/ ) search plugin
#qbittorrent author: Christophe Dumez (chris@qbittorrent.org) 
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

#module config
use_pwd = False
m_pages = 4 #11 - limit pages
#m_url = 'https://kickass.to'
m_url = 'https://kat.cr'
m_name = 'kickasstorrents'
m_shortname = 'KCK'
m_rss_light_download = True
m_cats = {
    'all': '',
    'anime':'Anime',
    'other':'Other',
    'movie': 'Movies', 
    'books': 'Books', 
    'tv': 'TV', 
    'music': 'Music',
    'xxx': 'XXX',
    'games': 'Games', 
    'apps': 'Applications'}
m_default_cat = 'all'
m_rss_filter = None #None - for not set filter - filter rss feed


import json, urllib, datetime, utils, httplib2
from BeautifulSoup import BeautifulSoup

class Item:
    def __init__(self, name, weblink, date, size):
        self.name = name
        self.date = self._convert_date(date)
        self.link = weblink
        self.size = size
        self.id = self._get_id(weblink)
        self.magnet = None
        self.files = None
        self.seed = None
        self.leech = None
        self.compl = None
        self.hashvalue = None
        self.idate = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S UTC")
        self.torrent_link = None
        self.torrent_link_alt1 = None
        self.torrent_link_alt2 = None
        self.descr = None
        
    def _get_id(self, link):
        string = link.replace(".html","")
        count = len(string) - 1
        char="a"
        while not char == "t":
            char = string[count]
            count = count-1
        count=count+2
        id = string[count:]
        return id

    def _convert_date(self, date):
        months = { "Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12 }
        week, day, month_w, year, time, gmt = date.split(" ")
        month = months[month_w]
        hour, minutes, second = time.split(":")
        newdate = datetime.datetime(int(year),int(month),int(day),int(hour),int(minutes),int(second))
        finaldate = newdate.strftime("%a, %d %b %Y %H:%M:%S GMT")
        return finaldate

class Data:
    def __init__(self, debug = False):
        self.pages = m_pages
        self.list = []
        self.url = m_url
        self.name = m_name
        self.shortname = m_shortname
        self.cats = m_cats
        self.cat = m_default_cat
        self.filter = m_rss_filter
        self.debug = debug
        self.rss_light_download = m_rss_light_download
                
    def makeVoidItem(self):
        void = Item("void","https://void/void-tvoid.html","Friday 1 Jun 1970 00:00:00 +0000","0")
        void.date = None
        void.size = None
        void.name = None
        return void
        
    def search(self, what, cat='all'):
        self.cat = cat
        ret = []
        i = 1
        while True and i<self.pages:
            results = []
            pattern = urllib.urlencode(dict(q = what))
            try:
                u = urllib.urlopen( self.url + '/json.php?%s&page=%d' %(pattern ,i) ) #was urllib2
                json_data = u.read()
                try:
                    json_dict = json.loads(json_data)
                except:
                    i += 1
                    continue

                if int(json_dict['total_results']) <= 0:
                    return
                results = json_dict['list']

                for r in results:
                    try:
                        if cat != 'all' and self.cats[cat] != r['category']:
                            continue
                        name = r['title']
                        size = str(r['size'])
                        seeds = r['seeds']
                        leech = r['leechs']
                        link = r['torrentLink']
                        desc_link = r['link']
                        date = r['pubDate']
                        files = r['files'] #to use in the future
                        hash = r['hash'] 

                        newitem = Item( name, desc_link, date, str(size) )
                        newitem.torrent_link = link
                        newitem.seed = str(seeds)
                        newitem.leech = str(leech)
                        newitem.hashvalue = hash
                        newitem.magnet = utils.get_mag_by_hash(hash)
                        newitem.torrent_link_alt1 = utils.get_url_by_hash(hash, utils.link_torcache )
                        newitem.torrent_link_alt2 = utils.get_url_by_hash(hash, utils.link_zoink )
                        
                        self.list.append(newitem)

                    except:
                        pass
            except urllib.HTTPError, e:
                print self.shortname +" http error:  " + str(e.code)
            except urllib.URLError, e:
                print self.shortname +" url error:  " + str(e.args)
            i += 1

    def _get_rss(self, code):
        import feedparser
        parsedRss = feedparser.parse(code)
    
        for i in parsedRss.entries:
            name = i['title']
            link = i['guid']
            date = i['published']
            torrent_link = i.enclosures[0]['href']
            size = i.enclosures[0]['length']
            magnet = i['torrent_magneturi']
            hashvalue = i['torrent_infohash']

            if not self.filter == None:
                if utils.search_words_case_insens(self.filter, name):
                    newitem = Item( name, link, date, str(size) )
                    newitem.torrent_link = torrent_link
                    newitem.hashvalue = hashvalue
                    newitem.magnet = magnet

                    self.list.append(newitem)      

    def getFeed(self, cat):
        self.cat=cat
        try:
            u = urllib.urlopen( self.url + '/' + self.cats[cat].lower() + '/?rss=1'  )
            data = u.read()
            self._get_rss(data)
        except urllib.HTTPError, e:
            print self.shortname +" http error:  " + str(e.code)
        except urllib.URLError, e:
            print self.shortname +" url error:  " + str(e.args)
        except Exception, e:
            print self.shortname + " error:  " + str(e)

    def get_detail_data(self, item_obj):
        try:
            result=httplib2.Http()
            resp,content=result.request(item_obj.link, 'GET')
            parsedDetails = BeautifulSoup( content ,convertEntities = BeautifulSoup.HTML_ENTITIES )
         
            item_obj.magnet = parsedDetails.find('a',{'title':'Magnet link'}).get('href')
            item_obj.leech = parsedDetails.find('div',{'class':'widgetLeech'}).find('strong').getText()
            item_obj.seed = parsedDetails.find('div',{'class':'widgetSeed'}).find('strong').getText()
            size = parsedDetails.find('div',{'class':'widgetSize'}).find('strong').getText()
            cut=len(size)-2
            size2 = size[:cut] + " " + size[cut:]
            item_obj.size = utils.getBytes(size2)
            item_obj.compl = parsedDetails.find('div',{'class':'font11px lightgrey line160perc'}).getText().split("Downloaded ")[1].split(" times.")[0].replace(",","")
            #item_obj.descr = parsedDetails.find('div',{'class':'dataList'})
        except Exception, e:
            print self.shortname + " error:  " + str(e)

    def getCategory(self, type):
        """build data object of single category by website page (only 1 page)"""
        pass
    
    def get_torrent_file(self, item):
        utils.get_torrent_file(item, self.shortname, download_path)
