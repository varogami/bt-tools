import sqlite3

class Data:
    def __init__(self, filepath, debug=False):
        self.__debug = debug
        self.__file = filepath
        self.__version = "0.0.1"
        self.__new_item = 0
            
    def makeDb(self):
        print "create database"
        self.__create_tor_string= "CREATE TABLE torrent ( " + \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," + \
            "module TEXT NOT NULL," + \
            "url_module TEXT NOT NULL," + \
            "id_module TEXT NOT NULL," + \
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

        self.__create_rss_string= "CREATE TABLE rss ( " + \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," + \
            "id_item INTEGER NOT NULL," + \
            "FOREIGN KEY(id_item) REFERENCES torrent(id))"
    
        self.__con = sqlite3.connect(self.__file)
        with self.__con:
            cur = self.__con.cursor()
            cur.execute(self.__create_tor_string)
            cur.execute(self.__create_config_string)
            cur.execute(self.__create_rss_string)
            cur.execute("INSERT INTO config VALUES('version','%s')" % self.__version)

    def insert(self, shortname, url_module, item):
        self.__con = sqlite3.connect(self.__file)
        with self.__con:
            cur = self.__con.cursor()
            cur.execute('''SELECT id FROM torrent WHERE module=? AND id_module=?''', (shortname, item.id))
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
                            item.id, \
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

    def getCountNew(self):
        return self.__new_item
    
    def resetCountNew(self):
        self.__new_item = 0

    def search_by_name(self, pattern):
        self.__con = sqlite3.connect(self.__file)
        with self.__con:
            cur = self.__con.cursor()
            words=pattern.split(" ")
            count=0
            sql="SELECT * FROM torrent WHERE name LIKE "
            for word in words:
                if count == 0:
                  sql = sql + "'%"+word+"%'"
                else:
                  sql = sql + " AND name LIKE '%"+word+"%'"
                count+=1
                
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

    def get_item(self, id):
        pass

    def update_item(self, newitem):
        pass
