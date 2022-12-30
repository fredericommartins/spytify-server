#!/usr/bin/env python3

# https://genius.com/api-clients (outlook.com)
# pip3 install mutagen musicbrainzngs lyricsgenius #lxml

import logging

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from musicbrainzngs import get_image_list, musicbrainz, search_recordings, search_releases, set_useragent
from mutagen import id3
from os import listdir, mkdir, path, rename, rmdir
from sys import argv
from textwrap import dedent
from urllib import error, request


LOG_PATH='/var/log/metadata_injection.log'
LOCK_PATH='/tmp/.metadata_injection'

logging.basicConfig(filename=LOG_PATH, level=logging.WARNING, format='%(asctime)s %(levelname)s %(message)s')

set_useragent(
    "python-musicbrainzngs-example",
    "0.1",
    "https://github.com/alastair/python-musicbrainzngs/",
)

relate = {'ACDC': 'AC/DC'}
forbidden = ['Live']
#genres = ['Indie Rock', 'Acid Rock', 'Trance', 'Reggae', 'Grunge', 'New Romantic', 'Hard Rock', 'Southern Rap', 'Emo & Hardcore', 'Pop Punk', 'Rap Comedy',
#    'Heavy Metal', 'Rock', 'Classical', 'Brazilian Pop', 'European Traditional', 'Samba', 'Industrial', 'Other', 'Synth Pop', 'Alternative Rock', 'House',
#    'Electronica', 'Electric Blues', 'Punk', 'Urban', 'Old School Punk', 'Western Pop', 'Classic R&B', 'Classic Soul', 'Jazz', 'New Wave Rock', 'Brit Pop', 
#    'Folk', 'Pop Electronica', 'Contemporary R&B', 'European Pop', 'Progressive House', 'Western Pop', 'New Wave Pop', 'East Coast Rap', 'Gangsta Rap',
#    'West Coast', 'Garage Rock Revival', 'Funk', 'Alternative', 'Midwestern Rap', 'Funk Metal', 'Lounge', 'Brit Rock', 'Classic Country', 'Caribbean Pop',
#    'African Pop', 'Goth', 'Ska Revival', 'Rockabilly Revival', 'Southern African', 'Pop']

def _lock():
  try:
    with open(LOCK_PATH, 'r') as domainLock:
      return domainLock.read()
  except FileNotFoundError:
    return None

def Parse():
    parser = ArgumentParser(prog=path.basename(__file__.rpartition('.')[0]), add_help=False, formatter_class=RawDescriptionHelpFormatter,
                description=dedent('''\
                              Metadata
                        ------------------
                        Metadata Injection
                    '''), epilog=dedent('''\
                        Check the git repository at https://github.com/fredericommartins/spytify-server,
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
previous_artist = _lock()

for artist in sorted(listdir(args.source)):
    artist_path = path.join(args.source, artist)
    if args.filter and artist not in args.filter.split(',') or previous_artist and min(previous_artist,artist) == artist:
        logging.debug(f'Skipping artist: {artist}')
        continue
    for album in listdir(artist_path):
        album_path = path.join(artist_path, album)
        for music in listdir(album_path): 
            music_path = path.join(album_path, music)
            # Create ID3 tag if not present
            try:
                tags = id3.ID3(music_path)
            except id3.ID3NoHeaderError:
                logging.warning("No header found")
                tags = id3.ID3()
            # Relate artist for character escape
            try:
                real_artist = relate[artist]
            except KeyError:
                real_artist = artist
            # Assert music .mp3 extension
            if music[-4:] == '.mp3':
                music = music[:-4]
            else:
                music_path += '.mp3'
                
            result = {'track_number': None, 'album_year': None, 'genre': None, 'album_art_url': None, 'album_title': 'Unknown Album', 'album_id': None}
            recordings = search_recordings(recording=music, artist=real_artist)

            logging.debug(f"Searching {music} by {real_artist}")
            for recording in recordings['recording-list']:
                try:
                    recording['release-list']
                except KeyError:
                    logging.debug(recording)
                    continue
                for release in recording['release-list']:
                    try:
                        #print(release['artist-credit'][0]['name'].title(), release['release-group']['type'], release['title'].title())
                        is_album = release['release-group']['type'] == 'Album'
                        #is_artist = real_artist == release['artist-credit'][0]['name'].title()
                        #is_music = release['medium-list'][0]['track-list'][0]['title'].title() == music
                    except KeyError:
                        pass
                    else:
                        if is_album:# and is_artist:# and is_music:
                            try:
                                for genre in recording['tag-list']:
                                    if genre['count'] == '1':
                                        result['genre'] = genre['name'].title()
                                        break
                            except KeyError:
                                pass

                            try:
                                result['album_year'] = release['date'].split('-')[0]
                            except KeyError:
                                pass

                            try:
                                result['album_title'] = release['title'].title()
                                result['track_number'] = release['medium-list'][0]['track-list'][0]['number']
                                result['album_id'] = release['id']
                                break
                            except KeyError:
                                logging.warning("Failled some album key")
                                release['title'] = ''

                if result['album_id']:
                    break
            else:
                logging.warning("No album release in result")
                release['title'] = ''

            previous_title = result['album_title']

            if not album == 'Unknown Album':
                result['album_title'] = album # Remove when faith is restored

            try:
                if not previous_title == result['album_title']:
                    result['album_id'] = search_releases(artist=real_artist, release=result['album_title'], limit=1)['release-list'][0]['id']

                data = get_image_list(result['album_id'])
                for image in data["images"]:
                    if "Front" in image["types"] and image["approved"]:
                        result['album_art_url'] = image["thumbnails"]["large"]
                        album_art = request.urlopen(result['album_art_url']).read()
                        break
            except (musicbrainz.ResponseError, KeyError):
                pass
            except (error.URLError, ValueError, TypeError):
                logging.warning("Unable to get album art from URL")

            tags.update_to_v23()

            tags.add(id3.TIT2(encoding=3, text=u'{0}'.format(music)))
            tags.add(id3.TPE1(encoding=3, text=u'{0}'.format(real_artist)))

            if result['album_title']:
                tags.add(id3.TALB(encoding=3, text=u'{0}'.format(result['album_title'])))

            if result['album_year']:
                tags.add(id3.TDRC(encoding=3, text=u'{0}'.format(result['album_year'])))

            if result['track_number']:
                tags.add(id3.TRCK(encoding=3, text=u'{0}'.format(result['track_number'])))

            if result['genre']:
                tags.add(id3.TCON(encoding=3, text=u'{0}'.format(result['genre'])))

            if result['album_art_url']:
                for k in list(tags.keys()):
                    if k.startswith('APIC:'):
                        tags.pop(k)

                tags.add(id3.APIC(encoding=3, mime='image/png' if '.png' in result['album_art_url'] else 'image/jpeg',
                    type=id3.PictureType.COVER_FRONT, desc='Cover', data=album_art))

                #tags['APIC'] = id3.APIC(encoding=3, mime='image/png' if '.png' in result['album_art_url'] else 'image/jpeg',
                #    type=3, desc=u'Cover', data=album_art)

            #LYR, lyrics tag

            tags.save(music_path, v2_version=3)
            logging.warning(f"Artist: {real_artist} | Album: {result['album_title']} ({result['album_year']}) Cover URL: {result['album_art_url']} > New Album: {previous_title} | {result['track_number']} Music: {music} ({result['genre']})")

            if album is not result['album_title']:
                real_album_path = path.join(artist_path, ''.join(result['album_title'].split('/')))
                try:
                    mkdir(real_album_path)
                except FileExistsError:
                    pass
                rename(music_path, path.join(real_album_path, music + '.mp3'))

        if not listdir(album_path):
            rmdir(album_path)
