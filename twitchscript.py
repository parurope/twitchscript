#!/usr/bin/python

"""
Twitchscript is a dirty Python-Script for Linux/Windows, enabling you to start and
watch Twitch Streams from the CLI.
It basically provides a menu that grabs current streams from the Twitch API.
I mainly use it for watching streams with my Raspberry Pi which is connected
to TV (via HDMI). VLC is used by default as video player. Change the "playerCommand"
setting for your needs (e.g. use omxplayer on a Rasperry Pi).

Use "q" to quit watching the current channel and return to menu.


How to Install:

Linux (Debian/Raspian and many more):
1. sudo apt-get install rtmpdump python-pip
2. sudo pip install livestreamer
3. sudo chmod +x twitchscript.py (give this file execution permissions)
4. make sure you have the player installed that is set at "playerCommand"
5. start this script

Windows 7:
1. install python 2.7
2. .... install rtmpdump & livestreamer .... (need to specify that)
3. add folders of python, rtmpdump and vlc to path variable
4. make sure you have the player installed that is set at "playerCommand"
5. start this script

"""

import json
import urllib2
import sys
import os

"""
Settings:
"""
playerCommand = 'vlc'
#playerCommand = 'omxplayer -o hdmi'
# must be > 0 (max: 100)
gameLimit = 100
# must be > 0 (max: 100)
channelLimit = 100

"""
Dont change:
"""
twitchApiUrl = 'https://api.twitch.tv/kraken/'
games = []
channels = []

def getTwitchApiRequestStreams(limit, game):
    #print 'using: %sstreams?limit=%d&game=%s' % (twitchApiUrl, limit, game)
    try:
        response = urllib2.urlopen(('%sstreams?limit=%d&game=%s' % (twitchApiUrl,
        limit, game)).encode('utf-8'))
        streams = response.read()
        return streams
    except Exception as e:
        print 'Error getting Streams!\n'
        print e.message
    finally:
        response.close()

def getTwitchApiRequestGames(limit):
    #print 'using: %sgames/top?limit=%d' % (twitchApiUrl, limit)
    try:
        response = urllib2.urlopen(('%sgames/top?limit=%d' % (twitchApiUrl,
        limit)).encode('utf-8'))
        games = response.read()
        return games
    except Exception as e:
        print 'Error getting Games!\n'
        print e.message
    finally:
        response.close()

def getChannels(game):
    global channelLimit

    channeldict = json.loads(getTwitchApiRequestStreams(channelLimit, game))
        
    receivedChannelCount = len(channeldict['streams'])
    
    if channelLimit > receivedChannelCount:
        channelLimit = receivedChannelCount
        print 'Only %d channels available!' % channelLimit

    for i in range(channelLimit):
        channels.append(channeldict['streams'][i]['channel']['name'])

def getGames():
    global gameLimit

    gamesDict = json.loads(getTwitchApiRequestGames(gameLimit))

    receivedGameCount = len(gamesDict['top'])
    
    if gameLimit > receivedGameCount:
        gameLimit = receivedGameCount
        print 'Only %d games available!' % gameLimit

    for i in range(gameLimit):
        games.append(gamesDict['top'][i]['game']['name'])

def show(content):
    for i in range(len(content)):
        if i < 9:
            print '',
        if i < 99:
            print '',            
        print '%d %s' % (i + 1, content[i])

def playStream(channel):
    if os.name == 'nt':
        os.system('livestreamer twitch.tv/%s best -p "%s"' % (channel,
        playerCommand))
    else:
        os.system('livestreamer twitch.tv/%s best -np "%s"' % (channel,
        playerCommand))

def reset():
    channels[:] = []
    games[:] = []

def transformSpaces(stringToTransform):
    return stringToTransform.replace(' ', '%20')

def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')

def getUserInput(message, validValues, choices):

    userInputValid = False

    while not userInputValid:
        try:
            userInput = int(raw_input('%s\n> ' % message))
            if userInput in validValues:
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
    return userInput

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

        chosenGame = getUserInput('\nChoose game by number (0 for exit):',
            range(gameLimit + 1), 1)

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

        chosenChannel = getUserInput('\nChoose channel by number (0 for exit):',
            range(channelLimit + 1), 2)

        clearScreen()
        if int(chosenChannel) in range(0, len(channels) + 1):
            if int(chosenChannel) is 0:
                sys.exit(0)
            print 'Loading stream: "%s"\n' % channels[int(chosenChannel) - 1]
            playStream(channels[int(chosenChannel) - 1])
        reset()

if __name__ == '__main__':
    if (channelLimit < 0  or channelLimit > 100) or (gameLimit < 0 or gameLimit > 100):
        clearScreen()
        print 'Check your Settings -> wrong channelLimit or gameLimit set!'
    else:    
        main()
