#!/usr/bin/env python3

# pip3 isntall youtube_dl
# dnf install ffmpeg

from __future__ import unicode_literals

from os import listdir, makedirs, path
from shutil import move
from sys import argv
from youtube_dl import YoutubeDL
from youtube_dl.utils import DownloadError

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

        if not path.exists('/home/flippy/Music/{0}'.format(artist)):
            makedirs('/home/flippy/Music/{0}'.format(artist))
        if not path.exists('/home/flippy/Music/{0}/Unknown Album'.format(artist)):
            makedirs('/home/flippy/Music/{0}/Unknown Album'.format(artist))
        move(each, '/home/flippy/Music/{0}/Unknown Album/{1}.mp3'.format(artist, song))
