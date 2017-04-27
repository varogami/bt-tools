#bt-tools - tools to interact with some bittorrent sites by commandline
#Copyright (C) 2015-2017 varogami <varogami@altervista.org>

#Some source code from qbittorrent script by "Diego de las Heras" <ngosang@hotmail.es>
#https://github.com/qbittorrent/qBittorrent/wiki/Unofficial-search-plugins

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

import urllib, httplib2, feedparser
try:
    from BeautifulSoup import BeautifulSoup
except Exception, e:
    from bs4 import BeautifulSoup

from datetime import datetime
from lib import module
from lib import utils

class Config(module.Config):
    def __init__(self):
        self.enabled = True
        self.url = 'http://forum.tntvillage.scambioetico.org'
        self.url_nl = 'http://www.tntvillage.scambioetico.org'
        self.name="tnt village"
        self.username = "INSERT USERNAME"
        self.password = "INSERT PASSWORD"
        self.default_cat = 'all'
        self.search_type = 'nologin'
        self.cats = {
            "all":"0",
            "tv_misc":"1",
            "music":"2",
            "book":"3",
            "movie":"4",
            "app_linux":"6",
            "anime":"7",
            "cartoon":"8",
            "app_mac":"9",
            "app_win":"10",
            "game_pc":"11",
            "game_psx2":"12",
            "app_student":"13",
            "movie_doc":"14",
            "movie_music":"21",
            "sport":"22",
            "movie_theater":"23",
            "wrestling":"24",
            "other":"25",
            "game_xbox":"26",
            "image_wall":"27",
            "game_other":"28",
            "tv":"29",
            "comic":"30",
            "trash":"31",
            "game_psx1":"32",
            "game_psp":"33",
            "book_audio":"34",
            "podcast":"35",
            "book_edicola":"36",
            "app_mobile":"37"    
        }
        self.rss = {
            "url" : "http://www.tntvillage.scambioetico.org/rss.php?c=",
            "num_item" : "20",
            "enabled" : False,
            "feeds" : [
                "movie", "tv"
            ]
        }

class Item(module.Item):
    def _set_size(self,size):
        self.size = utils.getBytes(size+" GB"
        )
    def _set_size_rss(self, size):
        fixed_size = size.replace(",","")
        self.size = utils.getBytes(fixed_size)
        
    def _set_id(self, link):
        self.id_module = link.split("=")[1]
        
    def _set_date(self, date):
        try:
            months = { "Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12 }
            MDY = date.split(",")[0]
            HMM = date.split(",")[1]
            space, month_w, day, year = MDY.split(' ')
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
        except:
            print "ERROR with date " + date
            self.date = None
            
    def get_human_size(self):
        if self.size == '0':
            return "<10 Mb"
        else:
            return utils.sizeof(int(self.size))
    
class Data(module.Data):
    def __init__(self, name, config, log_dir, user_agent, debug = False):
        module.Data.__init__(self,name,config,log_dir,user_agent,debug)
        self.username = config['username']
        self.password = config['password']
        self.search_type = config['search_type']
        self.cookie = None
        self.rss_conf = config['rss']
        self.__mod_conf = config
                               
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
            
        result = httplib2.Http()
        uri = self.url + "/index.php?act=Login&CODE=03"
        headers = {'Cookie':self.cookie}
        resp,content = result.request(uri, 'GET', None, headers)

        
    def _run_search(self,pattern,cat,stp=0,stn=20,first_page=True):
        result = httplib2.Http()
        uri = self.url + "/index.php?act=allreleases"
        headers = {'Content-type':'application/x-www-form-urlencoded','Cookie':self.cookie}
        data = {'sb':'0', 'sd':'0', 'cat':str(cat), 'stn':str(stn), 'filter':pattern}

        if first_page:
            data['set'] = "Imposta filtro"
        else:
            data['next'] = "Pagine successive >>"
            data['stp'] = str(stp)
            
        data=urllib.urlencode(data)
        
        try:
            resp,content=result.request(uri, 'POST', data, headers, redirections=5, connection_type=None)
            if self.debug:
                print "DEBUG: search - pattern \"" + pattern + "\" - cat " + cat + " - stp " + str(stp) + " - stn " + str(stn) + " - first page " + str(first_page)
                now = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.logfile = self.log_dir+"/"+self.shortname+"-search-"+pattern+"-"+cat+"-"+str(stp)+"-"+str(stn)+"-"+str(first_page)+"-"+now+".html"
            
            parsed = self._get_data(content, cat)

            if parsed is not None:
                have_next_page = parsed.find('input',{'name':'next'})

                try: 
                    if have_next_page.get('name')=='next':
                        stn=parsed.find('input',{'name':'stn'})
                        stn=stn.get('value')
                        try:
                            stp=parsed.find('input',{'name':'stp'})
                            stp=stp.get('value')
                        except:
                            stp=0
                        self._run_search(pattern, cat, stp, stn, False)
                except:
                    pass
                return True
            else:
                return False
        except Exception, e:
            print self.shortname +" search error:  " + str(e)
            return False


    def _get_data(self, html, cat):
        try:
            parsedHtml = BeautifulSoup(html,convertEntities=BeautifulSoup.HTML_ENTITIES) 
        except:
            parsedHtml = BeautifulSoup(html,'html.parser') #bs4

        not_registered_string = "Spiacente ma devi essere registrato per visualizzare questa pagina"
        overload_string = "Accesso ridotto allo Staff e nei gruppi di Releaser e Donatori"
        
        if html.find(not_registered_string) > 0:
            print self.shortname +" search error:  " + not_registered_string
        elif html.find(overload_string) > 0:
            print self.shortname +" search error:  " + overload_string
        else:
            if self.debug:
                logfile = open(self.logfile, "w")
                logfile.write(parsedHtml.prettify().encode("UTF-8"))            
                logfile.close()
            
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
                    newitem.type = img_cat.get('src').split('/')[2].split('.')[0].replace("icon","")
                else:
                    newitem.type = cat
                
                self.list.append(newitem)
            return parsedHtml
        
    def _run_search_nologin(self, pattern, cat="all"):
        result = httplib2.Http()
        uri = self.url + "/src/releaselist.php"
        headers = {"Content-type": "application/x-www-form-urlencoded", "X-Requested-With": "XMLHttpRequest"}

        i = 1
        while i < 15:
            data = {'cat':str(cat), 'page':str(i), 'srcrel':pattern}
            data=urllib.urlencode(data)
            success=True
            try:
                resp,content=result.request(uri, 'POST', data, headers, redirections=5, connection_type=None)
                if self.debug:
                    print "DEBUG: search nologin type - pattern \"" + pattern + "\" - cat " + cat + " - count " + str(i)
                    now = datetime.now().strftime("%Y%m%d_%H%M%S")
                    self.logfile = self.log_dir+"/"+self.shortname+"-search-nl-"+pattern+"-"+cat+"-"+str(i)+"-"+now+".html"
                parsed = self._get_data_nl(content, cat)               
                i += 1
            except:
                success=False
                print self.shortname +" search error:  " + str(e)
                break
            if parsed is None:
                break
        return success


    def _get_data_nl(self, html, cat):
        try:
            parsedHtml = BeautifulSoup(html,convertEntities=BeautifulSoup.HTML_ENTITIES) 
        except:
            parsedHtml = BeautifulSoup(html,'html.parser') #bs4
        
        if self.debug:
            logfile = open(self.logfile, "w")
            logfile.write(parsedHtml.prettify().encode("UTF-8"))            
            logfile.close()

        table = parsedHtml.find('div',{'class':'showrelease_tb'})
        list = table.findAll('tr')

        if len(list) < 2:
            return None
        else:
            for i in list:
                newitem = Item()

                list_data = i.findAll('td')
                list_link = i.findAll('a')

                if list_data[0].getText() != "T":    
                    newitem.torrent_link = list_link[0].get('href')
                    newitem.magnet = list_link[1].get('href')
                    newitem.link = list_link[3].get('href')
                    newitem.name = list_data[6].getText()
                    newitem._set_id(newitem.link)
                    newitem.leech = list_data[3].getText()
                    newitem.seed = list_data[4].getText()
                    newitem.compl = list_data[5].getText()
                    newitem.size = "0"
                    
                    if cat == '0':
                        img_cat = i.find('img')
                        newitem.type = list_link[2].get('href').split('cat=')[1]
                    else:
                        newitem.type = cat
                    self.list.append(newitem)
            return table
    
    def search(self, pattern, type):
        if self.search_type == "login":
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
        elif self.search_type == "nologin":
            self.url = self.__mod_conf['url_nl']
            result = self._run_search_nologin(pattern,self.cats[type])
            if result is not None:
                return result
            else:
                return False
        else:
            print self.shortname + " error:  "+self.search_type+" is wrong type - try: login or nologin in configuration file"
            

    def get_detail_data(self, item):
        detail=httplib2.Http()
        if self.debug:
            print "DEBUG: get detail data of - id " + str(item.id) + " - id module " + str(item.id_module) 
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.logfile = self.log_dir+"/"+self.shortname+"-detail_data-id"+str(item.id_module)+"-"+now+".html"

        try:
            resp,content=detail.request(item.link, 'GET')
            try:
                parsedDetail = BeautifulSoup(content,convertEntities=BeautifulSoup.HTML_ENTITIES) 
            except:
                parsedDetail = BeautifulSoup(content,'html.parser') #bs4

            if self.debug:
                logfile = open(self.logfile, "w")
                logfile.write(parsedDetail.prettify().encode("UTF-8"))            
                logfile.close()

            #check if link work without login
            torrent_link = parsedDetail.find('a', {'title':'Scarica allegato'})
            if torrent_link is None:
                if self.cookie is None:
                    self._try_login()
                    if self.debug:
                        print "DEBUG: make login because link need authentication"
                headers={'Content-type':'application/x-www-form-urlencoded','Cookie':self.cookie}
                resp,content=detail.request( link, headers=headers )

                try:
                    parsedDetail = BeautifulSoup(content,convertEntities=BeautifulSoup.HTML_ENTITIES) 
                except:
                    parsedDetail = BeautifulSoup(content,'html.parser') #bs4
                    
                torrent_link = parsedDetail.find('a', {'title':'Scarica allegato'})

                if self.debug:
                    self.logfile = self.log_dir+"/"+self.shortname+"-detail_data-id"+str(item.id_module)+"-"+now+"-with-login.html"
                    logfile = open(self.logfile, "w")
                    logfile.write(parsedDetail.prettify().encode("UTF-8"))            
                    logfile.close()

                
            #GET DATA
            item.torrent_link = torrent_link.get('href')
            if self.debug:
                print "DEBUG: torrent link:" + item.torrent_link
                
            date = parsedDetail.find('span', {'class':'postdetails'}).getText().replace("Inviato il:","")
            if self.debug:
                print "DEBUG: date:" + date

            tmp_item = Item()
            tmp_item._set_date(date)
            item.date = tmp_item.date
            if self.debug:
                print "DEBUG: date formatted:" + item.date

                
            #Details table
            details_table_src = torrent_link.findParent().findParent().findParent()
            details_table = details_table_src.findAll('tr')

            item.magnet = details_table[0].findAll('a')[1].get('href')
            if self.debug:
                print "DEBUG: magnet:" + item.magnet
                
                
            size = details_table[1].getText().split(":")[1] # kb - mb - gb....
            fix_size = size.split(' ')[1] + " " + size.split(' ')[2]
            if self.debug:
                print "DEBUG: size:" + size
                print "DEBUG: fix_size:" + fix_size

            item.size = utils.getBytes(fix_size)
            item.seed = details_table[2].getText().split(":")[1]
            item.leech = details_table[3].getText().split(":")[1]
            item.compl = details_table[4].getText().split(":")[1]
            date_last_seed = details_table[5].findAll("td")[1].getText() #maybe use in the future
            item.hashvalue = details_table[6].getText().split(":")[1]
            #item.add_torrent_link(utils.get_url_by_hash(item.hashvalue, utils.link_torcache ))
            #item.add_torrent_link(utils.get_url_by_hash(item.hashvalue, utils.link_zoink ))
            #item.html = content
            
            #TODO - description
            #item.descr = parsedDetail.findAll("div")[8]
            #file = open("/home/andrea/text.html", "w")
            #myhtml = parsedDetail.findAll("div")[8]
            #file.write(myhtml.prettify())
            #file.close()

            

            return item
        except Exception, e:
            print self.shortname + " error:  " + str(e)
            return None

    def _get_rss(self, code, type):
        parsedRss = feedparser.parse(code)
    
        for i in parsedRss.entries:
            newitem = Item()
            newitem.name = i['title']
            newitem.link = i['link']
            rssdesc = i['description'].split("Desc:")[1]
            itemsDesc = BeautifulSoup(rssdesc,convertEntities=BeautifulSoup.HTML_ENTITIES).findAll('b')
            try:
                itemsDesc = BeautifulSoup(rssdesc,convertEntities=BeautifulSoup.HTML_ENTITIES).findAll('b') 
            except:
                itemsDesc = BeautifulSoup(rssdesc,'html.parser').findAll('b') #bs4 

            #desc = itemsDesc[0].text
            #newitem.name = name + " " + descr            
            size = itemsDesc[3].text
            newitem.seed = itemsDesc[1].text
            newitem.leech = itemsDesc[2].text
            newitem.compl = newitem.nodata
            newitem.date = i['published']
            newitem.torrent_link = i.enclosures[0]['href']
            newitem._set_id(newitem.link)
            newitem._set_size_rss(size)
            newitem.type = type
                        
            self.list.append(newitem)


    def __get_feed(self,type):
        uri= self.rss_conf['url'] + str(self.__mod_conf["cats"][type]) + "&p=" + str(self.rss_conf['num_item'])
        result=httplib2.Http()
        resp,content=result.request(uri, 'GET')

        if self.debug:
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.logfile = self.log_dir+"/"+self.shortname+"-rss-"+type+"-"+now+".xml"
            logfile = open(self.logfile, "w")
            logfile.write(content)
            logfile.close()

        self._get_rss(content, self.__mod_conf["cats"][type])
        return uri

    def getFeed(self, type):
        if self.debug:
            return self.__get_feed(type)
        else:
            try:
                return self.__get_feed(type)
            except Exception, e:
                print self.shortname + " error:  " + str(e)
                return ""
            

