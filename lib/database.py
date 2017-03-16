import sqlite3

class Data:
    def __init__(self, filepath, debug=False):
        self.__debug = debug
        self.__file = filepath
        self.__version = "0.0.1"
        self.__db_version = None
        self.__new_item = 0
        self.__new_item_extra = 0

    def checkVersion(self):
        self.__con = sqlite3.connect(self.__file)
        cur = self.__con.cursor()
        cur.execute('''SELECT value FROM config WHERE name == ?''', ('version',))
        db_version=cur.fetchone()
        self.__db_version = db_version[0]
        if self.__version == self.__db_version: 
            return True
        else:
            print "error: db version is " + self.__db_version + " - required " + self.__version
            return False
    
    def makeDb(self):
        print "+create database"
        self.__create_tor_string= "CREATE TABLE torrent ( " + \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," + \
            "module TEXT NOT NULL," + \
            "url_module TEXT NOT NULL," + \
            "id_module INTEGER NOT NULL," + \
            "name TEXT NOT NULL," + \
            "url_item TEXT NOT NULL UNIQUE," + \
            "idate INTEGER NOT NULL," + \
            "type TEXT," + \
            "size INTEGER," + \
            "date INTEGER," + \
            "leech INTEGER," + \
            "seed INTEGER," + \
            "completed INTEGER," + \
            "magnet TEXT," + \
            "url_torrent TEXT," + \
            "hash TEXT," + \
            "object BLOB," + \
            "html BLOB)"

        self.__create_config_string= "CREATE TABLE config ( " + \
            "name TEXT NOT NULL PRIMARY KEY UNIQUE," + \
            "value TEXT NOT NULL)"

        self.__create_extra_info_string= "CREATE TABLE extra_info ( " + \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," + \
            "id_item INTEGER NOT NULL," + \
            "key TEXT NOT NULL," + \
            "value TEXT NOT NULL," + \
            "FOREIGN KEY(id_item) REFERENCES torrent(id))"
    
        self.__con = sqlite3.connect(self.__file)
        with self.__con:
            cur = self.__con.cursor()
            cur.execute(self.__create_tor_string)
            cur.execute(self.__create_config_string)
            cur.execute(self.__create_extra_info_string)
            cur.execute("INSERT INTO config VALUES('version','%s')" % self.__version)

    def insert(self, shortname, url_module, item):
        self.__con = sqlite3.connect(self.__file)
        with self.__con:
            cur = self.__con.cursor()
            cur.execute('''SELECT id FROM torrent WHERE module=? AND id_module=?''', (shortname, item.id_module))
            result=cur.fetchone()
            if result is None:
                self.__new_item += 1
                if item.data is not None:
                    blob_object = sqlite3.Binary(item.data)
                else:
                    blob_object = None
                    
                if item.html is not None:
                    html = sqlite3.Binary(item.html)
                else:
                    html = None
                    
                cur.execute('''INSERT INTO torrent VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', \
                            (None, \
                            shortname, \
                            url_module, \
                            item.id_module, \
                            item.name, \
                            item.link, \
                            item.idate, \
                            item.type, \
                            item.size, \
                            item.date, \
                            item.leech, \
                            item.seed, \
                            item.compl, \
                            item.magnet, \
                            item.torrent_link, \
                            item.hashvalue, \
                            blob_object, \
                            html))
                lid = cur.lastrowid
                return lid
            else:
                return result[0]
            
    def insert_extra(self, id, key, value):
        self.__con = sqlite3.connect(self.__file)
        with self.__con:
            cur = self.__con.cursor()
            cur.execute('''SELECT id FROM extra_info WHERE id_item=? AND key=?''', (id, key))
            result=cur.fetchone()
            if result is None:
                self.__new_item_extra += 1
                    
                cur.execute('''INSERT INTO extra_info VALUES(?,?,?,?)''', (None, id, key, value))
                lid = cur.lastrowid
                return True
            else:
                return False
            
    def getCountNew(self):
        return self.__new_item
    
    def resetCountNew(self):
        self.__new_item = 0

    def getCountNewExtra(self):
        return self.__new_item_extra
    
    def resetCountNewExtra(self):
        self.__new_item_extra = 0
        
    def search_by_name(self, pattern):
        self.__con = sqlite3.connect(self.__file)
        with self.__con:
            cur = self.__con.cursor()
            words=pattern.split(" ")
            begin=True
            sql="SELECT * FROM torrent WHERE name LIKE "
            for word in words:
                if begin:
                  sql = sql + "'%"+word+"%'"
                  begin=False
                else:
                  sql = sql + " AND name LIKE '%"+word+"%'"
                
            cur.execute(sql)
            result=cur.fetchall()
            return result
         
    def search_by_hash(self, hash):
        self.__con = sqlite3.connect(self.__file)
        with self.__con:
            cur = self.__con.cursor()
            cur.execute('''SELECT * FROM torrent WHERE hash LIKE ?''', (hash,))
            result=cur.fetchall()
            return result

    def search_by_mod(self, mod):
        self.__con = sqlite3.connect(self.__file)
        with self.__con:
            cur = self.__con.cursor()
            cur.execute('''SELECT * FROM torrent WHERE module == ?''', (mod,))
            result=cur.fetchall()
            return result

    def get_item(self, id):
        self.__con = sqlite3.connect(self.__file)
        cur = self.__con.cursor()
        cur.execute('''SELECT * FROM torrent WHERE id == ?''', (id,))
        result=cur.fetchone()
        return result

    def update_item(self, item):
        if item is None:
            print "ERROR: item is None cannot update db"
        else:    
            self.__con = sqlite3.connect(self.__file)
            with self.__con:
                cur = self.__con.cursor()
                if item.data is not None:
                    blob_object = sqlite3.Binary(item.data)
                else:
                    blob_object = None
                    
                if item.html is not None:
                    html = sqlite3.Binary(item.html)
                else:
                    html = None
                    
                cur.execute('''UPDATE torrent SET name = ?,idate = ?,type = ?,size = ?,date = ?,leech = ?,seed = ?,completed = ?,magnet = ?,url_torrent = ?,hash = ?,object = ?,html = ? WHERE id=?''', \
                            (item.name, \
                             item.idate, \
                             item.type, \
                             item.size, \
                             item.date, \
                             item.leech, \
                             item.seed, \
                             item.compl, \
                             item.magnet, \
                             item.torrent_link, \
                             item.hashvalue, \
                             blob_object, \
                             html, \
                             item.id))
