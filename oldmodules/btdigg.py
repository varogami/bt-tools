#bt-tools - tools to interact with some bittorrent sites by commandline
#modified by qbittorrent ( http://www.qbittorrent.org/ ) search plugin
#Copyright (C) 2015 varogami <varogami@autistici.org>

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
m_url = 'https://btdigg.org'
#m_url = 'http://btdigg63cdjmmmqj.onion/'
#m_url = 'http://btdigg.i2p'
m_name = 'BTDigg'
m_shortname = 'BTD'
m_rss_light_download = True
m_cats = { 'all':'all'}
m_default_cat='all'
        
import urllib, urllib2, httplib2
from BeautifulSoup import BeautifulSoup
from modules import utils
from datetime import datetime

class Item:
    def __init__(self,name,weblink,size):
        self.name = name
        self.link = weblink
        self.size = size
        self.seed = None
        self.leech = None
        self.torrent_link = None
        self.hashvalue = None
        self.idate = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S UTC")
        self.id = None
        self.magnet = None
        self.files = None
        self.compl = None
        self.torrent_link_alt1 = None
        self.torrent_link_alt2 = None
        self.descr = None
                
class Data:
    def __init__(self, debug = False):
        self.list = []
        self.url = m_url
        self.name = m_name
        self.shortname = m_shortname
        self.cats= m_cats
        self.cat = m_default_cat
        self.debug = debug
        self.rss_light_download = m_rss_light_download
        
    def makeVoidItem(self):
        return Item("void","https://void","0")

    def search(self, what, cat='all'):
        self.cat = cat
        #self._api_search(what)
        self._search(what)

    def _search(self, what):
        result=httplib2.Http()
        data={'search':pattern}
        data=urllib.urlencode(data)
        uri=self.url + "/argh.php?" + data
        resp,content=result.request(uri, 'GET')
        parsedHtml = BeautifulSoup( html, convertEntities = BeautifulSoup.HTML_ENTITIES)

    def _api_search(self, what):
        req = what.replace('+', ' ')
        try:
            api_link=self.url.replace("://","://api.")
            #u = urllib2.urlopen('https://api.btdigg.org/api/public-8e9a50f8335b964f/s01?%s' % (urllib.urlencode(dict(q = req)),))
            u = urllib2.urlopen( api_link + '/api/public-8e9a50f8335b964f/s01?%s' % (urllib.urlencode(dict(q = req)),))
            try:
                for line in u:
                    if line.startswith('#'):
                        continue

                    info_hash, name, files, size, dl, seen = line.strip().split('\t')[:6]
                    name = name.translate(None, '|')
                    link = 'magnet:?xt=urn:btih:%s&dn=%s' % (info_hash, urllib.quote(name))
                    desc_link = '%s/search?%s' % (self.url, urllib.urlencode(dict(info_hash = info_hash, q = req)),)
                
                    if utils.search_words_case_insens(what, name):
                        newitem = Item(name.decode('utf-8'), desc_link, size)
                        newitem.id = info_hash
                        newitem.hashvalue = info_hash
                        newitem.magnet = link
                        newitem.files = str(files)
                        newitem.compl = str(dl)
                        newitem.date = datetime.fromtimestamp(int(seen)).strftime("%a, %d %b %Y %H:%M:%S GMT")
                        self.list.append(newitem)
            finally:
                u.close()
        except urllib2.HTTPError, e:
                print self.shortname +" http error:  " + str(e.code)
        except urllib2.URLError, e:
                print self.shortname +" url error:  " + str(e.args)

    def get_detail_data(self, link):
        pass

    def getCategory(self, type):
        pass

    def getFeed(self, type):
        pass

    def get_torrent_file(self, item):
        pass
