from datetime import datetime
from mutagen import mp3
from os import listdir, path
from queue import Queue
from threading import Thread

from Source.output import Loading, Text
from Source.properties import Directory


def Building(sql, connection):

    pipe = Queue()
    animation = Thread(target=Loading, args=(pipe,))
    sortedfiles = sorted([line for line in listdir(Directory.library)]) # Sort files for database
    
    animation.start()

    try:
        for n, mpfile in enumerate(sortedfiles): # Only .mp3 extensions will be inserted in the database
            if mpfile.endswith(".mp3"):
                try:
                    artist, song, album = mpfile.rpartition('.')[0].split('-')

                except ValueError:   
                    print("Music {} not inserted in database, due to format error".format(mpfile))

                length = ("{0:.2f}".format(mp3.MP3(path.join(Directory.library, mpfile)).info.length/60)).replace('.', ':')
                sql.execute('insert into Library values(NULL, ?, ?, ?, ?, ?)', (artist, song, album, length, mpfile)) 
                connection.commit()
                pipe.put(n+1, block=True)

    except KeyboardInterrupt:
        pass

    pipe.put(False, block=True)
    animation.join() # Wait for thread end to prevent output damage


def Cleanup(sql, connection): # Library clean up for new loading at program start

    sql.execute('delete from Library')
    connection.commit()


def Formatted(sql, command): # Database table formatted output

    border, parameters, size = [], [], []
    columntitle = [title[0] for title in sql.execute(command).description]

    for line in sql.execute(command): # Table size
        increment = 0

        while not len(line) == increment:
            stringline = len(str(line[increment]))

            try:
                if stringline > size[increment]:
                    size[increment] = stringline

            except IndexError:
                if len(columntitle[increment]) < stringline:
                    size.append(stringline)

                else:
                    size.append(len(columntitle[increment]))

            increment += 1

        increment = 0
    
    for argument in line: # Table structure
        lineformat = []
        parameters.append('| {:^' + str(size[increment]) + '} ')

        while not size[increment] ==  len(lineformat) - 2:
            lineformat.append('-')

        border.append('+' + ''.join(lineformat))
        increment += 1

    finalformat = ''.join(border) + '+'
    finalargument = ''.join(parameters) + '|'

    print(finalformat)
    print(finalargument.format(*columntitle))
    print(finalformat)

    for line in sql.execute(command):
        print(finalargument.format(*line))

    print(finalformat)


def Timing(previoustime):

    querytime = round(datetime.today().timestamp() - previoustime, 4)

    print(" {1}rows affected{2} ({0:.2f} sec.)\n".format(querytime, Text.Italic, Text.Close))