#! /usr/bin/python
# -*- coding=utf-8 -*-

#VERSION: 0.02
#AUTHORS: varo (varogami@gmail.com)
#
#                    GNU GENERAL PUBLIC LICENSE
#                       Version 3, 29 June 2007
#
#                   <http://www.gnu.org/licenses/>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
'TNT Village plug-in for qBittorrent'

import urllib, datetime, os, time, httplib2, sys
from BeautifulSoup import BeautifulSoup


class tntvillage(object):
    url = 'http://forum.tntvillage.scambioetico.org'
    name = 'tntvillage' # spaces and special characters are allowed here
    supported_categories = {'all': ''}
    def __init__(self):
        self.username="INSERT USERNAME"
        self.password="INSERT PASSWORD"
        self.url='http://forum.tntvillage.scambioetico.org'

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

    def _run_search(self,pattern,stp=0,stn=20,first_page=True):
        result=httplib2.Http()
        uri=self.url + "/index.php?act=allreleases"
        headers={'Content-type':'application/x-www-form-urlencoded','Cookie':self.cookie}
        data={'sb':'0', 'sd':'0', 'cat':'0', 'stn':str(stn), 'filter':pattern}

        if first_page:
            data['set']='Imposta filtro'
        else:
            data['next']="Pagine successive >>"
            data['stp']=str(stp)

        data=urllib.urlencode(data)
        resp,content=result.request(uri, 'POST', data, headers, redirections=5, connection_type=None)

        checkhtml = self._put_html_data(content)
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
                self._run_search(pattern, stp, stn, False)
        except:
            pass

    def _put_html_data(self, html):
        parsedHtml = BeautifulSoup(html,convertEntities=BeautifulSoup.HTML_ENTITIES)
        list = parsedHtml.findAll('tr',{'class':'row4'})
        for i in list:
            a = i.find('a')
            name = a.getText()
            description = i.findAll('span',{'class':'copyright'})[1]
            desc = description.getText()
            name = name + " " + desc
            weblink = a.get('href')
            stats=i.findAll('td',{'class':'copyright'})
            leech =  stats[0].getText().replace("[", "").replace("]", "")
            seed = stats[1].getText().replace("[", "").replace("]", "")
            size = stats[3].getText().replace("[", "").replace("]", "")
            size = float(size) * 1024 * 1024 * 1024
            size = int(size)
            link = self._get_details(weblink)
            print link+"|"+name+"|"+str(size)+"|"+seed+"|"+leech+"|"+self.url
        return parsedHtml


    def _get_details(self, link):
        detail=httplib2.Http()
        headers={'Content-type':'application/x-www-form-urlencoded','Cookie':self.cookie}
        resp,content=detail.request(link,headers=headers)
        parsedDetail = BeautifulSoup(content,convertEntities=BeautifulSoup.HTML_ENTITIES)
        
        #torrent link
        torrent_link=parsedDetail.find('a', {'title':'Scarica allegato'})

        details_table=torrent_link.findParent().findParent().findParent()
        details_tr=details_table.findAll('tr')

        for i in details_tr:
            try:
                key=i.find('td').getText().rstrip().lstrip()
                value=i.findAll('td')[1]
        #Magnet
                if key=="Magnet:":
                    magnet=value.find('a').get('href')
            except:
                pass
        return torrent_link.get('href')

    def search(self, what, cat='all'):
        try:
            self._try_login()
        except:
            print "connection error"
        self._run_search(what)
            

if __name__ == "__main__":
    s = tntvillage()
    s.search(sys.argv[1])




