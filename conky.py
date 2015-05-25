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

import os, sys, xml, config

class Conky:
    def __init__(self):
        self.data = xml.Data()
        self.engines = config.engines
        self.cats = config.conky_categories
        self.conkyEng = config.conky_sites_to_show
        self.chars = config.conky_chars_to_print
        self.row = config.conky_rows_to_print
        
    def Print(self):
        self.data.load()
        self._getLast()
        self._setNow()

        numE=self.conkyEng[self.nowEng]
        cat = self.cats[self.lastCat]

        self.data.exportConky(self.engines[numE].name, cat, self.chars, self.row)

    def _getLast(self):
        if not os.path.isfile("/tmp/bttools-eng.state"):
            self._openfiles("w")
            self._writefiles('0','0')
            self.lastEng=0
            self.lastCat=0
        else:
            self._openfiles("r")
            self.lastEng = int(self.lastfile.readline())
            self.lastCat = int(self.lastfilecat.readline())
        self._closefiles()

    def _setNow(self):
        self.nowEng = self.lastEng + 1
        self.nowCat = self.lastCat

        if self.nowEng == len(self.conkyEng):
            self.nowEng = 0
            self.nowCat = self.lastCat + 1

        if self.nowCat == len(self.cats):
            self.nowCat = 0

        self._openfiles("w")
        self._writefiles(self.nowEng, self.nowCat)
        self._closefiles()

    def _openfiles(self, mode):
        self.lastfile = open("/tmp/bttools-eng.state", mode)
        self.lastfilecat = open("/tmp/bttools-cat.state", mode)

    def _writefiles(self, Eng, Cat):
        self.lastfile.write(str(Eng))
        self.lastfilecat.write(str(Cat))

    def _closefiles(self):
        self.lastfile.close()
        self.lastfilecat.close()

    def lscat(self):
        for engine in self.engines:
            engine.lscat()

if __name__ == "__main__":
    do = Conky()

    if sys.argv[1] == "lscat":
        do.lscat()

    elif sys.argv[1] == "make":
        do.Print()


    elif sys.argv[1] == "help":
        print "make - list feed item by category"
        print "lscat - list category"

    else:
        print "not valid options: " + sys.argv[1]
        print "try help"
        
        

