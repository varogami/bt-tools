import urllib, httplib2, feedparser 
try:
    from BeautifulSoup import BeautifulSoup
except Exception, e:
    from bs4 import BeautifulSoup

from datetime import datetime, date
from lib import module
from lib import utils
import feedparser

class Config(module.Config):
    def __init__(self):
        self.enabled = True
        self.url = 'http://ilcorsaronero.info'
        self.name = 'il corsaro nero'
        self.advanced_search = False #if True search have much result - False more speed - True not work
        self.rss_light_download = False #True not work after last update
        self.default_cat = "all"
        self.cats = {
            "all":"FAKE",
            "movie":"1",
            "movie_dvd":"20",
            "movie_screener":"19",
            "anime":"5",
            "tv":"15",
            "app_linux":"8",
            "app_mac":"9",
            "app_win":"7",
            "music":"2",
            "book_audio":"18",
            "game_pc":"3",
            "game_psx":"13",
            "game_xbox":"14",
            "hacking":"16",
            "other":"4",
            "book":"6"
        }
        self.rss = {
            "num_item" : 20,
            "enabled" : False,
            "feeds" : [
                "movie", "tv"
            ]
        }

class Item(module.Item):
    def _set_size(self, size):
        self.size = utils.getBytes(size) 
     
    def _set_id(self, link):
        self.id_module = link.split("/")[4]
           
    def _set_date(self, string):
        if len(string) < 20:
            day,month,year = string.split('.')
            cdate = date(int("20"+year),int(month),int(day))
        else:
            day,month,year = string.split("  - ")[0].split('.')
            Hour,Min,Sec = string.split("  - ")[1].split(':')
            cdate = datetime(int("20"+year),int(month),int(day),int(Hour),int(Min),int(Sec))
        self.date = cdate.strftime("%a, %d %b %Y %H:%M:%S CET")
    

class Data(module.Data):
    def __init__(self, name, config, log_dir, user_agent, debug = False):
        module.Data.__init__(self,name,config,log_dir,user_agent,debug)
        self.adv = config['advanced_search']
        self.rss_conf = config['rss']
        self.__mod_conf = config
        
    def _run_search(self,pattern,cat):
        result=httplib2.Http()
        if cat == "all":
            data={'search':pattern}
            data=urllib.urlencode(data)
            uri=self.url + "/argh.php?" + data
        else:
            data=urllib.pathname2url(pattern)
            uri=self.url + "/torrent-ita/" + self.cats[cat] + "/" + data + ".html"

        try:
            resp,content=result.request(uri, 'GET')
            self._get_data(content)
            return True
        except:
            return False


    def _run_search_adv(self, pattern, cat):
        result=httplib2.Http()
        data=urllib.pathname2url(pattern)

        if cat=="all":
            uri=self.url + "/adv/" + data + ".html"
        else:
             uri=self.url + "/adv/" + self.cats[cat] + "/" + data + ".html"

        try:
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
            return True
        except:
            return False

    def _get_data(self, html):
        try:
            parsedHtml = BeautifulSoup(html,convertEntities=BeautifulSoup.HTML_ENTITIES) 
        except:
            parsedHtml = BeautifulSoup(html,'html.parser') #bs4

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
        newitem = Item()
        newitem.name = row_code.find('a',{'class':'tab'}).getText()
        newitem.link = row_code.find('a',{'class':'tab'}).get('href')        
        newitem._set_id(newitem.link)
        size = row_code.find('font').getText()
        newitem._set_size(size)
        date = row_code.find('font',{'color':'#669999'}).getText()
        newitem._set_date(date)

        newitem.type =  row_code.find('a',{'class':'red'}).get('href').split('/')[4] 
        newitem.hashvalue = row_code.find('input',{'class':'downarrow'}).get('value')
        #tor_link_alt1 = utils.get_url_by_hash(newitem.infohash, utils.link_torcache )
        #tor_link_alt2 = utils.get_url_by_hash(newitem.infohash, utils.link_zoink )
        #newitem.add_torrent_link(tor_link_alt1)
        #newitem.add_torrent_link(tor_link_alt2)
        #newitem.magnet = utils.get_mag_by_hash(newitem.infohash)

        if row_code.find('font',{'color':'#00CC00'}):
            newitem.seed = row_code.find('font',{'color':'#00CC00'}).getText()
        else:
            newitem.seed = newitem.nodata
            
        if row_code.find('font',{'color':'#0066CC'}):
            newitem.leech = row_code.find('font',{'color':'#0066CC'}).getText()
        else:
            newitem.leech = newitem.nodata

        if row_code.find('font',{'color':'#EEEEEE'}):
            newitem.compl = row_code.find('font',{'color':'#EEEEEE'}).getText().replace('x','')
        else:
            newitem.compl = newitem.nodata

        self.list.append(newitem)

                    
    def __get_detail_data(self, item):
        result=httplib2.Http()
        resp,content=result.request(item.link, 'GET')
        #parsedDetails = BeautifulSoup( content.decode("utf-8") ,convertEntities = BeautifulSoup.HTML_ENTITIES )
        try:
            parsedDetails = BeautifulSoup(content,convertEntities=BeautifulSoup.HTML_ENTITIES) 
        except:
            parsedDetails = BeautifulSoup(content,'html.parser') #bs4
        
        #get data
        magnet_raw = parsedDetails.find('a',{'class':'forbtn magnet'})
        if magnet_raw == None:
            magnet_raw = parsedDetails.find('a',{'class':'forbtn magnet','target':'_blank'})
        item.magnet = magnet_raw.get('href')
        name_m = item.magnet.split("&tr=")[0].split("&dn=")[1]
        item.name = urllib.unquote_plus(name_m)
        
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
         
        item.leech = tdodd2[3].findAll('font')[1].getText()
        item.seed = tdodd2[3].findAll('font')[0].getText()
        item.compl = tdodd2[4].findAll('td')[1].getText().replace("x","")
        tmp_item = Item()
        tmp_item._set_date(tdodd[1].findAll('td')[1].getText())
        item.date = tmp_item.date
        #item.descr = description
 
        return item
    
    def get_detail_data(self, item):
        if self.debug:
            return self.__get_detail_data(item)
        else:
            try:
                return self.__get_detail_data(item)
            except Exception, e:
                print self.shortname + " error:  " + str(e)
                return None
        
    def __search(self, pattern, type):
        if self.adv:
            return self._run_search_adv(pattern, type)
        else:
            return self._run_search(pattern, type)

    def search(self, pattern, type):
        self.cat=type
        if self.debug:
            return self.__search(pattern, type)
        else:
            try:
                return self.__search(pattern, type)
            except Exception, e:
                print self.shortname + " error:  " + str(e)
                return False
            
    def _get_rss_fake(self, type):
        '''build data object of single category (only 1 page)'''
        uri=self.url+"/cat/"+self.cats[type]
        result=httplib2.Http()
        resp,content=result.request(uri, 'GET')
        
        #self._get_data(content.decode("utf-8"))
        self._get_data(content)

    def _get_rss(self,type):
        uri=self.url+'/rsscat.php?cat='+self.cats[type]
        result=httplib2.Http()
        resp,content=result.request(uri, 'GET')
        parsedRss = feedparser.parse(content)

        if self.debug:
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.logfile = self.log_dir+"/"+self.shortname+"-rss-"+type+"-"+now+".xml"
            logfile = open(self.logfile, "w")
            logfile.write(content)
            logfile.close()

        for i in parsedRss.entries:
            newitem = Item()
            newitem.name = i['title']
            newitem.link = i['link']
            newitem._set_id(newitem.link)
            newitem.size = 0
            newitem.compl = newitem.nodata
            newitem.seed = newitem.nodata
            newitem.leech = newitem.nodata
            newitem.type = self.cats[type]
            
            self.list.append(newitem)
        return uri
    
    def getFeed(self, type):
        #try:
            return self._get_rss(type)
        #except Exception, e:
        #    print self.shortname +" error:  " + str(e)
