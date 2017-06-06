from os import listdir, path, popen, remove, rmdir
from shutil import copytree, Error, move
from sys import argv


failed_transfers = [] 

for artist in sorted(listdir(argv[1])):
    artist_path = path.join(argv[2], artist)
    print("Copying:\n {0}".format(artist))

    try:
        copytree(path.join(argv[1], artist), artist_path)
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
                move(music_path, path.join(artist_path, '.'.join((music, 'mp3'))))
            except (Error, OSError):
                remove(music_path)
                failed_transfers.append(music_path)

        screen_size = int(popen('stty size', 'r').read().split()[1])
        print("Deleting:\n {0}\n{1}".format(album, '-'*screen_size))
        rmdir(album_path)

print("Failed:\n ".format('\n'.join(failed_transfers)))