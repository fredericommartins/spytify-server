#!/usr/bin/env python3

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, COMM, USLT, TCOM, TCON, TDRC
from os import listdir, path
from sys import  argv
from textwrap import dedent


def Parse():

    parser = ArgumentParser(prog=path.basename(__file__.rpartition('.')[0]), add_help=False, formatter_class=RawDescriptionHelpFormatter,
                description=dedent('''\
                              Metadata
                        -------------------
                        Metadata Injection
                    '''), epilog=dedent('''\
                        Check the git repository at https://github.com/flippym/spytify-server,
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
            
            try: # create ID3 tag if not present
                tags = ID3(music_path)
            except ID3NoHeaderError:
                print("Adding ID3 header;")
                tags = ID3()

            tags["TIT2"] = TIT2(encoding=3, text=u'{0}'.format(music))
            tags["TALB"] = TALB(encoding=3, text=u'{0}'.format(album))
            tags["TPE1"] = TPE1(encoding=3, text=u'{0}'.format(artist))

            tags.save(music_path)
