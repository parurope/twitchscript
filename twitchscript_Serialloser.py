#!/usr/bin/env python

"""
Cambios hechos por Paruro.pe:
=============================

10/09/2013:
===========
1. omxplayer seleccionado por defecto para que funcione en el Raspberry Pi
2. interfaz traducida a espanol
3. calidad por defecto 360p

Pompetardo

==================================================================================================

Como Instalar/Ejecutar:

Linux (Debian/Raspian y otras distribuciones):
1. sudo apt-get install rtmpdump python-pip
2. sudo pip install livestreamer
3. sudo chmod +x twitchscript.py (dale permiso a este archivo para ser ejecutado)
4. asegurate de que este instalado el reproductor que esta definido en "playerCommand"
5. inicia el script

Windows 7:
 1. instala python 2.6 - version de 32 bit
 2. anade el folder de instalacion de Python a la variable de ruta de Windows
 3. instala distribute - https://pypi.python .org/pypi/distribute
 4. instala pip - https://pypi.python.org/pypi/pip
 5. anade el folder "Script" de Python  a la variable de ruta de Windows (p.ej. C:\Python27\Scripts)
 6. instala livestreamer con pip desde la linea de comandos: "pip install livestreamer" 
 7. instala/descomprime rtmpdump - http://rtmpdump.mplayerhq.hu/
 8. anade el folder de rtmpdump a la variable de ruta de Windows
 9. asegurate de que este instalado el reproductor que esta definido en "playerCommand" Y 
    que su folder este anadido a la variable de ruta de Windows
10. inicia el script

"""

VERSION = '0.0.3'

CONFIGFILE_ERROR = 3

try:
    import simplejson as json
except ImportError:
    try:
        import json
        json.dumps ; json.dumps
    except (ImportError, AttributeError):
        quit("Porfavor instalar simplejson o Python 2.6 o mas actual.")

import ConfigParser
from optparse import OptionParser, SUPPRESS_HELP
from livestreamer import Livestreamer, StreamError, PluginError, NoPluginError
import requests
import urllib2
import requests
import sys
import os

config = ConfigParser.SafeConfigParser()
config.add_section('settings')
config.set('settings', 'channel', '45')
config.set('settings', 'game', '45')
config.set('settings', 'favorites', '')
config.set('settings', 'favgames', '')
config.set('settings', 'player', 'omxplayer -o hdmi')
config.set('settings', 'quality', 'medium')
config.set('settings', 'twitchapiurl', 'https://api.twitch.tv/kraken/')

# Handle request to twitch API

class TwitchApiRequest:
    def __init__(self, method):        
        self.method = method
        
    def send_request(self):
        try:
#            self.open_request = 'open'
	    self.open_request = requests.get(self.method)
        except AttributeError:
            pass
        except urllib2.HTTPError, e:
            try:
                msg = html2text(str(e.read()))
            except:
                msg = str(e)
        except urllib2.URLError, msg:
            try:
                reason = msg.reason[1]
            except IndexError:
                reason = str(msg.reason)
                                            
    def get_response(self):
        if self.open_request == None:
            return { 'result' : 'solicitud no abierta'}
        
        #response = self.open_request.read()
        
        try:
            #data = json.loads(response)
	    data = self.open_request.json()
        except ValueError:
            quit("No se puede analizar la respuesta: %s\n" % response, JSON_ERROR)
        self.open_request = None
        return data
    
# End of class TwitchApiRequest

# Wrapper to manage twitch API calls

class Twitch:
    def __init__(self, base_url, channel_limit, game_limit):        
        self.base_url = base_url
        self.channel_limit = channel_limit
        self.game_limit = game_limit        
        
    
    def get_game_list(self):
        parameter = ('%sgames/top?limit=%s' % (self.base_url, self.game_limit)).encode('utf-8')        
        request = TwitchApiRequest(parameter)
        request.send_request()        
        return request.get_response()
    
    def get_channel_for_game(self, game_name):        
        parameter = ('%sstreams?limit=%s&game=%s' % (self.base_url, self.channel_limit, game_name)).encode('utf-8')
        request = TwitchApiRequest(parameter)
        request.send_request()        
        return request.get_response()
        
    def get_favorites_streams_status(self, favs):
        parameter = ('%sstreams?channel=%s' % (self.base_url, favs)).encode('utf-8')        
        request = TwitchApiRequest(parameter)
        request.send_request()        
        return request.get_response()
                
# End of class Twitch

# Main loop

class Main:
    def __init__(self):    
        self.gchoice = -1
        self.cchoice = -1    
        self.exit_now = False
        self.state = 'none'
        self.keybingings = {
            ord('q'):       self.quit,
            ord('f'):       self.get_favorites,
            ord('s'):       self.get_fav_games,
            ord('g'):       self.get_games,
            ord('n'):       self.get_next,
            ord('r'):       self.refresh,
            ord('p'):       self.get_previous            
        }
        
        self.games = []
        self.favs = []
        self.channels = []        
        self.twitch = Twitch(config.get('settings', 'twitchapiurl'), config.get('settings', 'channel'), config.get('settings', 'game'))
        self.livestreamer = Livestreamer()
        
        try:
            self.run()
        except Exception as e:
            print e.message
        
    def run(self):
        
        while True:            
            self.display_message()                                            
            if self.exit_now:
                return
    
    def quit(self, c):
        self.exit_now = True
        
    def display_message(self):
                               
        if self.state == 'none':
            clear_screen()                      
            self.handle_user_input('Escoge una opcion : Favoritos(F), Juegos(G), Salir(Q)')            
        
        if self.state == 'favs':
            clear_screen()            
            print 'Mostrando transmisiones favoritas en linea :'
            print '-' * 40
            if(len(self.favs) > 0):                            
                self.show_content(self.favs)            
                self.handle_user_input('Escoge un canal por numero (r para refrescar, g para enlistar juegos y q para salir', range(len(self.favs) + 1))
                clear_screen()
            else:
                self.handle_user_input('No hay canales favoritos en linea (r para refrescar, g para enlistar juegos y q para salir', range(len(self.favs) + 1))
                clear_screen()            
                
        if self.state == 'games':
            clear_screen()            
            print 'Mostrando %d juegos destacados:' % config.getint('settings', 'game')
            print '-' * 40
            if(len(self.games) > 0):                            
                self.show_content(self.games)            
                self.gchoice = self.handle_user_input('Escoge un juego por numero (r para refrescar, f para revisar tus canales favoritos y q para salir', range(len(self.games) + 1))
                if self.gchoice != -1:
                    self.state = 'channels'
                    clear_screen()                                                 
                    
        if self.state == 'favgames':
            clear_screen()            
            print 'Mostrando juegos favoritos:'
            print '-' * 40
            if(len(self.games) > 0):                        
                self.show_content(self.games)            
                self.gchoice = self.handle_user_input('Escoge un juego por numero (r para refrescar, f para revisar tus canales favoritos y q para salir', range(len(self.games) + 1))
                if self.gchoice != -1:
                    self.state = 'channels'
                    clear_screen()
        
        if self.state == 'channels':
            clear_screen()            
            print 'Mostrando %d canales destacados para %s:' % (config.getint('settings', 'channel'), self.games[self.gchoice - 1])
            print '-' * 40            
            self.get_channels(self.gchoice)
            if(len(self.channels) > 0):                            
                self.show_content(self.channels)            
                self.cchoice = self.handle_user_input('Escoge un canal por numero (r para refrescar, f para revisar tus canales favoritos, g para enlistar juegos y q para salir', range(len(self.channels) + 1))
                if self.cchoice != -1:
                    self.play_stream(self.channels[self.cchoice - 1])
                    self.state = 'channels'
                    clear_screen()
       
    def play_stream(self, channel):
        clear_screen()
        
        try:
            plugin = self.livestreamer.resolve_url(("twitch.tv/{0}").format(channel))
        except Exception as e:
            print e.message                   
        
        try:
            streams = plugin.get_streams()
        except PluginError as err:
            exit("Plugin error: {0}".format(err))
        
        player = config.get('settings', 'player')
        quality = config.get('settings', 'quality')
        if quality not in streams:
            quality = "best"
            print "No se puede abrirla transmision con la calidad solicitada ({0}), abriendo la de mejor calidad".format(config.get('settings', 'quality'))
                        
        channel = transform_spaces(channel)
        if os.name == 'nt':
            #os.system('livestreamer twitch.tv/%s %s' % (channel, quality))
            os.system('livestreamer -p "%s" twitch.tv/%s %s' % (player, channel, quality))
        else:
            #os.system('livestreamer twitch.tv/%s %s' % (channel, quality))
            os.system('livestreamer -np "%s" twitch.tv/%s %s' % (player, channel, quality))
            
    def show_content(self, content):
        for i in range(len(content)):
            if i < 9:
                print '',
            if i < 99:
                print '',
            print '%d %s' % (i + 1, content[i])
            
    def handle_user_input(self, message, valid = None):
        self.state = 'none'
        validinput = False
        while not validinput:
            input = raw_input('%s\n ' % message)
            input = input.strip().lower()
            
            if input.isdigit():
                input = int(input)
                if input in valid:
                    validinput = True                    
                    return input
            elif len(input) == 1:
                c = ord(input)                
                f = self.keybingings.get(c, None)
                if f:
                    f(c)
                    validinput = True                    
                    return -1
            
        
    def get_favorites(self, c):
        self.state = 'favs'
        del self.favs[:]
        try:
            response = self.twitch.get_favorites_streams_status(config.get('settings', 'favorites'))
            receivedcount = len(response['streams'])
            
            for i in range(receivedcount):
                self.favs.append('%s Reproduciendo: %s' % (response['streams'][i]['channel']['name'], response['streams'][i]['game']))
                
        except Exception as e:
            print 'Error obteniendo transmisiones favoritas!\n'
            print e.message
            return 0
        
    def get_games(self, c):        
        self.state = 'games'
        del self.games[:]
        try:
            response = self.twitch.get_game_list()
            receivedcount = len(response['top'])
            
            for i in range(receivedcount):
                self.games.append(response['top'][i]['game']['name'])
                
        except Exception as e:
            print 'Error obteniendo juegos !\n'
            print e.message
            return 0
        
    def get_fav_games(self, c):
        self.state = 'favgames'
        del self.games[:]
        
        favgames = config.get('settings', 'favgames')
        if len(favgames) > 0:
            self.games.extend(favgames.split(', '))                        
        
    def get_channels(self, choice):
        self.state = 'channels'
        del self.channels[:]
        try:
            response = self.twitch.get_channel_for_game(transform_spaces(self.games[self.gchoice - 1]))
            receivedcount = len(response['streams'])
            
            for i in range(receivedcount):
                self.channels.append('%s (%s)' % (response['streams'][i]['channel']['name'], response['streams'][i]['viewers']))
                
        except Exception as e:
            print 'Error obteniendo canales !\n'
            print e.message
            return 0        
        
    def refresh(self, c):
        print 'tmp'
        
    def get_next(self, c):
        print 'tmp'
        
    def get_previous(self, c):
        print 'tmp'
        
# End of class Main

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def transform_spaces(s):
    return s.replace(' ', '%20')

def create_config(option, opt_str, value, parser):
    configfile = parser.values.configfile
    config.read(configfile)
    
    dir = os.path.dirname(configfile)
    if dir != "" and not os.path.isdir(dir):
        try:
            os.makedirs(dir)
        except OSError, msg:
            print msg
            exit(CONFIGFILE_ERROR)
    
    if not save_config(configfile, force=True):
        exit(CONFIGFILE_ERROR)
    print "Archivo de configuracion escrito: %s" % configfile
    exit(0)
    
def save_config(filepath, force=False):
    if force or os.path.isfile(filepath):
        try:
            config.write(open(filepath, 'w'))
            os.chmod(filepath, 0600)  # config may contain password
            return 1
        except IOError, msg:
            print >> sys.stderr, "No se puede escroibir el archivo de configuracion %s:\n%s" % (filepath, msg)
            return 0
    return -1

def html2text(str):
    str = re.sub(r'</h\d+>', "\n", str)
    str = re.sub(r'</p>', ' ', str)
    str = re.sub(r'<[^>]*?>', '', str)
    return str

def debug(data):
    if options.DEBUG:
        file = open("debug.log", 'a')
        if type(data) == type(str()):
            file.write(data)
        else:
            import pprint
            pp = pprint.PrettyPrinter(indent=4)
            file.write("\n====================\n" + pp.pformat(data) + "\n====================\n\n")
        file.close

def quit(msg='', exitcode=0):    
    # if this is a graceful exit and config file is present
    if not msg and not exitcode:
        save_config(cmd_args.configfile)
    else:
        print >> sys.stderr, msg,
    os._exit(exitcode)
    
def show_version(option, opt_str, value, parser):
    quit("twitch %s\n" % VERSION)


if __name__ == '__main__':
    default_config_path = os.path.expanduser('~') + '/.twitchrc'
    parser = OptionParser(usage="%prog [options]", description="%%prog %s" % VERSION)
    parser.add_option("-v", "--version", action="callback", callback=show_version,
                      help="Muestra el numero de version")
    parser.add_option("-f", "--config", action="store", dest="configfile", default=default_config_path,
                      help="Ruta al archivo de configuracion.")
    parser.add_option("--create-config", action="callback", callback=create_config,
                      help="Crea archivo de configuracion CONFIGFILE con valores por defecto.")
    parser.add_option("-d", "--debug", action="store_true", dest="DEBUG", default=False,
                      help="Todo pasado a la funcion debug() sera anadido al archivo debug.log.")
    (options, cmd_args) = parser.parse_args()
    debug(options)
    config.read(options.configfile)
    
    Main()
