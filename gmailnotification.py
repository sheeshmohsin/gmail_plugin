#!/usr/bin/env python

import os
import sys
import time
import urllib2
import subprocess
import ConfigParser
from bs4 import BeautifulSoup
from os.path import expanduser


FEED_URL = 'https://mail.google.com/mail/feed/atom'


cwd = sys.path[0]
basefile = os.path.join(cwd, 'config.ini')


Config = ConfigParser.ConfigParser()
Config.read(basefile)


def ConfigSectionMap(section):
    values = {}
    options = Config.options(section)
    for option in options:
        try:
            values[option] = Config.get(section, option)
            if values[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            values[option] = None
    return values


def internet_on():
    return subprocess.call(['/bin/ping', '-c1', 'google.com'])


def updatecredentials():
    home = expanduser("~")
    homefile = os.path.join(home, '.gmailnotf.ini')
    if os.path.exists(homefile):
        updateconfig = ConfigParser.RawConfigParser()
        updateconfig.read(homefile)
        username = updateconfig.get(updateconfig.sections()[0], updateconfig.options(updateconfig.sections()[0])[0])
        password = updateconfig.get(updateconfig.sections()[0], updateconfig.options(updateconfig.sections()[0])[1])
        changeconfig = ConfigParser.RawConfigParser()
        conpath = sys.path[0]
        configpath = os.path.join(conpath, 'config.ini')
        changeconfig.read(configpath)
        changeconfig.sections()
        changeconfig.set('SectionOne', 'username', username)
        changeconfig.set('SectionOne', 'password', password)
        with open(configpath, 'wb') as configfile:
            changeconfig.write(configfile)
    else:
        return


class Gmailnotification:

    def __init__(self, user, passwd, previousnumber):
        self.getnumberofmessage(user, passwd, previousnumber)

    def getnumberofmessage(self, user, passwd, previousnumber):
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(
            realm='New mail feed',
            uri='https://mail.google.com',
            user='{user}@gmail.com'.format(user=user),
            passwd=passwd
        )
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)
        feed = urllib2.urlopen(FEED_URL)
        self.parsingfullcount(feed, previousnumber)

    def parsingfullcount(self, feed, previousnumber):
        soup = BeautifulSoup(feed.read())
        number = soup.fullcount.string
        number = int(number)
        unreadmessages = "You have %d unread mails in your gmail inbox" % int(number)
        self.sendmessage(unreadmessages, number, previousnumber)

    def sendmessage(self, message, number, previousnumber):
        if int(number) == int(previousnumber):
            self.dontshowpopup(number)
        else:
            self.showpopup(number, message)

    def dontshowpopup(self, number):
        self.value = number
        self.updateconfig(number)

    def showpopup(self, number, message):
        nomessage = "No unread mails in your gmail inbox"
        if number == 0:
            subprocess.Popen(['notify-send', nomessage])
            self.updateconfig(number)
        else:
            subprocess.Popen(['notify-send', message])
            self.updateconfig(number)

    def updateconfig(self, number):
        self.cwd = sys.path[0]
        self.basefile = os.path.join(self.cwd, 'config.ini')
        self.editconfig = ConfigParser.RawConfigParser()
        self.editconfig.read(self.basefile)
        self.editconfig.set('SectionOne', 'previousnumber', number)
        with open(self.basefile, 'wb') as configfile:
            self.editconfig.write(configfile)
        return

if __name__ == "__main__":
    updatecredentials()
    while True:
        if internet_on() == 0:
            user = ConfigSectionMap("SectionOne")['username']
            passwd = ConfigSectionMap("SectionOne")['password']
            previousnumber = ConfigSectionMap("SectionOne")['previousnumber']
            d = Gmailnotification(user, passwd, previousnumber)
            time.sleep(300)
        else:
            time.sleep(30)

