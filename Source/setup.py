from crypt import crypt
from getpass import getpass
from os import makedirs, path
from queue import Queue
from sqlite3 import connect
from threading import Thread

from Source.animations import Progress


def Setup(sqlpath, loginpath, historypath, datapath, libpath): # It will only be called if the data directory doesn't exist, attempting a program install/repair

    print("A root password is needed.")

    while True:
        try:
            password = getpass("Choose a password: ")
            passwordcheck = getpass("Verify password: ")

            if password == passwordcheck:
                passwordhash = crypt(password) # SHA512 password hashing
                break

            print("Input doesn't match, try again.")

        except KeyboardInterrupt:
            print()
            raise SystemExit

        print("New root password created.")

    for folder in [datapath, libpath]:
        if not path.exists(folder) == True:
            makedirs(folder)

    pipe = Queue()
    animation = Thread(target=Progress, args=(pipe,))
    animation.start()

    for each in [sqlpath, loginpath, historypath]:
        with open(each, 'w', encoding='UTF-8') as openeach:
            openeach.write('')

    connection = connect(sqlpath)
    sql = connection.cursor()
    superuser, mail = 'root', 'root@spytify.com'

    sql.execute('create table Users (Username text primary key not NULL, Password text not NULL, Email text)')
    sql.execute('create table Library (ID integer primary key, Artist text, Music text, Album text, Duration text, Directory text)')
    sql.execute('create table Playlist (ID integer primary key, User text, Name text)')
    sql.execute('create table Track (ID integer primary key, LibrabryID integer, PlaylistID integer)')
    sql.execute('insert into Users values (?, ?, ?)', (superuser, passwordhash, mail))
    
    connection.commit()
    sql.close()
    pipe.put('Done', block=True)

    print("Setup done, reboot the program to start.")