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

use_pwd = False
import json, urllib2, urllib, datetime, base

class Item(base.BaseItem):
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
        self.idate = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

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
        array = date.split(" ")
        day = array[1]
        month = months[array[2]]
        year = array[3]
        time = array[4]
        newdate = datetime.date(int(year),int(month),int(day))
        finaldate = newdate.strftime("%a, %d %b %Y %H:%M:%S GMT")
        return finaldate


class Data(base.BaseData):
    def __init__(self):
        self.pages=4 #11
        self.list = []
        self.url='https://kickass.to'
        self.name='kickasstorrents'
        self.shortname='KCK'
        self.cats = {
            'all': '',
            'anime':'Anime',
            'film': 'Movies', 
            'book-e': 'Books', 
            'serie': 'TV', 
            'musica': 'Music', 
            'giochi': 'Games', 
            'apps': 'Applications'}
        self.cat='all'
        self.filter='ita' #None

    def search(self, what, cat='all'):
        ret = []
        i = 1
        while True and i<self.pages:
            results = []
            pattern = urllib.urlencode(dict(q = what))
            try:
                u = urllib2.urlopen( self.url + '/json.php?%s&page=%d' %(pattern ,i) )
                #print self.url + '/json.php?%s&page=%d' %(pattern ,i)
                json_data = u.read()
                try:
                    json_dict = json.loads(json_data)
                except:
                    i += 1
                    continue

                if int(json_dict['total_results']) <= 0: return
                results = json_dict['list']

                for r in results:
                    try:
                        if cat != 'all' and self.cats[cat] != r['category']: continue
                        name = r['title']
                        size = str(r['size'])
                        seeds = r['seeds']
                        leech = r['leechs']
                        link = r['torrentLink']
                        desc_link = r['link']
                        date = r['pubDate']

                        newitem = Item( name, desc_link, date, str(size) )
                        newitem.torrent_link = link
                        newitem.seed = str(seeds)
                        newitem.leech = str(leech)
          
                        self.list.append(newitem)

                    except:
                        pass
            except urllib2.HTTPError, e:
                print self.shortname +" http error:  " + str(e.code)
            except urllib2.URLError, e:
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
                if base.search_words_casei(self.filter, name):
                    newitem = Item( name, link, date, str(size) )
                    newitem.torrent_link = torrent_link
                    newitem.hashvalue = hashvalue
                    newitem.magnet = magnet

                    self.list.append(newitem)      

    def getFeed(self, cat):
        self.cat=cat
        try:
            u = urllib2.urlopen( self.url + '/' + self.cats[cat].lower() + '/?rss=1'  )
            data = u.read()
            self._get_rss(data)
        except urllib2.HTTPError, e:
            print self.shortname +" http error:  " + str(e.code)
        except urllib2.URLError, e:
            print self.shortname +" url error:  " + str(e.args)

