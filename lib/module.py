import utils, time
from collections import namedtuple

class Config(object):
    def __init__(self):
        self.enabled = True
        self.url = 'http://test.test'
        self.name="name of module"
        self.default_cat = 'all'
        self.cats = {
            "all":"all",
            "music":"music",
            "movie":"movie",
            "apps_win":"software",
            "games_pc":"games"
        }

class Item(object):
    def __init__(self):
        self.name = None
        self.module = None
        self.id_module = None
        self.link_module = None
        self.date = None 
        self.link = None
        self.size = None
        self.id = None
        self.seed = None
        self.leech = None
        self.compl = None
        self.magnet = None
        self.torrent_link = None
        self.hashvalue = None
        self.idate = int(time.time()) 
        self.type = None
        self.data = None 
        self.html = None
        self.nodata = "x"
        
    def add_torrent_link(self, url):
        if self.data is None:
            self.data = {}
            self.data['torrent_links'] = []
        self.data['torrent_links'].append(url)

    def add_generic_item(self, name, value):
        if self.data is None:
            self.data = {}
            self.data[name] = []
        self.data[name].append(value)


    def _set_data(self, name, descr):
        if self.data is None:
            self.data = {}
        self.data[name] = descr

    def get_human_size(self):
        if self.size == "0" or self.size == 0:
            return "x byte"
        else:
            return utils.sizeof(int(self.size))

    def update_idate(self):
        self.idate = int(time.time())


class Data(object):
    def __init__(self, name, config, log_dir, user_agent, debug = False):
        self.shortname = name
        self.debug = debug
        self.list = []
        self.url = config['url']
        self.name = config['name']
        self.cats = config['cats'] 
        self.cat = config['default_cat']
        self.user_agent = user_agent
        self.log_dir = log_dir

    def get_detail_data(self, item):
        """
        Return detailed info of torrent. Must be overwritten in subclass.
        """
        raise NotImplementedError("This method must be overwritten")
        
    def get_torrent_file(self, item):
        """
        Get and download torrent. Must be overwritten in subclass.
        """
        raise NotImplementedError("This method must be overwritten")

    def search(self, pattern, type):
        """
        Search torrent by pattern and type. Must be overwritten in subclass.
        """
        raise NotImplementedError("This method must be overwritten")

    def getFeed(self, type):
        """Get Feed. Must be overwritten in subclass."""
        raise NotImplementedError("This method must be overwritten")

    def getCount(self):
        return str(len(self.list))

    def get_torrent_file(self, item):
        utils.get_torrent_file(item, self.shortname)
