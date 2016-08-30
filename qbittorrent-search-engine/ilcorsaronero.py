#! /usr/bin/python
# -*- coding=utf-8 -*-

#VERSION: 0.04
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
'Il Corsaro Nero plug-in for qBittorrent'

import urllib, datetime, os, time, httplib2, sys
from BeautifulSoup import BeautifulSoup

class ilcorsaronero(object):
    url = 'http://ilcorsaronero.info'
    name = 'ilcorsaronero' # spaces and special characters are allowed here             
    supported_categories = {'all': ''}

    def __init__(self):
        self.url = 'http://ilcorsaronero.info'

    def _run_search(self,pattern):
        result=httplib2.Http()
        data={'search':pattern}
        data=urllib.urlencode(data)
        uri=self.url + "/argh.php?" + data

        resp,content=result.request(uri, 'GET')

        self._get_html_data(content)

    def _get_html_data(self, html):
        parsedHtml = BeautifulSoup(html,convertEntities=BeautifulSoup.HTML_ENTITIES)

        list1 = parsedHtml.findAll('tr',{'class':'odd'})
        list2 = parsedHtml.findAll('tr',{'class':'odd2'})

        self._get_base_data(list1)
        self._get_base_data(list2)

    def _get_base_data(self, parsedlist):
        for i in parsedlist:
            name = i.find('a',{'class':'tab'}).getText()
            weblink = i.find('a',{'class':'tab'}).get('href')
            size = i.find('font').getText()
            size = self._tobyte(size)
            date = i.find('font',{'color':'#669999'}).getText()

            if i.find('font',{'color':'#00CC00'}):
                seed = i.find('font',{'color':'#00CC00'}).getText()
            if i.find('font',{'color':'#0066CC'}):
                leech = i.find('font',{'color':'#0066CC'}).getText()
            array = []
            self._get_details(weblink, array)
            magnet = array[0]
            print magnet+"|"+name+"|"+str(size)+"|"+seed+"|"+leech+"|"+self.url

    def _tobyte(self, sizehr):
        size = sizehr.split(" ")[0]
        if sizehr.find("GB") > 0:
            size = float(size) * 1024 * 1024 * 1024
        elif sizehr.find("MB") > 0:
            size = float(size) * 1024 * 1024 
        elif sizehr.find("KB") > 0:
            size = float(size) * 1024
        size = int(size)
        return size

    def _get_details(self, link, myarray):
        result=httplib2.Http()
        resp,content=result.request(link, 'GET')
        parsedDetails = BeautifulSoup(content,convertEntities=BeautifulSoup.HTML_ENTITIES)
        det_magnet = parsedDetails.find('a',{'class':'forbtn','target':'_blank'}).get('href')
        myarray.append(det_magnet)
        

    def search(self, pattern):
        self._run_search(pattern)
            

if __name__ == "__main__":
    s = ilcorsaronero()
    s.search(sys.argv[1])



