#!/usr/bin/python

""" 

TwitchScript is a little Python script for linux, enabling you to start Twitch Streams from the CLI.
I mainly use it for watching Streams with the Raspberry Pi which is connected to my TV (via HDMI). However you can also use it on a usual machine with vlc.
It might not be perfect but it does work atleast :)

Requirements: 
- livestreamer must be installed (https://github.com/chrippa/livestreamer) -> easy install via "python-pip" (pip install livestreamer)
- make this script executable (chmod +x) and run it!
- you may have to adapt some settings regarding your environment 

Todo:
- input validation
- fix problem with special characters
- what if there are less channels than u want to get?

"""

import json
import urllib2
import sys
import os

# settings:

# if you use a raspberry pi with omxplayer change it to 'True'!
usingOmxPlayer = False
# api url
twitchApiUrl = 'https://api.twitch.tv/kraken/'
# must be > 0 (max: 100)
gameLimit = 20
# must be > 0 (max: 100)
channelLimit = 20
games = []
channels = []

def diag():
	print 'channels: '
	print channels
	print '\nlength channels: ' + str(len(channels))
	print '\ngames: ' 
	print games 
	print '\nlength games:' + str(len(games))
	print '\n'
	print channelLimit 
	print gameLimit
	print '\n\n'

def getTwitchApiRequestStreams(limit, game):
	print 'using: ' + twitchApiUrl + 'streams?limit=' + str(limit) + '&game=' + game
	return urllib2.urlopen(twitchApiUrl + 'streams?limit=' + str(limit) + '&game=' + game).read()

def getTwitchApiRequestGames(limit):
	#print 'using: ' + twitchApiUrl + 'games/top?limit=' + str(limit)
	return urllib2.urlopen(twitchApiUrl + 'games/top?limit=' + str(limit)).read()

def getChannels(game):
	global channelLimit

	channeldict = json.loads(getTwitchApiRequestStreams(channelLimit, game))

	if channelLimit > len(channeldict['streams']):
		channelLimit = len(channeldict['streams'])
		print 'Only ' + str(channelLimit) + ' channels available!'

	for i in range(channelLimit):
		channels.append(channeldict['streams'][i]['channel']['name'])

def showChannels():
	for i in range(len(channels)):
		if i < 9:
			print ' %d %s' % (i + 1, channels[i])
		else:	
			print '%d %s' % (i + 1, channels[i])

def getGames():
	gamesDict = json.loads(getTwitchApiRequestGames(gameLimit))

	for i in range(gameLimit):
		games.append(gamesDict['top'][i]['game']['name'])

def showGames():
	for i in range(len(games)):
		if i < 9:
			print ' %d %s' % (i + 1, games[i])
		else:
			print '%d %s' % (i + 1, games[i])

def playStream(channel):
	if usingOmxPlayer:
		os.system('livestreamer twitch.tv/' + channel + ' best -np "omxplayer -o hdmi"')
	else:
		os.system('livestreamer twitch.tv/' + channel + ' best')

def reset():
	channels[:] = []
	games[:] = []

def transformSpaces(stringToTransform):
	return stringToTransform.replace(' ', '%20')

def clearScreen():
	os.system('clear')

def menu():
	while True:
		clearScreen()
		print '\nLoading'
		getGames()
		clearScreen()
		print '\nWelcome to TwitchChannelViewer (TCV)!'
		print '\nShowing top %s games:' % str(gameLimit)
		print '------------------------------------------------------------'
		showGames()
		
		print '\nChoose game by number (0 for exit):'
		chosenGame = raw_input('> ')

		clearScreen()
		if int(chosenGame) in range(0, len(games) + 1):
			if int(chosenGame) is 0:
				sys.exit(0)
			print '\nLoading channellist: "%s"\n' % games[int(chosenGame) - 1]
			getChannels(transformSpaces(games[int(chosenGame) - 1]))

		showChannels()

		print '\nChoose channel by number (0 for exit):'
		chosenChannel = raw_input('> ')

		clearScreen()
		if int(chosenChannel) in range(0, len(channels) + 1):
			if int(chosenChannel) is 0:
				sys.exit(0)
			print '\nLoading stream: "%s"\n' % channels[int(chosenChannel) - 1]
			playStream(channels[int(chosenChannel) - 1])
		reset()

def main():
	menu()

if __name__ == '__main__':
    main()