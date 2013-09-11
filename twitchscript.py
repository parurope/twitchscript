#!/usr/bin/python

"""
Cambios hechos por Paruro.pe:
=============================

10/09/2013:
===========
1. comentarios traducidos
2. omxplayer seleccionado por defecto para que funcione en el Raspberry Pi
3. anadida la opcion para cambiar la calidad, puesta en 'medium' por defecto
4. interfaz traducida a espanol

Pompetardo

==================================================================================================

Twitchscript es un script burdo escrito en Python para Linux/Windows, que te permite
iniciar y ver transmisiones de Twitch desde la linea de comandos.
Basicamente provee un menu que toma las transmisiones actuales del Twitch API.
Yo lo uso principalmente para ver transmisiones desde mi Raspberry Pi que esta
conectado a mi TV (via HDMI). VLC es usado por defecto como reproductor de video.
Cambia la configuracion "playerCommand" segun tus necesidades (p.ej. usa omxplayer
en el Raspberry Pi)

Usa "q" para salir del canal que estes viendo y regresar al menu.

Como Instalar/Ejecutar:

Linux (Debian/Raspian y otras distribuciones):
1. sudo apt-get install rtmpdump python-pip
2. sudo pip install livestreamer
3. sudo chmod +x twitchscript.py (dale permiso a este archivo para ser ejecutado)
4. asegurate de que este instalado el reproductor que esta definido en "playerCommand"
5. inicia el script

Windows 7:
 1. instala python 2.7 - version de 32 bit
 2. anade el folder de instalacion de Python a la variable de ruta de Windows
 3. instala distribute - https://pypi.python .org/pypi/distribute
 4. instala pip - https://pypi.python.org/pypi/pip
 5. anade el folder "Script" de Python  a la variable de ruta de Windows (p.ej. C:\Python27\Scripts)
 6. instala livestreamer con pip desde la linea de comandos: "pip install livestreamer" 
 7. instala/descomprime rtmpdump - http://rtmpdump.mplayerhq.hu/
 8. anade el fornde de rtmpdump a la variable de ruta de Windows
 9. asegurate de que este instalado el reproductor que esta definido en "playerCommand" Y 
    que su folder este anadido a la variable de ruta de Windows
10. inicia el script

"""

import json
import urllib2
import sys
import os

"""
Configuracion:
"""
#playerCommand = 'vlc'
playerCommand = 'omxplayer -o hdmi'
# cuantos juegos quieres que se muestren? -> debe ser > 0 (max: 100)
gameLimit = 60
# cuantos canales/transmisiones quieres que se muestren? -> must be > 0 (max: 100)
channelLimit = 60
# Que calidad deseas que tenga la transmision?
# -> low(baja), medium(media), high(alta), best(maxima)
quality = 'medium'

"""
NO CAMBIAR:
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
        print 'Error obteniendo la Transmision!\n'
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
        print 'Error obteniendo los Juegos!\n'
        print e.message
    finally:
        response.close()

def getChannels(game):
    channeldict = json.loads(getTwitchApiRequestStreams(channelLimit, game))

    receivedChannelCount = len(channeldict['streams'])
    TmpChannelLimit = channelLimit  
    
    if TmpChannelLimit > receivedChannelCount:
        TmpChannelLimit = receivedChannelCount
        print 'Solo %d canales disponibles!' % TmpChannelLimit

    for i in range(TmpChannelLimit):
        channels.append(channeldict['streams'][i]['channel']['name'])

    return TmpChannelLimit

def getGames():
    gamesDict = json.loads(getTwitchApiRequestGames(gameLimit))

    receivedGameCount = len(gamesDict['top'])
    TmpGameLimit = gameLimit
    
    if TmpGameLimit > receivedGameCount:
        TmpGameLimit = receivedGameCount
        print 'Solo %d juegos disponibles!' % TmpGameLimit

    for i in range(TmpGameLimit):
        games.append(gamesDict['top'][i]['game']['name'])

    return TmpGameLimit

def show(content):
    for i in range(len(content)):
        if i < 9:
            print '',
        if i < 99:
            print '',            
        print '%d %s' % (i + 1, content[i])

def playStream(channel):
    if os.name == 'nt':
        os.system('livestreamer twitch.tv/%s %s -p "%s"' % (channel,
        quality, playerCommand))
    else:
        os.system('livestreamer twitch.tv/%s %s -np "%s"' % (channel,
        quality, playerCommand))

def reset():
    del channels[:]
    del games[:]

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
            print 'Entrada Erronea! Porfavor ingresar valores Validos!'
            print '-' * 40
            if choices == 1:
                show(games)
            else:
                show(channels)
    return userInput

def main():
    while True:
        print '\nCargando'
        TmpGameLimit = getGames()
        clearScreen()
        print 'Mostrando %d juegos top:' % gameLimit
        print '-' * 40
        show(games)

        chosenGame = getUserInput('\nEscoge el juego por numero (0 para salir):',
            range(TmpGameLimit + 1), 1)

        clearScreen()
        if int(chosenGame) in range(0, len(games) + 1):
            if int(chosenGame) is 0:
                sys.exit(0)
            print 'Cargando lista de canales: "%s"\n' % games[int(chosenGame) - 1]
            TmpChannelLimit = getChannels(transformSpaces(games[int(chosenGame) - 1]))

        clearScreen()
        print 'Mostrando %d canales top:' % channelLimit
        print '-' * 40
        show(channels)

        chosenChannel = getUserInput('\nEscoge el canal por numero (0 para salir):',
            range(TmpChannelLimit + 1), 2)

        clearScreen()
        if int(chosenChannel) in range(0, len(channels) + 1):
            if int(chosenChannel) is 0:
                sys.exit(0)
            print 'Cargando transmision: "%s"\n' % channels[int(chosenChannel) - 1]
            playStream(channels[int(chosenChannel) - 1])
        reset()

if __name__ == '__main__':
    if (channelLimit < 0  or channelLimit > 100) or (gameLimit < 0 or gameLimit > 100):
        clearScreen()
        print 'Revisa tus Configuraciones -> channelLimit o gameLimit erroneos!'
    else:    
        clearScreen()
        print 'Bienvenido a twitchscript!'
        main()
