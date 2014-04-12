#!/usr/bin/env python

import os
import sys
import time
import urllib2
import subprocess
import ConfigParser
from bs4 import BeautifulSoup


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
    try:
        response = urllib2.urlopen('http://www.google.com')
        return True
    except:
    	return False


class Gmailnotification:

	def __init__(self, user, passwd, previousnumber):
		self.getnumberofmessage(user, passwd, previousnumber)

	def getnumberofmessage(self, user, passwd, previousnumber):
		auth_handler = urllib2.HTTPBasicAuthHandler()
		auth_handler.add_password(
			realm = 'New mail feed',
			uri = 'https://mail.google.com',
			user = '{user}@gmail.com'.format(user=user),
			passwd = passwd
		)
		opener = urllib2.build_opener(auth_handler)
		urllib2.install_opener(opener)
		try:
			feed = urllib2.urlopen(FEED_URL)
			self.parsingfullcount(feed, previousnumber)
		except:
			return

	def parsingfullcount(self, feed, previousnumber):
		soup = BeautifulSoup(feed.read())
		number = soup.fullcount.string
		number = int(number)
		unreadmessages = "You have %d unread mails in your gmail inbox" % int(number)
		self.sendmessage(unreadmessages, number, previousnumber)

	def sendmessage(self, message, number, previousnumber):
		nomessage = "No unread mails in your gmail inbox"
		if number == int(previousnumber):
			return
		else:
			if number == 0:
				subprocess.Popen(['notify-send', nomessage])
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

if __name__ == "__main__":
	while True:
		if internet_on():
			user = ConfigSectionMap("SectionOne")['username']
			passwd = ConfigSectionMap("SectionOne")['password']
			previousnumber = ConfigSectionMap("SectionOne")['previousnumber']
			d = Gmailnotification(user, passwd, previousnumber)
			time.sleep(300)
		else:
			time.sleep(30)
