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

use_pwd = True
import urllib, datetime, httplib2, base
from BeautifulSoup import BeautifulSoup


class Item(base.BaseItem):
    def __init__(self,name,desc,weblink,size,seeders,leechers,completed):
        self.name = name + " " + desc
        self.date = None
        self.link = weblink
        self.size = base.getBytes(size+" GB")
        self.id = self.link.split("=")[1]
        self.seed = seeders
        self.leech = leechers
        self.compl = completed
        self.magnet = None
        self.files = None
        self.torrent_link = None
        self.hashvalue = None
        self.idate = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

    def _convert_date(self, string):
        date=string
        j=date.index(',')
        date=date[:j].rstrip().lstrip()
        month,day,year=date.split(' ')
        month=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'].index(month)+1
        day=eval(day)
        year=eval(year)
        #time=date[j+1:].rstrip().lstrip()
        #meridiem=time.split(' ')[1]
        #time=time.split(' ')[0]
        #if meridiem == "PM":
        #    hour=time.split(':')[0]
        #    hour=int(hour)+12
        #    if hour==24:
        #        hour==0
        #else:
        #    hour=time.split(':')[0]
        #minutes=time.split(':')[1]
            
        newdate=datetime.date(year,month,day)
        self.date=newdate.strftime("%a, %d %b %Y %H:%M:%S GMT")
        return newdate

class Data(base.BaseData):
    def __init__(self, usr, pwd):
        self.username = usr
        self.password = pwd
        self.list = []
        self.url='http://forum.tntvillage.scambioetico.org'
        self.name="tnt village"
        self.shortname="TNT"
        self.cookie="None"
        self.cats = {
            "all":"0",
            "film":"4",
            "anime":"7",
            "serie":"29",
            "cartoni":"8",
            "book-e":"3",
            "book-a":"34",
            "fumetti":"30",
            "teatro":"23",
            "musica":"2",
            "apps-linux":"6",
            "documentari":"14"
            }
        self.cat="all"

    def _try_login(self):
        c=httplib2.Http()
        resp,content=c.request(self.url + '/index.php?act=Login&CODE=00')
        data=urllib.urlencode({'UserName':self.username,'PassWord':self.password,'CookieDate':'1','Privacy':'1','submit':'Connettiti al Forum'})
        headers={'Content-type':'application/x-www-form-urlencoded', 'Cookie':resp['set-cookie']}
        resp,content=c.request(self.url + "/index.php?act=Login&CODE=01","POST",data,headers)

        if 'set-cookie' in resp and 'member_id' in resp['set-cookie']:
            self.cookie=resp['set-cookie']
        else:
            return None

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
        resp,content=result.request(uri, 'POST', data, headers, redirections=5, connection_type=None)

        checkhtml = self._get_data(content)
        nextcheck = checkhtml.find('input',{'name':'next'})

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


    def _get_data(self, html):
        parsedHtml = BeautifulSoup(html,convertEntities=BeautifulSoup.HTML_ENTITIES)
        list = parsedHtml.findAll('tr',{'class':'row4'})
        for i in list:
            a = i.find('a')
            description = i.findAll('span',{'class':'copyright'})[1]
            desc = description.getText()                
            stats=i.findAll('td',{'class':'copyright'})
            name = a.getText()
            weblink = a.get('href')
            leech =  stats[0].getText().replace("[", "").replace("]", "")
            seed = stats[1].getText().replace("[", "").replace("]", "")
            comp = stats[2].getText().replace("[", "").replace("]", "")
            size = stats[3].getText().replace("[", "").replace("]", "")
            newitem = Item(name,desc,weblink,size,seed,leech,comp)
            self.list.append(newitem)
        return parsedHtml

    def get_detail_data(self, link):
        details = []
        detail=httplib2.Http()

        resp,content=detail.request(link, 'GET')
        parsedDetail = BeautifulSoup(content,convertEntities=BeautifulSoup.HTML_ENTITIES)

        #torrent link
        torrent_link = parsedDetail.find('a', {'title':'Scarica allegato'})

        #check if link work without login
        if torrent_link is None:
            if self.cookie == "None":
                self._try_login()
                print "##### make login #####"
            headers={'Content-type':'application/x-www-form-urlencoded','Cookie':self.cookie}
            resp,content=detail.request(link,headers=headers)
            parsedDetail = BeautifulSoup(content,convertEntities=BeautifulSoup.HTML_ENTITIES)
            torrent_link=parsedDetail.find('a', {'title':'Scarica allegato'})
        
        #date
        date=parsedDetail.find('span', {'class':'postdetails'}).getText().replace("Inviato il:","")
        
        #Details table
        details_table=torrent_link.findParent().findParent().findParent()
        details_tr=details_table.findAll('tr')

        ##### tab keys #####
        #Completati:
        #Dimensione:
        #Leechers:
        #seeders:
        #data ultimo seed:
        #info_hash:
        #Tracker:
        #Magnet:

        for i in details_tr:
            try:
                key=i.find('td').getText().rstrip().lstrip()
                value=i.findAll('td')[1]
                #Magnet
                if key=="Magnet:":
                    magnet=value.find('a').get('href')
                #info hash
                if key=="info_hash:":
                    hashvalue=value.getText()
            except:
                magnet=None
                hashvalue=None

        voidItem= Item("void","","http://void=void","0","0","0","0")
        voidItem._convert_date(date)
        voidItem.magnet = magnet
        voidItem.hashvalue = hashvalue
        voidItem.torrent_link = torrent_link.get('href')

        return voidItem

    def _get_rss(self, code):
        import feedparser
        parsedRss = feedparser.parse(code)
    
        for i in parsedRss.entries:
            name = i['title']
            link = i['link']
            rssdesc = i['description'].split("Desc:")[1]
            itemsDesc = BeautifulSoup(rssdesc,convertEntities=BeautifulSoup.HTML_ENTITIES).findAll('b')
            #desc = itemsDesc[0].text
            desc = ""
            size = itemsDesc[3].text
            seed = itemsDesc[1].text
            leech = itemsDesc[2].text
            compl = "x" #prendere dalla descrizione

            newitem = Item(name,desc,link,size,seed,leech,compl)
            newitem.date = i['published']
            newitem.torrent_link = i.enclosures[0]['href']

            self.list.append(newitem)


    def search(self, pattern, type):
        self._try_login()
        cat=self.cats[type]
        self._run_search(pattern,cat)

    def getCategory(self, type):
        pass

    def getFeed(self, type):
        numitem="20"
        self.cat=type
        try:
            uri= 'http://www.tntvillage.scambioetico.org/rss.php?c=' + self.cats[type] + "&p=" + numitem
            result=httplib2.Http()
            resp,content=result.request(uri, 'GET')
            self._get_rss(content)
        except:
            pass

