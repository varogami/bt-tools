import urllib, httplib2, time
from BeautifulSoup import BeautifulSoup
from datetime import datetime
from lib import utils

class Config:
    def __init__(self):
        self.enabled = True
        self.url = 'http://forum.tntvillage.scambioetico.org'
        self.name="tnt village"
        self.username = "INSERT USERNAME"
        self.password = "INSERT PASSWORD"
        self.rss_light_download = True
        self.num_rss_item = 20
        self.default_cat = 'all'
        self.cats = {
            "all":"0",
            "programmi_tv":"1",
            "music":"2",
            "books":"3",
            "movie":"4",
            "apps_linux":"6",
            "anime":"7",
            "cartoons":"8",
            "apps_mac":"9",
            "apps_win":"10",
            "games_pc":"11",
            "games_playstation_2":"12",
            "apps_students_release":"13",
            "movie_documentary":"14",
            "movie_music":"21",
            "sport":"22",
            "movie_theater":"23",
            "wrestling":"24",
            "other":"25",
            "games_xbox":"26",
            "immagini_sfondi":"27",
            "games_other":"28",
            "tv":"29",
            "comics":"30",
            "trash":"31",
            "games_playstation_1":"32",
            "games_psp_portable":"33",
            "books_audio":"34",
            "podcast":"35",
            "books_edicola":"36",
            "apps_mobile":"37"    
        }

class Item:
    def __init__(self):
        self.name = None
        self.date = None #date when bittorrent was load to website
        self.link = None
        self.size = None
        self.id = None
        self.seed = None
        self.leech = None
        self.compl = None
        self.magnet = None
        self.torrent_link = None
        self.hashvalue = None
        self.idate = int(time.time()) #datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S UTC")
        self.type = None
        self.object = None
        self.html = None
        self.files = None
        self.torrent_link_alt1 = None
        self.torrent_link_alt2 = None
        self.descr = None

    def _set_size(self,size):
        self.size = utils.getBytes(size+" GB")
        
    def _set_id(self, link):
        self.id = link.split("=")[1]
        
    def _set_date(self, date):
        months = { "Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12 }
        MDY = date.split(",")[0]
        HMM = date.split(",")[1]
        month_w, day, year = MDY.split(' ')
        month=months[month_w]
        space, HM, meridiem = HMM.split(' ')
        hour = HM.split(":")[0]
        minutes = HM.split(":")[1]
        if meridiem == "PM":
            hour=int(hour)+12
            if hour==24:
                hour==0                   
        newdate = datetime(int(year),int(month),int(day),int(hour),int(minutes))
        self.date = newdate.strftime("%a, %d %b %Y %H:%M:%S CET")
        
    def get_human_size(self):
        if self.size == '0':
            return "<10 Mb"
        else:
            return utils.sizeof(int(self.size))
    
class Data:
    def __init__(self, name, config, debug = False):
        self.shortname = name
        self.debug = debug
        self.username = config['username']
        self.password = config['password']
        self.list = []
        self.url = config['url']
        self.name = config['name']
        self.cookie = None
        self.cats = config['cats'] 
        self.cat = config['default_cat'] 
        self.rss_light_download = config['rss_light_download'] 
        self.num_rss_item = config['num_rss_item']
                               
    def _try_login(self):
        c=httplib2.Http()
        try:
            resp,content=c.request(self.url + '/index.php?act=Login&CODE=00')
            data=urllib.urlencode({'UserName':self.username,'PassWord':self.password,'CookieDate':'1','Privacy':'1','submit':'Connettiti al Forum'})
            headers={'Content-type':'application/x-www-form-urlencoded', 'Cookie':resp['set-cookie']}
            resp,content=c.request(self.url + "/index.php?act=Login&CODE=01","POST",data,headers)

            if 'set-cookie' in resp and 'member_id' in resp['set-cookie']:
                self.cookie=resp['set-cookie']
            
            if self.debug:
                print "DEBUG: try login with " + self.username
                if self.cookie is None:
                    print "DEBUG: none cookie"
                else:
                    print "DEBUG: got cookie - login maybe successful"

        except Exception, e:
            print self.shortname +" login error:  " + str(e)

    def _logout(self):
        if self.debug:
            print "DEBUG: logout"
        result=httplib2.Http()
        uri=self.url + "/index.php?act=Login&CODE=03"
        headers={'Cookie':self.cookie}
        resp,content=result.request(uri, 'GET', None, headers)

    def _run_search(self,pattern,cat,stp=0,stn=20,first_page=True):
        result=httplib2.Http()
        uri=self.url + "/index.php?act=allreleases"
        headers={'Content-type':'application/x-www-form-urlencoded','Cookie':self.cookie}
        data={'sb':'0', 'sd':'0', 'cat':str(cat), 'stn':str(stn), 'filter':pattern}

        if first_page:
            data['set']='Imposta filtro'
        else:
            data['next']="Pagine successive >>"
            data['stp']=str(stp)
        data=urllib.urlencode(data)
        
        try:
            resp,content=result.request(uri, 'POST', data, headers, redirections=5, connection_type=None)

            checkhtml = self._get_data(content, cat)
            nextcheck = checkhtml.find('input',{'name':'next'})
            if self.debug:
                print "DEBUG: run search and get html - first page " + str(first_page)
            try: 
                if nextcheck.get('name')=='next':
                    stn=checkhtml.find('input',{'name':'stn'})
                    stn=stn.get('value')
                    try:
                        stp=checkhtml.find('input',{'name':'stp'})
                        stp=stp.get('value')
                    except:
                        stp=0
                    self._run_search(pattern, cat, stp, stn, False)
            except:
                pass
            return True
        except Exception, e:
            print self.shortname +" search error:  " + str(e)
            return False


    def _get_data(self, html, cat):
        parsedHtml = BeautifulSoup(html,convertEntities=BeautifulSoup.HTML_ENTITIES)
        list = parsedHtml.findAll('tr',{'class':'row4'})
        for i in list:
            newitem = Item()
            
            a = i.find('a')
            description = i.findAll('span',{'class':'copyright'})[1]
            descr = description.getText()                
            stats = i.findAll('td',{'class':'copyright'})
            size = stats[3].getText().replace("[", "").replace("]", "")
            name = a.getText()

            newitem.name = name + " " + descr
            newitem.link = a.get('href')
            newitem._set_id(newitem.link)
            newitem.leech =  stats[0].getText().replace("[", "").replace("]", "")
            newitem.seed = stats[1].getText().replace("[", "").replace("]", "")
            newitem.compl = stats[2].getText().replace("[", "").replace("]", "")
            newitem._set_size(size)
            if cat == '0':
                img_cat = i.find('img')
                cat = img_cat.get('src').split('/')[2].split('.')[0].replace("icon","")
                newitem.type = cat
            else:
                newitem.type = cat
            
            self.list.append(newitem)
        return parsedHtml

    def get_detail_data(self, item_obj):
        detail=httplib2.Http()

        try:
            resp,content=detail.request(item_obj.link, 'GET')
            parsedDetail = BeautifulSoup(content,convertEntities=BeautifulSoup.HTML_ENTITIES)
            
            #check if link work without login
            torrent_link = parsedDetail.find('a', {'title':'Scarica allegato'})
            if torrent_link is None:
                if self.cookie is None:
                    self._try_login()
                    print "##### make login #####"
                headers={'Content-type':'application/x-www-form-urlencoded','Cookie':self.cookie}
                resp,content=detail.request( item_obj.link, headers=headers )
                parsedDetail = BeautifulSoup( content, convertEntities=BeautifulSoup.HTML_ENTITIES )
                torrent_link = parsedDetail.find('a', {'title':'Scarica allegato'})

            #GET DATA
            item_obj.torrent_link = torrent_link.get('href')
            date = parsedDetail.find('span', {'class':'postdetails'}).getText().replace("Inviato il:","")
            item_obj._set_date(date)
            
            #Details table
            details_table_src = torrent_link.findParent().findParent().findParent()
            details_table = details_table_src.findAll('tr')

            item_obj.magnet = details_table[0].findAll('a')[1].get('href')
            size = details_table[1].getText().split(":")[1] # kb - mb - gb....
            item_obj.size = utils.getBytes(size)
            item_obj.seed = details_table[2].getText().split(":")[1]
            item_obj.leech = details_table[3].getText().split(":")[1]
            item_obj.compl = details_table[4].getText().split(":")[1]
            date_last_seed = details_table[5].findAll("td")[1].getText() #maybe use in the future
            item_obj.hashvalue = details_table[6].getText().split(":")[1]
            item_obj.torrent_link_alt1 = utils.get_url_by_hash(item_obj.hashvalue, utils.link_torcache )
            item_obj.torrent_link_alt2 = utils.get_url_by_hash(item_obj.hashvalue, utils.link_zoink )

            #TODO - description
            #item_obj.descr = parsedDetail.findAll("div")[8]
            #file = open("/home/andrea/text.html", "w")
            #myhtml = parsedDetail.findAll("div")[8]
            #file.write(myhtml.prettify())
            #file.close()
            
        except Exception, e:
            print self.shortname + " error:  " + str(e)

    def _get_rss(self, code):
        import feedparser
        parsedRss = feedparser.parse(code)
    
        for i in parsedRss.entries:
            newitem = Item()
            newitem.name = i['title']
            newitem.link = i['link']
            rssdesc = i['description'].split("Desc:")[1]
            itemsDesc = BeautifulSoup(rssdesc,convertEntities=BeautifulSoup.HTML_ENTITIES).findAll('b')
            #desc = itemsDesc[0].text
            newitem.descr = ""
            newitem.size = itemsDesc[3].text
            newitem.seed = itemsDesc[1].text
            newitem.leech = itemsDesc[2].text
            newitem.compl = "x" #prendere dalla descrizione
            newitem.date = i['published']
            newitem.torrent_link = i.enclosures[0]['href']

            self.list.append(newitem)

    def search(self, pattern, type):
        if self.username == "INSERT USERNAME":
            print "tnt error: username and password not configured"
            return False
        else:
            if self.debug:
                print "DEBUG: search \"" + pattern + "\" in category \"" + type + "\""
            self._try_login()
            if self.cookie is not None:
                result = self._run_search(pattern,self.cats[type])
                self._logout()
                return result
            else:
                print self.shortname + " error:  none cookie - no login"
                return False

    def getCategory(self, type):
        for key, value in self.cats.iteritems():
            if value == type:
                return key

    def getFeed(self, type):
        self.cat = type
        try:
            uri= 'http://www.tntvillage.scambioetico.org/rss.php?c=' + self.cats[type] + "&p=" + str(self.num_rss_item)
            result=httplib2.Http()
            resp,content=result.request(uri, 'GET')
            self._get_rss(content)
        except Exception, e:
            print self.shortname + " error:  " + str(e)
            
    def get_torrent_file(self, item):
        utils.get_torrent_file(item, self.shortname,download_path)

