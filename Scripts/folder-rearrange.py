#!/usr/bin/env python3

from os import listdir, makedirs, path, rename
from sys import argv


for file in listdir(argv[1]):
    if path.isfile(path.join(argv[1], file)):
        print(file)
        artist, music, album = file[:-4].split('-')
        newpath = path.join(path.join(argv[1], artist), album)
        if not path.isdir(newpath):
            makedirs(newpath, exist_ok=True)
        rename(path.join(argv[1], file), path.join(newpath, music))
