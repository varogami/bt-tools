import urllib, httplib2, datetime, feedparser
from BeautifulSoup import BeautifulSoup
from lib import module
from lib import utils


class Config(module.Config):
    def __init__(self):
        self.enabled = True
        #self.url = 'https://kickasstop.com/'
        self.url = 'https://kat.am'
        self.name = 'kickasstorrents'
        self.rss_light_download = True
        self.cats = {
            'all': '',
            'anime':'anime',
            'other':'Other',
            'movie': 'movies', 
            'books': 'books', 
            'tv': 'tv', 
            'music': 'music',
            'xxx': 'xxx',
            'games': 'games', 
            'apps': 'applications'}
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
    def __init__(self, name, config, logdir, user_agent, debug = False):
        module.Data.__init__(self,name,config,logdir,user_agent,debug)        
        self.filter = config['rss_filter']
        self.rss_light_download = config['rss_light_download']

    def search(self, what, cat='all', page=1):
        result=httplib2.Http(disable_ssl_certificate_validation=True)
        
        if cat == "all":
            data=urllib.quote(what) 
        else:
            data=urllib.quote(what + " ") + "category:" + self.getCategory(cat)
            
        uri=self.url + "/usearch/" + data + "/"

        if self.debug:
            print "DEBUG: url "+uri
            
        resp,content=result.request(uri, 'GET')
        
        if self.debug:
            print "DEBUG: search - pattern \"" + what + "\" - cat " + cat
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.logfile = self.log_dir+"/"+self.shortname+"-search-"+pattern+"-"+cat
            logfile = open(self.logfile, "w")
            logfile.write(content)
            logfile.close()
            
        num_pages = self._get_data(content)
        if page <= num_pages:
            page += 1
            search(what,cat,page)
        
    def _get_data(self,html):
        parsedHtml = BeautifulSoup( html, convertEntities = BeautifulSoup.HTML_ENTITIES)

        try:
            num_results = int(parsedHtml.find('h2').getText().split()[-1])
            #int(pq("h2").text().split()[-1])
            if num_results % 25:
                num_pages = num_results / 25 + 1
            num_pages = num_results / 25
        except ValueError:
            num_pages = 1
            print "No results found!"


        rows = parsedHtml.find('table',{'class':'data'})
        rows = rows.findAll('tr')
   
        for i in rows:
            newitem = Item()
            td = i.find('td')
            name = td.find('a',{'class':'cellMainLink'}).getText()
            newitem.name = name.replace(" . ", ".").replace(" .", ".")
            newitem.type = td.find('span').find("strong").find("a").getText().lower()

            if td('a',{'class':'cellMainLink'}).get("href") is not None:
                newitem.link = self.link + td('a',{'class':'cellMainLink'}).get("href")
            newitem.magnet = td.find('a',{'data-nop':''}).get("href")
            newitem.torrent_link = td.find('a',{'data-download'}).get("href")
            td_centers = i.findAll('td',{'class':'center'})
            newitem.size = td_centers[0].getText()
            files = td_centers[1].getText()
            age = td_centers[2].getText()
            newitem.seed = td_centers[3].getText()
            newitem.leech = td_centers[4].getText()
            newitem._set_id(newitem.link)
            print "DEBUG: name - id - magnet" + name + id + magnet
            print files
            print age
                                              
            self.list.append(newitem)

        return 

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

    def _get_rss(self, code):
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

    
