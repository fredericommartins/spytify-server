from argparse import ArgumentParser, RawDescriptionHelpFormatter
from os import listdir, path, popen, remove, rmdir
from shutil import copytree, Error, move
from sys import argv
from textwrap import dedent


def Parse():

    parser = ArgumentParser(prog=path.basename(__file__.rpartition('.')[0]), add_help=False, formatter_class=RawDescriptionHelpFormatter,
                description=dedent('''\
                              Download
                        -------------------
                        Music download conv
                    '''), epilog=dedent('''\
                        Check the git repository at https://github.com/fredericomateusmartins/spytify-server,
                        for more information about usage, documentation and bug report.\
                    ''')
                )

    optional = parser.add_argument_group('Flags')
    optional.add_argument('-d', '--destiny', metavar='path', type=str, help='Destiny path for music', required=True)
    optional.add_argument('-f', '--filter', metavar='exp', type=str, help='Artist comma delimited expression')
    optional.add_argument('-s', '--source', metavar='path', type=str, help='Source path with music', required=True)
    optional.add_argument('-h', '--help', action='help', help='Show this help message')
    
    if len(argv) == 1:
        parser.print_help()
        exit(1)

    return parser.parse_args()


args = Parse()

try:
    artist_filter = args.filter.split(',')
except AttributeError:
    artist_filter = None

failed_transfers = []

for artist in sorted(listdir(args.source)):
    artist_path = path.join(args.destiny, artist)
    print("Copying:\n {0}".format(artist))

    try:
        if not args.filter or args.filter and artist in artist_filter:
            copytree(path.join(args.source, artist), artist_path)
        else:
            continue    
    except (Error, OSError):
        failed_transfers.append(artist)
        continue

    for album in listdir(artist_path):
        album_path = path.join(artist_path, album)
        print("Moving:")
        
        for music in listdir(album_path):         
            music_path = path.join(album_path, music)
            print(" {0}".format(music))

            try:
                move(music_path, path.join(artist_path, music + '.mp3'))
            except (Error, OSError):
                remove(music_path)
                failed_transfers.append(music_path)

        screen_size = int(popen('stty size', 'r').read().split()[1])
        print("Deleting:\n {0}\n{1}".format(album, '-'*screen_size))
        rmdir(album_path)

print("Failed:\n ".format('\n'.join(failed_transfers)))
