#!/usr/bin/env python3

# pip3 isntall youtube_dl
# dnf install ffmpeg

from __future__ import unicode_literals

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
