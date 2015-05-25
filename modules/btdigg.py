#bt-tools - tools to interact with some bittorrent sites by commandline
#modified by qbittorrent ( http://www.qbittorrent.org/ ) search plugin
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
import urllib, urllib2, datetime, re, base

class Item(base.BaseItem):
    def __init__(self,name,weblink,size):
        self.name = name
        self.link = weblink
        self.size = size
        self.seed = None
        self.leech = None
        self.torrent_link = None
        self.hashvalue = None
        self.idate = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

class Data(base.BaseData):
    def __init__(self):
        self.list = []
        self.url='https://btdigg.org'
        self.name='BTDigg'
        self.shortname='BTD'
        self.cats={ 'all':'all'}
        self.cat='all'

    def search(self, what, cat='all'):
        req = what.replace('+', ' ')
        try:
            u = urllib2.urlopen('https://api.btdigg.org/api/public-8e9a50f8335b964f/s01?%s' % (urllib.urlencode(dict(q = req)),))
            try:
                for line in u:
                    if line.startswith('#'):
                        continue

                    info_hash, name, files, size, dl, seen = line.strip().split('\t')[:6]
                    name = name.translate(None, '|')
                    link = 'magnet:?xt=urn:btih:%s&dn=%s' % (info_hash, urllib.quote(name))
                    desc_link = '%s/search?%s' % (self.url, urllib.urlencode(dict(info_hash = info_hash, q = req)),)
                
                    if base.search_words_casei(what, name):
                        newitem = Item(name.decode('utf-8'), desc_link, size)
                        newitem.id = info_hash
                        newitem.hashvalue = info_hash
                        newitem.magnet = link
                        newitem.files = str(files)
                        newitem.compl = str(dl)
                        newitem.date = datetime.datetime.fromtimestamp(int(seen)).strftime("%a, %d %b %Y %H:%M:%S GMT")
                        self.list.append(newitem)
            finally:
                u.close()

        except urllib2.HTTPError, e:
                print self.shortname +" http error:  " + str(e.code)
        except urllib2.URLError, e:
                print self.shortname +" url error:  " + str(e.args)
