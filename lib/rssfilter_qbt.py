#! /usr/bin/python
# -*- coding=utf-8 -*-

#bt-tools - tools to interact with some bittorrent sites by commandline
#Copyright (C) 2015-2016 varogami <varogami@altervista.org>

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
import json

class Func:
    def __init__(self, path, debug = False ):
        self.debug = debug
        self.path = path
    
    def write_rules( self ):
        rules = self._loadRules()
        file_list = {}
        if self.debug:
            print "+build qbitorrent filters list"
        for i in rules:
            name = i['name'].replace(" ","_")
            filename = self.path + "/filter-qbt_"+name+".json"
            print "+write file " + filename
            rules_file = open(filename, "w")
            json_data = json.dumps(i, indent=4, separators=(',', ': '))
            rules_file.write(json_data)
            rules_file.close()

    def _loadRules( self ):
        qb = QSettings("qBittorrent", "qBittorrent-rss")
        Rules = self._loadRulesFromVariantHash(qb.value("download_rules").toHash())
        return Rules

    def _loadRulesFromVariantHash( self, qtdict ):
        all_rules = []
        print "+load "+ str(len(qtdict)) +" rules by qbittorrent file"
        for title, obj in qtdict.items():
            rule = self._fromVariantHash(obj.toHash())
            if rule['enabled']:
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

    
