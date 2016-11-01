from mutagen import mp3
from os import listdir


def Building(pipe, sql, connection, libpath):

    sortedfiles = sorted([line for line in listdir(libpath)]) # Sort files for database

    for n, mpfile in enumerate(sortedfiles): # Only .mp3 extensions will be inserted in the database
        if mpfile.endswith(".mp3"):
            try:
                artist, song, album = mpfile.rpartition('.')[0].split('-')

            except ValueError:   
                print("Music {} not inserted in database, due to format error".format(mpfile))

            length = ("{0:.2f}".format(mp3.MP3(libpath + '/' + mpfile).info.length/60)).replace('.', ':')
            sql.execute('insert into Library values(NULL, ?, ?, ?, ?, ?)', (artist, song, album, length, mpfile)) 
            connection.commit()
            pipe.put(n+1, block=True)

    pipe.put(False, block=True)


def Cleanup(sql, connection): # Library clean up for new loading at program start

    sql.execute('delete from Library')
    connection.commit()