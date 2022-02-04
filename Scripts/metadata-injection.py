#!/usr/bin/env python3

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from mutagen import id3
from os import listdir, mkdir, path, rename, rmdir
from pygn import register, search # https://raw.githubusercontent.com/cweichen/pygn/master/pygn.py
from sys import argv
from textwrap import dedent
from urllib import error, request


clientID = '702337754-900975F20663BD0B36A073B2E463DE14'
userID = register(clientID)
relate = {'ACDC': 'AC/DC'}
forbidden = ['Live']
genres = ['Indie Rock', 'Acid Rock', 'Trance', 'Reggae', 'Grunge', 'New Romantic', 'Hard Rock', 'Southern Rap', 'Emo & Hardcore', 'Pop Punk', 'Rap Comedy',
    'Heavy Metal', 'Rock', 'Classical', 'Brazilian Pop', 'European Traditional', 'Samba', 'Industrial', 'Other', 'Synth Pop', 'Alternative Rock', 'House',
    'Electronica', 'Electric Blues', 'Punk', 'Urban', 'Old School Punk', 'Western Pop', 'Classic R&B', 'Classic Soul', 'Jazz', 'New Wave Rock', 'Brit Pop', 
    'Folk', 'Pop Electronica', 'Contemporary R&B', 'European Pop', 'Progressive House', 'Western Pop', 'New Wave Pop', 'East Coast Rap', 'Gangsta Rap',
    'West Coast', 'Garage Rock Revival', 'Funk', 'Alternative', 'Midwestern Rap', 'Funk Metal', 'Lounge', 'Brit Rock', 'Classic Country', 'Caribbean Pop',
    'African Pop', 'Goth', 'Ska Revival', 'Rockabilly Revival', 'Southern African', 'Pop']

def Parse():

    parser = ArgumentParser(prog=path.basename(__file__.rpartition('.')[0]), add_help=False, formatter_class=RawDescriptionHelpFormatter,
                description=dedent('''\
                              Metadata
                        ------------------
                        Metadata Injection
                    '''), epilog=dedent('''\
                        Check the git repository at https://github.com/fredericomateusmartins/spytify-server,
                        for more information about usage, documentation and bug report.\
                    ''')
                )

    optional = parser.add_argument_group('Flags')
    optional.add_argument('-f', '--filter', metavar='exp', type=str, help='Artist comma delimited expression')
    optional.add_argument('-s', '--source', metavar='path', type=str, help='Source path with music', required=True)
    optional.add_argument('-h', '--help', action='help', help='Show this help message')
    
    if len(argv) == 1:
        parser.print_help()
        exit(1)

    return parser.parse_args()


args = Parse()

for artist in sorted(listdir(args.source)):
    artist_path = path.join(args.source, artist)
    if args.filter and artist not in args.filter.split(','):
        continue
    for album in listdir(artist_path):
        album_path = path.join(artist_path, album)
        for music in listdir(album_path): 
            music_path = path.join(album_path, music)
            try: # create ID3 tag if not present
                tags = id3.ID3(music_path)
            except id3.ID3NoHeaderError:
                tags = id3.ID3()

            try:
                if artist in relate:
                    real_artist = relate[artist]
                else:
                    real_artist = artist

                if music[-4:] == '.mp3':
                    music = music[:-4]
                else:
                    music_path += '.mp3'

                result = search(clientID=clientID, userID=userID, artist=real_artist, track=music)
            except UnboundLocalError:
                print("Failed query with artist '{0}' and music '{1}'".format(artist, music))
                continue

            try:
                album_art = request.urlopen(result['album_art_url']).read()
            except (error.URLError, ValueError, TypeError):
                album_art = None

            for each in result['genre'].keys():
                if result['genre'][each]['TEXT'] in genres:
                    result['genre'] = result['genre'][each]['TEXT']
                    break
            else:
                if not result['genre']:
                    result['genre'] = 'Other'
                else:
                    print("Failed with no appropriate genre found for '{0} - {1}':\n{2}".format(artist, music, result['genre']))
                    continue

            if 'TALB' in tags and str(tags['TALB']) and str(tags['TALB']) != 'Unknown Album':
                result['album_title'] = str(tags['TALB'])

            tags['TIT2'] = id3.TIT2(encoding=3, text=u'{0}'.format(music))
            tags['TALB'] = id3.TALB(encoding=3, text=u'{0}'.format(result['album_title']))
            tags['TPE1'] = id3.TPE1(encoding=3, text=u'{0}'.format(real_artist))
            tags['TCON'] = id3.TCON(encoding=3, text=u'{0}'.format(result['genre']))
            tags['TDRC'] = id3.TDRC(encoding=3, text=u'{0}'.format(result['album_year']))
            tags['TRCK'] = id3.TRCK(encoding=3, text=u'{0}'.format(result['track_number']))
            if album_art:
                    tags['APIC'] = id3.APIC(encoding=3, mime='image/png' if '.png' in result['album_art_url'] else 'image/jpeg',
                        type=3, desc=u'Cover', data=album_art)

            tags.save(music_path)
            print("Artist: {} | Album: {} ({}) | {} Music: {} ({})".format(real_artist, result['album_title'], result['album_year'], result['track_number'], music, result['genre']))

            if album is not result['album_title']:
                real_album_path = path.join(artist_path, ''.join(result['album_title'].split('/')))
                try:
                    mkdir(real_album_path)
                except FileExistsError:
                    pass
                rename(music_path, path.join(real_album_path, music + '.mp3'))

        if not listdir(album_path):
            rmdir(album_path)
