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

import json, os, sys, database, common


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

            
class Module:
    def __init__(self, ext_mod, mod_conf, debug = False):
        self.__ext_modules = ext_mod
        self.__mod_config_dir = mod_conf
        self.__debug = debug
        self.__json = None
        self.list = []
        self.__ModJson = {}
        self.__getList()

    def __get_mod_dir(self):
        filepath = os.path.dirname(os.path.realpath(__file__))
        return os.path.dirname(filepath) + "/modules"
        
    def __getList(self):
        modules_dir = self.__get_mod_dir()
        self.__get_list_dir(modules_dir)
        self.__get_list_dir(self.__ext_modules)

    def __get_list_dir(self, modules_dir):
        if self.__debug:
            print "DEBUG: search modules in - " + modules_dir
        for f in os.listdir(modules_dir):
            if os.path.isfile(os.path.join(modules_dir, f)):
                if f.endswith('.py'):
                    if f != '__init__.py' and f != '__init__.pyc':
                        modname = f.replace('.py','')
                        if modname not in self.list:
                            self.list.append(modname)
                            self.__ModJson[modname] = None
                            if self.__debug:
                                print "DEBUG: add to list module - " + modname
                        else:
                            print Color().red + "ERROR: two modules with name \"" +modname+ "\"" + Color().base
                        
    def loadConf(self, name):
        mod_config = self.__mod_config_dir + "/" + name + ".json"
        if self.__debug:
            print "DEBUG: load config - " + mod_config
        if os.path.isfile(mod_config):
            with open(mod_config) as data_file:
                self.__ModJson[name] = json.load(data_file)
            if self.__ModJson[name]['enabled']:
                return True
            else:
                self.__ModJson[name] = None
                return False
        else:
            self.__build_conf(name)
            with open(mod_config) as data_file:
                self.__ModJson[name] = json.load(data_file)
            return True


    def __build_conf(self, name):
        modules_dir = self.__get_mod_dir()
        mod_config = self.__mod_config_dir + "/" + name + ".json"
        
        print "+build config for module " + name
        
        data = self.__load_mods(modules_dir, name)
        if data is None:
            data = self.__load_mods(self.__ext_mod,name)        
        if data is None:
            print Color().red + "ERROR: problem to build config for module " + name + Color().base
        
        self.__build_json(mod_config, data)
        
    def __build_json(self, file_conf, data):
        print "+write config " + file_conf
        DataFile = open(file_conf, "w")
        data = json.dumps(data, indent=4, separators=(',', ': '), sort_keys=True)
        DataFile.write(data)
        DataFile.close()


    def __load_mods(self, modules_dir, name):
        sys.path.append(modules_dir)
        f = name + ".py"
        if os.path.isfile(os.path.join(modules_dir, f)):            
            module = __import__(name)
            print "+" +name+ " loaded module to build config"
            return module.Config().__dict__
        else:
            print "ERROR: " + os.path.join(modules_dir, f) + " not found"
            return None

    def getModJson(self, name):
        if self.__ModJson[name] is None:
            for mod in self.list:
                if mod == name:
                    self.loadConf(name)
        return self.__ModJson[name]
        
class Data:
    def __init__(self):
        self.conf_version = "0.0.1"
        self.torrent_client = "qbittorrent-nox"
        self.user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36"
        self.debug = False
        self.dir_download = None #TODO
        self.browser = "w3m"
        self.output_string_limit = 80 #used by bt-download
        self.date_format = "" #TODO

        self.rss = {}
        self.rss['enabled'] = False
        self.rss['dir'] =  None
        self.rss['show_limit'] = 40    
        self.rss['download_filtered'] = True

        self.conky = {}
        self.conky['chars_to_print'] = 90
        self.conky['rows_to_print'] = 6
        self.conky['font'] = "Sans Mono:size=8"
        self.conky['font_bold'] = "Sans Mono:bold:size=8"
        self.conky['color1'] = "color2"
        self.conky['color2'] = "color"
        self.conky['color_line_even'] = "color4"
        self.conky['color_line_odd'] = "color"
        
        self.links = {}
        self.links['torcache'] = "http://torcache.net/torrent/"
        self.links['zoink'] = "https://zoink.it/torrent/"
        
class Config:
    def __init__(self):
        self.__color = Color()
        self.__dir = os.environ['HOME'] + "/.config/bt-tools"
        self.__dir_mod =  self.__dir + "/modules"
        self.__dir_log =  self.__dir + "/log"
        self.__mod_conf =  self.__dir + "/modules_conf"       
        self.__file_conf = self.__dir + "/config.json"
        self.__file_db = self.__dir + "/database.sqlite"
        self.__db = None

        
        if not os.path.exists(self.__dir):
            print "+create " + self.__dir
            os.mkdir(self.__dir)
            
        if not os.path.exists(self.__dir_mod):
            print "+create " + self.__dir_mod
            os.mkdir(self.__dir_mod)
            
        if not os.path.exists(self.__dir_log):
            print "+create " + self.__dir_log
            os.mkdir(self.__dir_log)

        if not os.path.exists(self.__mod_conf):
            print "+create " + self.__mod_conf
            os.mkdir(self.__mod_conf)
            
        if not os.path.exists(self.__file_conf):
            print "+build config file "
            self.__data = Data()
            self.__build_config()
        
            
        #load config
        with open(self.__file_conf) as data_file:
            self.__json = json.load(data_file)            
        self.__debug = self.__json['debug']
        
        self.module = Module(self.__dir_mod, self.__mod_conf, self.__debug)
        
        self.__db = database.Data(self.__file_db, self.__debug)       
        if not os.path.exists(self.__file_db):
            self.__db.makeDb()
            
    def __build_config(self):
        print "+write config " + self.__file_conf
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
    
    def load_mod(self, name, config):
        #load modules config from "modules" dir
        filepath = os.path.dirname(os.path.realpath(__file__))
        moddir = os.path.dirname(filepath) + "/modules"
        sys.path.append(moddir)
        sys.path.append(self.__dir_mod)

        if os.path.isfile(os.path.join(moddir, name+'.py')) or \
          os.path.isfile(os.path.join(self.__dir_mod, name+'.py')):
            module = __import__(name)
            return module.Data(name, config, self.__dir_log, self.__json['user_agent'], self.__debug)
        else:
            print self.__color.red + "ERROR: module " + name + " not found" + self.__color.base
            return None


    def getDb(self):
        return self.__db

    def checkVersion(self):
        if self.__db is not None:
            if self.__db.checkVersion():
                if self.__json['conf_version'] != Data().conf_version:
                    print "error: config version is " + self.__json['conf_version'] + " - required " + Data().conf_version
                    return False
                else:
                    return True
            else:
                if self.__json['conf_version'] != Data().conf_version:
                    print "error: config version is " + self.__json['conf_version'] + " - required " + Data().conf_version
                return False
        else:
            print "error: db object is None"
            return False
        
