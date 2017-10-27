#!/usr/bin/env python3

from argparse import ArgumentParser, RawDescriptionHelpFormatter
#from io import StringIO
#from mutagen.mp3 import MP3
from mutagen import id3
from os import listdir, path
#from PIL import Image
from pygn import register, search # https://github.com/cweichen/pygn
from sys import argv
from textwrap import dedent
from urllib import request


clientID = '702337754-900975F20663BD0B36A073B2E463DE14'
userID = register(clientID)

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
                tags = id3.ID3(music_path)
            except id3.ID3NoHeaderError:
                print("Adding ID3 header;")
                tags = id3.ID3()

            result = search(clientID=clientID, userID=userID, artist=artist, track=music)
            album_art = request.urlopen(result['album_art_url']).read()
            # Image.open(StringIO(opened_url)) and Image.show()

            for each in result['genre'].keys():
                if result['genre'][each]['TEXT'] in genres:
                    result['genre'] = result['genre'][each]['TEXT']
                    break
            else:
                print("Failed with no appropriate genre found in:", result['genre'])
                exit(1)

            tags["TIT2"] = id3.TIT2(encoding=3, text=u'{0}'.format(music))
            tags["TALB"] = id3.TALB(encoding=3, text=u'{0}'.format(result['album_title']))
            tags["TPE1"] = id3.TPE1(encoding=3, text=u'{0}'.format(artist))
            tags["TCON"] = id3.TCON(encoding=3, text=u'{0}'.format(result['genre']))
            tags["TDRC"] = id3.TDRC(encoding=3, text=u'{0}'.format(result['album_year']))
            tags["TRCK"] = id3.TRCK(encoding=3, text=u'{0}'.format(result['track_number']))
            tags["APIC"] = id3.APIC(encoding=3, mime='image/png' if cover.endswith('png') else 'image/jpeg',
                type=3, desc=u'Cover', data=album_art)

            tags.save(music_path)
