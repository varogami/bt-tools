#got by https://github.com/fm4d/KickassAPI

import json, urllib, datetime, httplib2
from BeautifulSoup import BeautifulSoup
from lib import module
import KickassAPI

class Config(module.Config):
    def __init__(self):
        self.enabled = True
        #self.url = 'https://kickasstop.com/'
        self.url = 'https://kat.am'
        #self.url = 'http://katcr.to'
        self.name = 'kickasstorrents'
        self.rss_light_download = True
        self.pages = 4 #11 - limit pages
        self.cats = {
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
        self.default_cat = 'all'
        self.rss_filter = None #None - for not set filter - filter rss feed


class Item(module.Item):
    def _set_id(self, link):
        string = link.replace(".html","")
        count = len(string) - 1
        char="a"
        while not char == "t":
            char = string[count]
            count = count-1
        count=count+2
        self.id = string[count:]

    def _set_date(self, date):
        months = { "Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12 }
        week, day, month_w, year, time, gmt = date.split(" ")
        month = months[month_w]
        hour, minutes, second = time.split(":")
        newdate = datetime.datetime(int(year),int(month),int(day),int(hour),int(minutes),int(second))
        self.date = newdate.strftime("%a, %d %b %Y %H:%M:%S GMT")



        
class Data(module.Data):
    def __init__(self, name, config, debug = False):
        module.Data.__init__(self,name,config,debug)        
        self.pages = config['pages']
        self.filter = config['rss_filter']
        self.rss_light_download = config['rss_light_download']                
        self.api = KickassAPI

    def search(self, what):
        KickassAPI.Search
    def search_bk(self, what, cat='all'):
        self.cat = cat
        ret = []
        i = 1
        while True and i<self.pages:
            results = []
            pattern = urllib.urlencode(dict(q = what))
            #try:
            test = True
            if test:
                u = urllib.urlopen( self.url + '/json.php?%s&page=%d' %(pattern ,i) ) #was urllib2
                if self.debug:
                    print self.url + '/json.php?%s&page=%d' %(pattern ,i)
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

                        newitem = Item()
                        newitem.name = r['title']
                        newitem.size = str(r['size'])
                        newitem.seed = str(r['seeds'])
                        newitem.leech = str(r['leechs'])
                        newitem.link = r['torrentLink']
                        newitem._set_obj(r['link'],"descr")
                        newitem._set_date = r['pubDate']
                        newitem._set_obj(r['files'],"files")
                        newitem.hashvalue = r['hash'] 
                        newitem.torrent_link = link
                        newitem.hashvalue = hash
                        newitem.magnet = utils.get_mag_by_hash(hash)                       
                        newitem.add_torrent_link(utils.get_url_by_hash(hash, utils.link_torcache ))
                        newitem.add_torrent_link(utils.get_url_by_hash(hash, utils.link_zoink ))
                        self.list.append(newitem)

                    except:
                        pass
                return True
            #except urllib.HTTPError, e:
             #   print self.shortname +" http error:  " + str(e.code)
              #  return False
            #except urllib.URLError, e:
             #   print self.shortname +" url error:  " + str(e.args)
              #  return False
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

    
    def get_torrent_file(self, item):
        utils.get_torrent_file(item, self.shortname, download_path)
    
