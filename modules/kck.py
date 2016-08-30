import json, urllib, datetime, httplib2
from BeautifulSoup import BeautifulSoup

class Config:
    def __init__(self):
        self.enabled = True
        #self.url = 'https://kickasstop.com/'
        #self.url = 'https://kat.cr'
        self.url = 'http://katcr.to/'
        self.name = 'kickasstorrents'
        self.rss_light_download = True
        self.cats = {
            'all': '',
            'anime':'Anime',
            'other':'Other',
            'movie': 'Movies', 
            'books': 'Books', 
            'tv': 'TV', 
            'music': 'Music',
            'xxx': 'XXX',
            'games': 'Games', 
            'apps': 'Applications'}
        self.default_cat = 'all'
        self.rss_filter = None #None - for not set filter - filter rss feed

class Data:
    def __init__(self, name, config, debug=False):
        self.list = []
    def search(self, pattern, cat):
        return True
