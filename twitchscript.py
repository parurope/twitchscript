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
- error handling
- encapsulate menu

"""

import json
import urllib2
import sys
import os

# settings:

# put command for whatever player should be used
#playercommand = 'vlc'
playercommand = 'omxplayer -o hdmi'
# api url
twitchApiUrl = 'https://api.twitch.tv/kraken/'
# must be > 0 (max: 100)
gameLimit = 20
# must be > 0 (max: 100)
channelLimit = 20
games = []
channels = []

def getTwitchApiRequestStreams(limit, game):
    #print 'using: %sstreams?limit=%d&game=%s' % (twitchApiUrl, limit, game)
    return urllib2.urlopen(('%sstreams?limit=%d&game=%s' % (twitchApiUrl, limit, game)).encode('UTF-8')).read()

def getTwitchApiRequestGames(limit):
    #print 'using: %sgames/top?limit=%d' % (twitchApiUrl, limit)
    return urllib2.urlopen('%sgames/top?limit=%d' % (twitchApiUrl, limit)).read()

def getChannels(game):
    global channelLimit

    channeldict = json.loads(getTwitchApiRequestStreams(channelLimit, game))

    if channelLimit > len(channeldict['streams']):
        channelLimit = len(channeldict['streams'])
        print 'Only %d channels available!' % channelLimit

    for i in range(channelLimit):
        channels.append(channeldict['streams'][i]['channel']['name'])

def getGames():
    global gameLimit

    gamesDict = json.loads(getTwitchApiRequestGames(gameLimit))

    if gameLimit > len(gamesDict['top']):
        gameLimit = len(gamesDict['top'])
        print 'Only %d games available!' % gameLimit

    for i in range(gameLimit):
        games.append(gamesDict['top'][i]['game']['name'])

def show(content):
    for i in range(len(content)):
        if i < 9:
            print '',
        print '%d %s' % (i + 1, content[i])

def playStream(channel):
    os.system('livestreamer twitch.tv/%s best -np "%s"' % (channel, playercommand))

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
            print '-' * 40
            if choices == 1:
                show(games)
            else:
                show(channels)
    return choice

def main():
    while True:
        clearScreen()
        print 'Welcome to twitchscript!'
        print '\nLoading'
        getGames()
        clearScreen()
        print 'Showing top %d games:' % gameLimit
        print '-' * 40
        show(games)

        chosenGame = getUserInput('\nChoose game by number (0 for exit):', range(gameLimit + 1), 1)

        clearScreen()
        if int(chosenGame) in range(0, len(games) + 1):
            if int(chosenGame) is 0:
                sys.exit(0)
            print 'Loading channellist: "%s"\n' % games[int(chosenGame) - 1]
            getChannels(transformSpaces(games[int(chosenGame) - 1]))

        clearScreen()
        print 'Showing top %d channels:' % channelLimit
        print '-' * 40
        show(channels)

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
