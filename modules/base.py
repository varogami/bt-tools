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

use_pwd = False
import re

def getBytes(string):
    if string.find("TB") > 0:
        bytes = float(string.split(" ")[0]) * 1024 * 1024 * 1024 * 1024
    elif string.find("GB") > 0:
        bytes = float(string.split(" ")[0]) * 1024 * 1024 * 1024
    elif string.find("MB") > 0:
        bytes = float(string.split(" ")[0]) * 1024 * 1024
    elif string.find("KB") > 0:
        bytes = float(string.split(" ")[0]) * 1024
    else:
        bytes = float(string.split(" ")[0])
    return str(int(bytes))

def sizeof(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def search_words_casei(seek, string):
    words=seek.split(" ")
    rng=len(words)
    if rng == 1:
        if re.search(seek, string, re.IGNORECASE) is None:
            return False
        else:
            return True
    else:
        found=True
        for i in range(rng):
            if re.search(words[i], string, re.IGNORECASE) is None:
                found=False
        return found

def hashConvert(hashstring, type='32'):
    #needed to create TNT magnet
    hash = hashstring.upper()
    import base64
    data = base64.b16decode(hash)
    if type=='32':
        return base64.b32encode(data)
    elif type=='64': 
        return base64.b64encode(data)


class BaseItem:
    def __init__(self,name,weblink):
        self.name = name
        self.date = date
        self.link = weblink
        self.size = None
        self.id = None
        self.magnet = None
        self.torrent_link = None
        self.files = None
        self.seed = None
        self.leech = None
        self.compl = None
        self.hashvalue = None

class BaseData:
    def __init__(self):
        self.list = []
        self.url='http://www.link.org'
        self.name='name site'
        self.shortname='NMS'
        self.cats = {
            "film":"film",
            "anime":"anime",
            "serie":"serie"
            }
        self.cat="all"
        
        
    def get_detail_data(self, link):
        pass

    def search(self, pattern, type):
        pass

    def getCategory(self, type):
        pass

    def getFeed(self, type):
        pass

    def lscat(self):
        import operator
        catsorted = sorted(self.cats.iteritems(), key=operator.itemgetter(0))
        print self.name +":"
        for i in catsorted:
            print i[0]
        print

