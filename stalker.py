#!/usr/bin/env python                                               #
#####################################################################
#- erm1s.n1nja@gmail.com | github.com/erm1s | erm1s.wordpress.com - #
#####################################################################
# stalker.py

import time
import urllib2
import os
from threading import *
import re

class tvguide():
        def __init__(self):
            self.masterlist = []
            self.newlist = []
            self.downloads = []
            self.writelog = ''
            self.file_tvshow = open('tvshows', 'r+')
            self.link_log = open('link.log', 'a+')
            self.error_log = open('error.log', 'a+')
            self.start = time.ctime()

        def errorlog(self, e, funcname):
            try:
                timenow = time.ctime()
                self.writelog = timenow+': ['+funcname+'] '+str(e)+'\n'
                self.error_log.write(self.writelog)
                return
            except Exception, e:
                print str(e)+'\n'

        def linklog(self, link):
            try:
                timenow = time.ctime()
                self.writelog = timenow+' : [+] Download: '+str(link)+'\n'
                self.link_log.write(self.writelog)
                return
            except Exception, e:
                self.errorlog(e, 'linklog()')

def guidesetup(showlist):
    tvshows = []
    tvshows = [item.strip('\n').split(':') for item in showlist if '#' not in item]
    return tvshows

def readytowatch(tvshow):
    tvshow = tvshow.replace(' ','.')
    tvshow = tvshow.lower()
    tvshow = tvshow.strip('\n')
    return tvshow

def readyurl(tvshow):
    tvshow = tvshow.replace(' ', '%20')
    tvshow = tvshow.lower()
    tvshow = tvshow.strip('\n')
    return tvshow

def getepisode(tv, link):
    try:
        regex = re.search("\.s(\d{2})e(\d{2}\.)", link)
        if regex is not None:
            return regex.group().strip('.')
        else:
            return None
    except Exception, e:
        tv.errorlog(e, 'getepisode()')

def download(link):
    cmd = 'transmission-gtk '+link+' &'
    os.system(cmd)
    return

def stalker_eztv(tv):
    try:
        host = "http://eztv.it"
        url = urllib2.urlopen(host)
        torlinks = []
        for link in url:
            if 'href' in link and 'torrent' in link:
                link = link.split('href')
                if len(link) > 2:
                    link = link[2].split('http')[1]
                    link = link.split('.torrent')[0]
                    link = 'http'+link+'.torrent'
                    torlinks.append(link)
        return torlinks
    except Exception, e:
        tv.errorlog(e, 'stalker_eztv()')

def stalker_ezrss(tv, tvshow):
    try:
        rsslinks = []
        tvshow = readyurl(tvshow)
        host = "http://ezrss.it"+"/search/?mode=simple&show_name="+tvshow
        url = urllib2.urlopen(host)
        for link in url:
            if 'href' in link and 'torrent' in link:
                link = link.split('href')
                if len(link) > 1:
                    link = link[1].split('http')[1]
                    link = link.split('.torrent')[0]
                    link = 'http'+link+'.torrent'
                    rsslinks.append(link)
        return rsslinks
    except Exception, e:
        tv.errorlog(e, 'stalker_ezrss()')
        return rsslinks

def stalker_tpb(tv, tvshow):
    try:
        tpb_links = []
        tvshow = readyurl(tvshow)
        host = "http://thepiratebay.sx"+"/search/"+tvshow+"/0/7/0"
        url = urllib2.urlopen(host)
        for link in url:
            if "magnet:?" in link:
                mag = link.rsplit('a href=\"')[1]
                mag = mag.split('\"')[0]
                mag = '\"'+mag+'\"'
                tpb_links.append(mag)
                continue
            else:
                continue
        return tpb_links
    except Exception, e:
        tv.errorlog(e, 'stalker_tpb()')
        return False

def chkLink(tvshows, episode):
    for line in tvshows[1:]:
        if line in episode:
            return True
    return False

def stalker_main(tv, tvshow, tvshows):
    try:
        tvlist = tvshows
        eztvlinks = stalker_eztv(tv)
        ezrsslinks = stalker_ezrss(tv, tvshow)
        tpblinks = stalker_tpb(tv, tvshow)
        tvshow = readytowatch(tvshow)
        for link in ezrsslinks:
            eztvlinks.append(link)
        for link in tpblinks:
            eztvlinks.append(link)

        for link in eztvlinks:
            lowLink = link.lower()
            if tvshow in lowLink:
                episode = getepisode(tv, lowLink)
                if episode is None:
                    continue

                check = chkLink(tvshows, episode)
                if not check:
                    link = link.replace('[', '%5B')
                    link = link.replace(']', '%5D')
                    tvlist.append(episode)
                    tv.downloads.append(link)
                    continue

        list(set(tvlist))
        tvlist = ':'.join(tvlist)
        tv.newlist.append(tvlist)
        return

    except Exception, e:
        tv.errorlog(e, 'stalker_main')

def main():
    tv = tvguide()

    while True:
        filename = open('tvshows', 'r')
        tvshows = guidesetup(filename)
        filename.close()
        for tvshow in tvshows:
            stalker_main(tv, tvshow[0], tvshow)
            continue

        for line in tv.downloads:
            if '720' in line:
                continue
            else:
                download(line)
                tv.linklog(line)
                continue
            time.sleep(.5)

        file2 = open('.tmpshows', 'w')

        for line in tv.newlist:
            file2.write(line+'\n')

        tv.newlist = []
        tv.downloads = []
        os.remove('tvshows')
        os.rename('.tmpshows', 'tvshows')
        file2.close()
        time.sleep(600)

if __name__ == "__main__":
    main()
