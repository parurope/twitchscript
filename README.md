twitchscript
============

Linux CLI Script for watching Twitch streams (useful for RaspberryPi).
See twitchscript.py for some Infos.

Known Bugs
==========

1.  There is a problem with special characters. For example when selecting the Stream "Pokémon ..." it crashes stating: 
    UnicodeEncodeError: 'ascii' codec can't encode character u'\xe9' in position 37: ordinal not in range(128)
