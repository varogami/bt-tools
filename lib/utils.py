#bt-tools - tools to interact with some bittorrent sites by commandline
#Copyright (C) 2015-2016  varogami <varogami@altervista.org>

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

link_torcache = "http://torcache.net/torrent/"
link_zoink = "https://zoink.it/torrent/"
db_date_format = ""

import re, httplib2, base64

def _get_torrent(link, namefile, download_path):
    myfile = download_path+"/"+namefile+".torrent"
    if link == None:
        success = False
    else:
        try:
            result=httplib2.Http()
            resp,content=result.request(link, 'GET')
            with open(myfile, 'wb') as f:
                f.write(content)
            success = True
        except:
            success = False
    return success
    
def get_torrent_file(item, shortname, download_path=None):
    if not item.torrent_link == None:
        link = item.torrent_link
    elif not item.torrent_link_alt1 == None:
        link = item.torrent_link_alt1
    elif not item.torrent_link_alt2 == None:
        link = item.torrent_link_alt2
    else:
        link = None
    success = _get_torrent(link, shortname+"-"+item.id, download_path)
    return success

def isodd(num):
    return num & 1 and True or False

def get_url_by_hash(bthash, link):
    return link + bthash.upper() + ".torrent"

def get_mag_by_hash(bthash):
    return "magnet:?xt=urn:btih:" + bthash

def get_hash_by_torcache_link(link):
    return link.split(".torrent")[0].split("/")[4].lower()

def getBytes(string):
    if string.find("TB") > 0:
        bytes = float(string.split(" ")[0]) * 1024 * 1024 * 1024 * 1024
    elif string.find("tb") > 0:
        bytes = float(string.split(" ")[0]) * 1024 * 1024 * 1024 * 1024
    elif string.find("GB") > 0:
        bytes = float(string.split(" ")[0]) * 1024 * 1024 * 1024
    elif string.find("gb") > 0:
        bytes = float(string.split(" ")[0]) * 1024 * 1024 * 1024
    elif string.find("MB") > 0:
        bytes = float(string.split(" ")[0]) * 1024 * 1024
    elif string.find("mb") > 0:
        bytes = float(string.split(" ")[0]) * 1024 * 1024
    elif string.find("KB") > 0:
        bytes = float(string.split(" ")[0]) * 1024
    elif string.find("kb") > 0:
        bytes = float(string.split(" ")[0]) * 1024
    else:
        bytes = float(string.split(" ")[0])
    return str(int(bytes))

def sizeof(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def search_words_case_insens(seek, string):
    """ case insensitive search ALL words in string """
    words=seek.split(" ")
    rng=len(words)
    if string == None:
        print "warning - database item is None!!"
        return True
    else:
        if rng == 1:
            if re.search(seek, string, re.IGNORECASE) is None:
                return False
            else:
                return True
        else:
            found=True
            for i in words:
                if re.search(i, string, re.IGNORECASE) is None:
                    found=False
            return found

#needed to create TNT magnet
def hashConvert(hashstring, type='32'):
    hash = hashstring.upper()
    data = base64.b16decode(hash)
    if type=='32':
        return base64.b32encode(data)
    elif type=='64': 
        return base64.b64encode(data)
