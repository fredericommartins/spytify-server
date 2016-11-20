#!/bin/env python3

from os import listdir, path, rename
from sys import argv


progpath = path.dirname(path.realpath(argv[0]))
libpath = '{0}/libr'.format(progpath.rpartition('/')[0])

for music in listdir(libpath):
    if music.endswith('.mp3'):
        splitname = music.split('.mp3')[0].split(' - ')
        splitname.append('Unknown Album.mp3')

        newmusic = '-'.join(splitname)
        rename(path.join(libpath, music), path.join(libpath, newmusic))
