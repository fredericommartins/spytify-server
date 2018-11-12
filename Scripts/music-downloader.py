#!/usr/bin/env python3

# pip3 install youtube_dl
# dnf install ffmpeg

from __future__ import unicode_literals

from mpd import MPDClient
from os import listdir, makedirs, path, system
from shutil import move
from sys import argv
from youtube_dl import YoutubeDL
from youtube_dl.utils import DownloadError

library_path = '/music/'
mpd = MPDClient()
music2add = []

mpd.connect("localhost", 6600)

ydl_opts = {'format': 'bestaudio/best', 
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3'
                }]
            }

with YoutubeDL(ydl_opts) as ydl, open(argv[1], 'r') as openfile:
    try:
        for url in openfile.read().split('\n'):
            if url:
                ydl.download([url])

    except DownloadError as error:
        print("\033[31mFailed\033[0m: {0}".format(error))

for each in listdir('.'):
    if path.isfile(each) and each[-4:] == '.mp3':
        print("Moving '{0}'".format(each))
        try:
            artist, song, *rest = each.split('-')
        except ValueError:
            artist = song = ''
        else:
            artist = artist.strip()
            song = song.strip()

        artist_input = input("Artist [{0}]: ".format(artist))
        song_input = input("Song [{0}]: ".format(song))

        if artist_input:
            artist = artist_input
        if song_input:
            song = song_input

        if not path.exists('{0}{1}'.format(library_path, artist)):
            makedirs('{0}{1}'.format(library_path, artist))
        if not path.exists('{0}{1}/Unknown Album'.format(library_path, artist)):
            makedirs('{0}{1}/Unknown Album'.format(library_path, artist))
        move(each, '{0}{1}/Unknown Album/{2}.mp3'.format(library_path, artist, song))
        music2add.append('{0}/Unknown Album/{1}.mp3'.format(artist, song))

mpd.update()
system('restorecon -rv {0}; chown mpd:mpd -R {0}'.format(library_path)

for music in music2add: # Add new songs to MPD playlist
    mpd.playlistadd('New', music)

mpd.load('New')
