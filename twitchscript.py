#!/usr/bin/python

"""

Twitchscript is a little Python Script for Linux, enabling you to start Twitch Streams from the CLI.
It basically provides a menu so that u dont need to browse Twitch in order to get the current streams.
I mainly use it for watching streams with the Raspberry Pi which is connected to my TV (via HDMI).
However you can also use it on a normal machine with vlc.

I am new to python so feel free to criticize me.
Hints and suggestions are appreciated.

Requirements:
- livestreamer must be installed (https://github.com/chrippa/livestreamer) -> easy install via "python-pip" (pip install livestreamer)
- make this script executable (chmod +x) and run it!
- you may have to adapt some settings regarding your environment

Todo:
- input validation
- error handling
- fix problem with special characters

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

def getTwitchApiRequestStreams(limit, game):
    #print 'using: ' + twitchApiUrl + 'streams?limit=' + str(limit) + '&game=' + game
    return urllib2.urlopen('%sstreams?limit=%d&game=%s' % (twitchApiUrl, limit, game)).encode('UTF-8').read()

def getTwitchApiRequestGames(limit):
    #print 'using: ' + twitchApiUrl + 'games/top?limit=' + str(limit)
    return urllib2.urlopen('%sgames/top?limit=%d' % (twitchApiUrl, limit)).read()

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
    global gameLimit

    gamesDict = json.loads(getTwitchApiRequestGames(gameLimit))

    if gameLimit > len(gamesDict['top']):
        gameLimit = len(gamesDict['top'])
        print 'Only ' + str(gameLimit) + ' games available!'

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

def getUserInput(message, validValues, choices):

    userInputValid = False

    while not userInputValid:
        try:
            choice = int(raw_input('%s\n> ' % message))
            if choice in validValues:
                userInputValid = True
            else:
                raise ValueError()
        except ValueError:
            clearScreen()
            print 'Wrong Input! Please enter valid Values!'
            print '-' * 20
            if choices == 1:
                showGames()
            else:
                showChannels()
    return choice

def main():
    while True:
        clearScreen()
        print 'Welcome to twitchscript!'
        print '\nLoading'
        getGames()
        clearScreen()
        print 'Showing top %s games:' % str(gameLimit)
        print '-' * 20
        showGames()

        chosenGame = getUserInput('\nChoose game by number (0 for exit):', range(gameLimit + 1), 1)

        clearScreen()
        if int(chosenGame) in range(0, len(games) + 1):
            if int(chosenGame) is 0:
                sys.exit(0)
            print 'Loading channellist: "%s"\n' % games[int(chosenGame) - 1]
            getChannels(transformSpaces(games[int(chosenGame) - 1]))

        clearScreen()
        print 'Showing top %s channels:' % str(channelLimit)
        print '-' * 20
        showChannels()

        chosenChannel = getUserInput('\nChoose channel by number (0 for exit):', range(channelLimit + 1), 2)

        clearScreen()
        if int(chosenChannel) in range(0, len(channels) + 1):
            if int(chosenChannel) is 0:
                sys.exit(0)
            print 'Loading stream: "%s"\n' % channels[int(chosenChannel) - 1]
            playStream(channels[int(chosenChannel) - 1])
        reset()

if __name__ == '__main__':
    main()
