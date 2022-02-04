#!/usr/bin/env python3

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from os import listdir, mkdir, path, rename, rmdir
from sys import argv
from textwrap import dedent


def Parse():

    parser = ArgumentParser(prog=path.basename(__file__.rpartition('.')[0]), add_help=False, formatter_class=RawDescriptionHelpFormatter,
                description=dedent('''\
                              Appender
                        ------------------
                         MP3 Name Appender
                    '''), epilog=dedent('''\
                        Check the git repository at https://github.com/fredericomateusmartins/spytify-server,
                        for more information about usage, documentation and bug report.\
                    ''')
                )

    optional = parser.add_argument_group('Flags')
    optional.add_argument('-s', '--source', metavar='path', type=str, help='Source path with music', required=True)
    optional.add_argument('-h', '--help', action='help', help='Show this help message')
    
    if len(argv) == 1:
        parser.print_help()
        exit(1)

    return parser.parse_args()


args = Parse()

for artist in sorted(listdir(args.source)):
    artist_path = path.join(args.source, artist)
    for album in listdir(artist_path):
        album_path = path.join(artist_path, album)
        for music in listdir(album_path):         
            music_path = path.join(album_path, music)
            rename(music_path, '.'.join([music_path, 'mp3']))
