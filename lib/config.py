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

import json, os, sys, database


class Color:
    def __init__(self):
        #colors for shell
        self.grey = '\033[90m'
        self.red = '\033[91m'
        self.green = '\033[92m'
        self.yellow = '\033[93m'
        self.blu = '\033[94m'
        self.magenta = '\033[95m'
        self.cyan = '\033[96m'
        self.base = '\033[0m'

class Rss:
    def __init__(self):
        self.enabled = False
        self.dir =  None
        self.show_limit = 40    
        self.download_filtered = True
            
class Module:
    def __init__(self, ext_mod):
        self.__ext_mod = ext_mod
        self.list = self.__build_conf()
        
    def __build_conf(self):
        #load modules config from "modules" dir
        filepath = os.path.dirname(os.path.realpath(__file__))
        moddir = os.path.dirname(filepath) + "/modules"

        engines = {}
        self.__load_mods(moddir,engines)
        self.__load_mods(self.__ext_mod,engines)        
        return engines

    def __load_mods(self, modules_dir, engines):
        sys.path.append(modules_dir)
        print "  search modules in   - " + modules_dir
        for f in os.listdir(modules_dir):
            if os.path.isfile(os.path.join(modules_dir, f)):
                if f.endswith('.py'):
                    modname = f.replace('.py','')
                    module = __import__(modname)
                    print "    build default config of module - " + modname
                    engines[modname] = module.Config().__dict__
    
class Conky:
    def __init__(self):
        self.chars_to_print = 90
        self.rows_to_print = 6
        self.font = "Sans Mono:size=8"
        self.font_bold = "Sans Mono:bold:size=8"
        self.color1="color2"
        self.color2="color"
        self.color_line_even="color4"
        self.color_line_odd="color"

        
class Data:
    def __init__(self, moddir):
        self.conf_version = "0.0.1"
        self.export_file = "export-database.xml"
        self.torrent_client = "qbittorrent-nox"
        self.user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36"
        self.debug = False
        self.dir_cache = None #TODO
        self.dir_download = None #TODO
        self.browser = "w3m" #"dwv" "qupzilla" "midori"
        self.download_bt_file_only = True #TODO
        self.filter_download_file_only = True
        self.output_string_limit = 80 #used by bt-download
        self.date_format = "" #TODO
        self.rss = Rss().__dict__
        self.conky = Conky().__dict__
        self.module = Module(moddir).list
        self.links = {}
        self.links['torcache'] = "http://torcache.net/torrent/"
        self.links['zoink'] = "https://zoink.it/torrent/"

        
class Config:
    def __init__(self):
        self.__color = Color()
        self.__dir = os.environ['HOME'] + "/.config/bt-tools"
        self.__dir_mod =  self.__dir + "/modules"
        self.__dir_log =  self.__dir + "/log"       
        self.__file_conf = self.__dir + "/config.json"
        self.__file_db = self.__dir + "/database.sqlite"
        
        if not os.path.exists(self.__dir):
            print "config dir not exist  - create: " + self.__dir
            os.mkdir(self.__dir)
            
        if not os.path.exists(self.__dir_mod):
            print "modules dir not exist - create: " + self.__dir_mod
            os.mkdir(self.__dir_mod)
            
        if not os.path.exists(self.__dir_log):
            print "log dir not exist  - create: " + self.__dir_log
            os.mkdir(self.__dir_log)

        if not os.path.exists(self.__file_conf):
            print "config file not exist - build data "
            self.__data = Data(self.__dir_mod)
            self.__build_config()
        
        self.__load_new_mod_conf()
        print "load config           - " + self.__file_conf
        with open(self.__file_conf) as data_file:
            self.__json = json.load(data_file)            
        self.__debug = self.__json['debug']

        self.__db = database.Data(self.__file_db, self.__debug)
        
        if not os.path.exists(self.__file_db):
            self.__db.makeDb()
            
    def __build_config(self):
        print "write config json     - " + self.__file_conf
        DataFile = open(self.__file_conf, "w")
        data = json.dumps(self.__data.__dict__, indent=4, separators=(',', ': '), sort_keys=True)
        DataFile.write(data)
        DataFile.close()
                    
    def getColors(self):
        return self.__color

    def getJson(self):
        return self.__json

    def getLogDir(self):
        return self.__dir_log

    def getDebug(self):
        return self.__debug
    
    def load_mod(self, name, config, log_dir, user_agent):
        #load modules config from "modules" dir
        filepath = os.path.dirname(os.path.realpath(__file__))
        moddir = os.path.dirname(filepath) + "/modules"
        sys.path.append(moddir)
        sys.path.append(self.__dir_mod)

        if os.path.isfile(os.path.join(moddir, name+'.py')) or \
          os.path.isfile(os.path.join(self.__dir_mod, name+'.py')):
            module = __import__(name)
            return module.Data(name, config, log_dir, user_agent, self.__debug)
        else:
            print self.__color.red + "module " + name + " not found" + self.__color.base
            return None

    def __load_new_mod_conf(self):
        #check for new mod
        #if true load json - add new mod - save json
        pass
    

    def getDb(self):
        return self.__db
