#!/usr/bin/env python3

__author__ = "Frederico Martins"
__license__ = "GPLv3"
__version__ = 1.0

from ast import literal_eval
from crypt import crypt
from Crypto import Random
from Crypto.PublicKey import RSA
from datetime import datetime
from getpass import getpass
from multiprocessing import Process
from mutagen import mp3
from os import kill, listdir, path, popen, remove, system
from pickle import dumps, loads
from queue import Queue
from readline import parse_and_bind
from signal import SIGKILL
from socket import socket, AF_INET, SO_REUSEADDR, SOL_SOCKET, SOCK_STREAM
from sqlite3 import connect, Error, sqlite_version
from sys import argv
from threading import Thread

from Source.setup import Setup # Spytify modules
from Source.animations import Loading


class Interface():

    def Server(login):

        system('clear') 
        terminalwidth = "{:^" + popen('stty size', 'r').read().split()[1] + "}\n" + "\n"
        serverprocess = Process(target=Bond, args=()) # Socket server process

        sql.execute('delete from Library') # Lib clean up, for new loading at program start
        connection.commit()

        sortedfiles = sorted([line for line in listdir(libpath)]) # Sort files for database
        pipe = Queue()

        for n, mpfile in enumerate(sortedfiles): # Only .mp3 extensions will be inserted in the database
            animation = Thread(target=Loading, args=(pipe,len(sortedfiles)))
            
            if mpfile.endswith(".mp3"):
                artist, song, album = mpfile.rpartition('.')[0].split('-')
                length = ("{0:.2f}".format(mp3.MP3(libpath + '/' + mpfile).info.length/60)).replace('.', ':')

                sql.execute('insert into Library values(NULL, ?, ?, ?, ?, ?)', (artist, song, album, length, mpfile)) 
                connection.commit()
                pipe.put(n, block=False)

        print(terminalwidth.format(Colors.Blue + "Welcome to Spytify Server Administration Console" + Colors.Close))
        print("Last login:", login, "\n") 
        print("Use", Colors.Underline + "exit" + Colors.Close + ", to leave the program.")
        print("Use", Colors.Underline + "help" + Colors.Close + ", for program info.")
        print(Colors.Shade + "SQLite3 " + sqlite_version + " v." + Colors.Close, "\n") # Welcome screen 

        while True:
            try:
                command = input("root# ")

                with open(historypath, 'a') as history: # Writes all executed commands in history.log
                    history.write("Date: {1} | # {0}\n".format(command, datetime.now().replace(microsecond=0)))

                lowcommand = command.lower()
                splitcommand = lowcommand.split(' ')
                previoustime = datetime.today().timestamp()

                if lowcommand == '':
                    continue

                elif lowcommand == 'exit':
                    raise KeyboardInterrupt

                else:
                    print()

                if lowcommand == 'help':
                    print("Server:", "\n")
                    print("# server start                                            | Start the socket server.")
                    print("# server stop                                             | Stop the socket server.")
                    print("# server status                                           | Print server status.")
                    print("# server connections                                      | Print for active connections.")
                    print("# server kill PID                                         | Terminate an existing connection.", "\n")
                    print("Database:", "\n")
                    print("# show tables                                             | Print existing tables.")
                    print("# select * from sqlite_master where type='table'          | Print existing tables and their schemas.")
                    print("# create table TABLE(TITLE text, TITLE int)               | Create a new table.")
                    print("# drop table TABLE                                        | Delete specified table.")
                    print("# select * from TABLE                                     | Print table records.")
                    print("# insert into TABLE values('PARAMETER', 'PARAMETER')      | Insert new line in table.")
                    print("# delete from TABLE where TITLE='PARAMETER'               | Delete specified line.", "\n")
                
                elif lowcommand == 'server start':
                    if not serverprocess.is_alive() == True:
                        serverprocess.start()
                        print("Server is currently " + Colors.Green + "on" + Colors.Close + ".\n")

                    elif serverprocess.is_alive() == True:
                        print("Error, the server is already" + Colors.Green + "on" + Colors.Close + ".\n")

                elif lowcommand == 'server stop':
                    if serverprocess.is_alive() == True:
                        serverprocess.terminate()

                        with open(linkpath, 'r') as readlink:
                            connections = [literal_eval(line) for line in readlink][0]

                            for PID in connections.values(): # Kill all server connections/processes
                                kill(int(PID), SIGKILL)

                        with open(linkpath, 'w', encoding='UTF-8') as writelink:
                            writelink.write('{}')

                        print("Server is currently " + Colors.Red + "off" + Colors.Close + ".\n")

                    elif not serverprocess.is_alive() == True:
                        print("Error, the server is already " + Colors.Red + "off" + Colors.Close + ".\n")

                elif lowcommand == 'server status':
                    if serverprocess.is_alive() == True:
                        print(Colors.Green + "On" + Colors.Close + "\n")

                    elif not serverprocess.is_alive() == True:
                        print(Colors.Red + "Off" + Colors.Close + "\n")

                elif lowcommand == 'server connections':
                    if serverprocess.is_alive() == True:
                        with open(linkpath, 'r') as readlink:
                            connections = [literal_eval(line) for line in readlink][0]

                            if len(connections) == 0:
                                print("No active server connections.")

                            else:
                                for line in connections:
                                    print("IP - {:<15} | PID - {}".format(line, connections[line]))

                            print()

                    elif not serverprocess.is_alive() == True:
                        print("The server is not on.", "\n")

                elif all([splitcommand[0] == 'server', splitcommand[1] == 'kill']):
                    with open(linkpath, 'r') as readlink:
                        connections = [literal_eval(line) for line in readlink][0]

                        if int(splitcommand[2]) not in connections.values():
                            print("PID doesn't exist.")

                        else:
                            kill(int(splitcommand[2]), SIGKILL)

                            update = {IP: PID for IP, PID in connections.items() if PID != int(splitcommand[2])}

                            with open(linkpath, 'w', encoding='UTF-8') as writelink:
                                writelink.write(str(update))

                            print("Connection killed.")

                        print()

                elif lowcommand == 'show tables':
                    command = 'select name from sqlite_master where type=\'table\''
                    ShowTable(command)

                    print("Time:", round(datetime.today().timestamp() - previoustime, 5), "s\n")

                elif splitcommand[0] == 'select':
                    ShowTable(command) # Content is printed in a sorted fashion and with a sql-like table

                    print("Time:", round(datetime.today().timestamp() - previoustime, 5), "s\n")

                elif all([splitcommand[0] == 'insert', splitcommand[2] == 'users']): # For every new user, the password is automatically converted to SHA512
                    passwordhash = '\'' + crypt(command.split(', ')[1].strip('\'')) + '\'' 
                    command = "{0}, {1}, {2}".format(command.split(', ')[0], passwordhash, command.split(', ')[2])
                    sql.execute(command)
                    connection.commit()

                    print("Time:", round(datetime.today().timestamp() - previoustime, 5), "s\n")

                else:
                    sql.execute(command)
                    connection.commit()

                    print("Time:", round(datetime.today().timestamp() - previoustime, 5), "s\n")

            except IndexError:
                print("Error ( invalid command )", "\n")

            except UnboundLocalError:
                print(Colors.Italic + "The table has no records." + Colors.Close, "\n")

            except AssertionError:
                print("Reboot the program in order to start the server again.", "\n")

            except Error as debug:
                print("Error (", debug, ")", "\n")

            except KeyboardInterrupt:
                try:
                    if not lowcommand == 'exit':
                        raise NameError

                except NameError:
                    print()

                if serverprocess.is_alive() == True:
                    serverprocess.terminate()

                try:
                    with open(linkpath, 'r') as readlink:
                        connections = [literal_eval(line) for line in readlink][0]

                        if not len(connections) == 0:
                            for PID in connections.values():
                                kill(int(PID), SIGKILL)

                        raise ProcessLookupError

                except ProcessLookupError:
                    with open(linkpath, 'w', encoding='UTF-8') as writelink:
                        writelink.write('{}')

                    sql.close()
                    raise SystemExit


    def Client(username, login): # Client handshake

        while True:
            try:
                Interface.Communicate(username)

            except (BrokenPipeError, ConnectionResetError): # Refresh the connections, if a client hangs
                try:
                    update = {IP: PID for IP, PID in connections.items() if PID != int(connections[clientIP[0]])}

                    with open(linkpath, 'w', encoding='UTF-8') as writelink:
                        writelink.write(str(update))

                    raise SystemExit

                except KeyError:
                    raise SystemExit


    def Communicate(username):

        clientmessage = client.recv(1024)
        decryption = str(keys.decrypt(clientmessage))[1:].strip('\'')
        servermessage = ''
        listsend = []

        if decryption == 'getlibrary': # Library request
            for line in sql.execute('select * from Library'):
                if not len(line) == 0:
                    listline = list(line)
                    listline[0] = str(listline[0])
                    listsend.append("-".join(listline) + '|')

            client.send(''.join(listsend).encode()) # Sends all available music in the Library table
            servermessage = 0

        elif decryption == 'getplaylist': # User playlist request
            for line in sql.execute('select * from Playlist where User = ?', (username,)):
                listsend.append(str(line[0]) + '-' + line[2])

            servermessage = '|'.join(listsend)

        elif decryption.split(' ')[0] == 'getcover': # Album cover request, when not in client cache
            for line in sql.execute('select * from Library where ID = ?', (decryption.split(' ')[1],)):
                album = line[3]

            jpgpath = libpath + '/' + album + '.jpg'

            with open(jpgpath, 'rb') as openfile:
                readfile = openfile.read()
                client.send(readfile)
                servermessage = 0

        elif decryption.split(' ')[0] == 'newplaylist': # New playlist request
            name = 'Playlist ' + decryption.split(' ')[1]
            sql.execute('insert into Playlist values (NULL, ?, ?)', (username, name))
            connection.commit()

            for line in sql.execute('select * from Playlist where User = ? and Name = ?', (username, name)):
                ID, username, name = line
                servermessage = str(ID) + '-' + name

        elif decryption.split(' ')[0] == 'play': # Music stream request
            for line in sql.execute('select * from Library where ID = ?', (decryption.split(' ')[1],)):
                directory = line[5]

            songpath = libpath + '/' + directory

            with open(songpath, 'rb') as openfile:
                readfile = openfile.read()
                client.send(readfile)
                servermessage = 0
        
        try:
            encryption = clientkey.encrypt(servermessage.encode('UTF-8'), 1024) # Files are sent unencrypted
            client.send(encryption[0]) # Information is sent via asymmetric encryption, RSA

        except AttributeError:
            client.send('stop'.encode()) # File stream ending message


def Authentication(username, password, location): # User lookup and authentication

    sql.execute ('select * from Users')

    try:
        hashedtext = [line[1] for line in sql if line[0] == username][0] # Database hashed password
        hashingtext = crypt(password, '${}${}$'.format(hashedtext.split('$')[1], hashedtext[3:19])) # Sent hashed password

    except IndexError: # No user in database
        hashedtext, hashingtext = 'no', 'user'

    if hashingtext == hashedtext:
        with open(loginpath, 'r') as readlog, open(loginpath, 'a') as writelog:
            writelog.write("User: {0:<12} | Login success: {2} | In: {1}\n".format(username, location, datetime.now().replace(microsecond=0)))
            login = Colors.Italic + "Não há login registado" + Colors.Close

            for line in readlog: # Last user login
                if line.split(' ')[1] == username:
                    login = line.split('|')[1][16:-1]

        if location == 'Server':
            return login

        elif location.split(' ')[0] == 'Client':
            encryption = clientkey.encrypt('success'.encode('UTF-8'), 1024) # Encrypted message to the client
            client.send(encryption[0]) 
            Interface.Client(username, login)

    else:
        if not hashedtext + hashingtext == 'nouser':
            with open(loginpath, 'a') as writelog: # Logs failed password matches in login.log
                writelog.write("User: {0:<12} | Login attempt: {2} | In: {1}\n".format(username, location, datetime.now().replace(microsecond=0)))


def Bond(): # Socket server setup

    global client, clientIP, connections

    n = 0
    connections = {}
    connectionprocess = []

    try:
        server = socket()
        server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server.bind(('', 55400))

        while True:
            server.listen(5)
            client, clientIP = server.accept()

            connectionprocess.append(Process(target=Link)) # Creates a new process for each new user
            connectionprocess[n].start()
            connections[clientIP[0]] = connectionprocess[n].pid # Dictionary with client IP and PID

            with open(linkpath, 'w', encoding='UTF-8') as writelink: # Information sharing with the parent process
                writelink.write(str(connections))

            n += 1

    except OSError as debug:
        print("\n")
        print("Error starting the server (%s)\n\n" % debug, end="\rroot# ")

    except KeyboardInterrupt:
        raise SystemExit


def Link():

    global clientkey, keys

    keys = RSA.generate(1024, Random.new().read) # Public and private key creation, RSA
    serverkey = dumps(keys.publickey()) # Server public key to send
    client.send(serverkey)
    clientkey = loads(client.recv(1024)) # Client public key

    while True:

        clientmessage = client.recv(1024)
        decryption = str(keys.decrypt(clientmessage))[1:].strip('\'') # Encrypted message sent by the client, to decrypt
        arguments = decryption.split(' ')

        for argument in arguments:
            if argument == '':
                arguments = 'error'
                break

            for character in argument:
                if character not in 'ABCDEFGHIJLMNOPQRSTUVXZKYWabcdefghijlmnopqrstuvxzkyw0123456789_.@':
                    arguments = 'error'
                    break 
        
        if arguments == None or arguments == 'error':
            arguments = 'error'
            servermessage = 'error'

        if arguments[0] == 'getsession': # Session begin request
            session = arguments[1]

            with open(loginpath, 'r') as login:
                for line in reversed(list(login)):
                    servermessage = 'nologin'
                    logIP = line.split('|')[-1].split(':')[-2].strip()
                    logsession = line[-14:].strip()
                    logtry = line.split('|')[1].split(' ')[2].strip(':')

                    if logIP == clientIP[0]:
                        if logtry == 'success' and session == logsession: # Check the user last login
                            username = line.split(':')[1].split('|')[0].strip() 

                            for line in sql.execute('select * from Users where username = ?', (username,)):
                                username, password, mail = line

                            servermessage = 'session ' + username # In case user as chosen to save session
                            break

                        else: 
                            break # In case it has not saved session

        elif arguments[0] == 'register' and len(arguments) == 4: # New user request 
            action, username, password, mail = arguments
            if len(username) >= 13:
                servermessage = 'usertoolong' # Username can't be more than 12 characters long

            else:
                passwordhash = crypt(password) # Password encryption

                try:
                    sql.execute('insert into Users values(?, ?, ?)', (username, passwordhash, mail))
                    connection.commit() # Inserted user in database
                    servermessage = 'registered'

                except Error as debug:
                    servermessage = 'sqlerror'

        elif arguments[0] == 'login': #and len(arguments) == 3: # Login request
            servermessage = 'unmatched'

            if len(arguments) == 4:   
                action, username, password, session = arguments
                Authentication(username, password, 'Client | IP: ' + clientIP[0] + ':' + str(clientIP[1]) + ' - ' + session)

            else:
                action, username, password = arguments
                Authentication(username, password, 'Client | IP: ' + clientIP[0] + ':' + str(clientIP[1]))
            
        try:
            encryption = clientkey.encrypt(servermessage.encode('UTF-8'), 1024)
            client.send(encryption[0])

        except (BrokenPipeError, ConnectionResetError): # Refresh connection handle when hang by the client
            try:
                update = {IP: PID for IP, PID in connections.items() if PID != int(connections[clientIP[0]])}

                with open(linkpath, 'w', encoding='UTF-8') as writelink:
                    writelink.write(str(update))

                raise SystemExit

            except KeyError:
                raise SystemExit


class Colors:

    Cyan = '\033[96m'
    Blue = '\033[94m'
    Green = '\033[92m'
    Yellow = '\033[93m'
    Red = '\033[91m'
    Bold = '\033[1m'
    Underline = '\033[4m'
    Shade = '\033[2m'
    Italic = '\033[3m'
    Close = '\033[0m'


def ShowTable(command): # Database table formatted output

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


currentpath = path.dirname(path.realpath(argv[0])) # pathdict
datapath = currentpath + '/data'
temppath = currentpath + '/temp'
libpath = currentpath + '/libr'
sqlpath = datapath + '/database.sqlite3'
loginpath = datapath + '/login.log'
historypath = datapath + '/history.log'
linkpath = temppath + '/link.log'

try:
    if not path.exists(datapath): # Chech if a repair/install is needed
        Setup(sqlpath, loginpath, historypath, datapath, libpath)
        raise SystemExit

    connection = connect(sqlpath)
    sql = connection.cursor()

    while True:
        password = getpass("Enter password (root): ")
        login = Authentication('root', password, 'Server')

        if login:
            break

        print("Wrong password.")

    Interface.Server(login)

except KeyboardInterrupt:
    sql.close(), print()
    raise SystemExit