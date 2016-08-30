#! /usr/bin/python
# -*- coding=utf-8 -*-

#bt-tools - tools to interact with some bittorrent sites by commandline
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

from PyQt4.QtCore import QVariant, QSettings, QString
import config

class Func:
    def __init__(self, verbose = False):
        #self.debug = config.debug
        self.verbose = verbose
        self.debug = False
    
    def getFeeds( self, rules ):
        pass

    def write_rules( self ):
        rules = self._loadRules()
        file_list = {}
        if self.verbose:
            print "build filters list"
        for i in rules:
            for z in i['affected_feeds']:
                if "file://" + config.rssdir in z:
                    filename = z.replace("file://" + config.rssdir,"").replace(".rss","")
                    if filename in file_list.keys():
                        rule_list = file_list[filename]
                        rule_list.append(i['must_contain'])
                        file_list[filename] = rule_list
                    else:
                        if self.verbose:
                            print "new list: " + filename
                        file_list[filename] = []
        for key, list in file_list.items():
            if self.verbose:
                print "write file: " + config.rssdir + key + "-filters-qbt.txt"
            rules_file = open(config.rssdir + key + "-filters-qbt.txt", "w")
            for i in list:
                rules_file.write(i+"\n")
            rules_file.close()

    def _loadRules( self ):
        qb = QSettings("qBittorrent", "qBittorrent-rss")
        Rules = self._loadRulesFromVariantHash(qb.value("download_rules").toHash())
        return Rules

    def _loadRulesFromVariantHash( self, qtdict ):
        all_rules = []
        if self.debug:
            print "load rules by qbittorrent file"
        for title, obj in qtdict.items():
            rule = self._fromVariantHash(obj.toHash())
            if rule['enabled']:
                if self.debug:
                    print "#####################################################"
                    print title
                    print
                    for key, value in rule.items():                
                        if key == "affected_feeds":
                            print key + " : "
                            print " " + value[0]
                            print " " + value[1]
                            print " " + value[2]
                        else:
                            print key + " : " + str(value)
                    print
                all_rules.append(rule)
        return all_rules

                    
    def _fromVariantHash( self, rule_hash ):
        name = str(rule_hash[QString("name")].toString())
        enabled = rule_hash[QString("enabled")].toBool()
        must_contain = str(rule_hash[QString("must_contain")].toString())
        must_not_contain = str(rule_hash[QString("must_not_contain")].toString())
        use_regex = rule_hash[QString("use_regex")].toBool()
        affected_feeds = []
        for value in rule_hash[QString("affected_feeds")].toStringList():
            affected_feeds.append(str(value))

        out = {
            "name" : name,
            "enabled" : enabled,
            "must_contain" : must_contain,
            "must_not_contain" : must_not_contain,
            "use_regex" : use_regex,
            "affected_feeds" : affected_feeds
            }
        return out

    
