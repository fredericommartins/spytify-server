from collections import OrderedDict
from crypt import crypt
from json import decoder, dumps, loads
from multiprocessing import Process
from queue import Empty
from re import match
from sqlite3 import Error
from socket import socket
from ssl import wrap_socket
from time import sleep

from Source.cryptography import Authentication
from Source.properties import File, System


def Retrieve(pipe, block=False): # Queue exception handler

    try:
       output = pipe.get(block)

    except Empty:
        return

    return output


def Listener(pipe=False): # Socket server setup

    pool = OrderedDict()
    server = socket()
    ciphers = "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:AES128-GCM-SHA256:AES128-SHA256:HIGH:"
    ciphers += "!aNULL:!eNULL:!EXPORT:!DSS:!DES:!RC4:!3DES:!MD5:!PSK" # Prevent unsafe chiphers usage 

    server.settimeout(2)

    server.bind(('', 44355))
    server.listen()

    while True:
        try:
            pipe.put(pool, block=False)
            client, address = server.accept()
            sslsocket = wrap_socket(client, server_side=True, certfile=File.crt, keyfile=File.key, ciphers=ciphers)
            pool[address] = Process(target=API, args=(sslsocket, address)) # Creates a new process for each new user
            pool[address].start()

        except OSError as debug:
            if not type(debug).__name__ == 'timeout':
                print("\nError starting the server ({})\n\n".format(debug)) # Change with logging

        except KeyboardInterrupt:
            raise SystemExit


class API(object): # Build RestAPI

    maximum_length = 24

    def __init__(self, client, address):

        call = {'getlibrary': self.Getlibrary,
                'getsession': self.Session,
                'login':      self.Login,
                'register':   self.Register}

        self.address = address[0]
        self.port = address[1]
        self._client = client

        try:
            while True:
                self._json = self.Listen()
                if self._json and call[self._json['action']](): # Argument passed by the client, being the first the action call
                    pass
                    #while True:
                    #    if self.Communicate():
                    #        break

        except (BrokenPipeError, ConnectionResetError):
            pass

        except KeyError:
            self.Reply('No such call {}'.format(self._json['action']), label='error')

            
    def Session(self):

        with open(File.login, 'r') as login:
            for line in reversed(list(login)):
                logIP = line.split('|')[-1].split(':')[-2].strip()
                logsession = line[-14:].strip()
                logtry = line.split('|')[1].split(' ')[2].strip(':')

                if logIP == self.address[0]:
                    if logtry == 'success' and node == logsession: # Check the user last login
                        self.username = line.split(':')[1].split('|')[0].strip()

                        for line in System.sql.execute('select * from Users where username = ?', (self.username,)):
                            self.username, password, mail = line

                        self.Reply('session {0}'.format(self.username), True) # In case user as chosen to save session
                        return

                    else: 
                        break # In case it has not saved session

        self.Reply('nologin', False, 'info')

    def Login(self):

        # if len(self.message) == 4:   
        #     action, self.username, password, session = self.message
        #     if Authentication(self.username, password, 'Client | IP: {0}:{1} - {2}'.format(self.address[0], str(self.address[1]), session)):
        #         return self.Reply('success', True)

        if Authentication(self._json['data']['username'], self._json['data']['password'], 'Client | IP: {0}:{1}'.format(self.address, self.port)):
            self.username = self._json['data']['username']
            return self.Reply('success', True)

        return self.Reply('Username or Password incorrect', False)

    def Register(self):

        for each in ['username', 'password', 'mail']: # Check for unknown characters
            try:
                field = self._json['data'][each]
            except KeyError:
                return self.Reply('Unknown field {}'.format(each), False)
            if not field: # Check if fields are not empty
                return self.Reply('{0} can\'t be empty'.format(each.capitalize()), False)
            for char in field:
                if char not in 'ABCDEFGHIJLMNOPQRSTUVXZKYWabcdefghijlmnopqrstuvxzkyw0123456789_.@':
                    return self.Reply('Invalid character {0} in {1}'.format(char, each), False)

        if not match(r'[^@]+@[^@]+\.[^@]+', self._json['data']['mail']): # Validate e-mail address
            return self.Reply('Invalid e-mail address')

        if len(self._json['data']['username']) > self.maximum_length: # Username maximum length
            return self.Reply('User can\'t have more than {0} characters'.format(self.username_length), False)

        try: # Insert new user in database
            System.sql.execute('insert into Users values(?, ?, ?)', (self._json['data']['username'], crypt(self._json['data']['password']), self._json['data']['mail']))
            System.connection.commit()

        except Error as debug:
            return self.Reply('Username already in use', False)

        return self.Reply('Registration success', True)


    def Getlibrary(self):

        listsend = []

        for line in System.sql.execute('select ID, Artist, Music, Album, Duration from Library'):
            if line:
                listsend.append(list(map(str, line)))

        sleep(5)
        self.Reply('Library data', action=True, data=listsend) # Sends all available music in the Library table

    def Communicate(self):

        clientmessage = self._client.read()
        action, *args = clientmessage.decode().split(' ')
        servermessage = 'nothing to say'

        if action == 'getlibrary': # Library request
            for line in System.sql.execute('select ID, Artist, Music, Album, Duration from Library'):
                print(line)
                if not len(line) == 0:
                    listline = list(line)
                    listline[0] = str(listline[0])
                    listsend.append("-".join(listline) + '|')
            sleep(5)
            self._client.write(''.join(listsend).encode()) # Sends all available music in the Library table
            servermessage = 0

        elif action == 'getplaylist': # User playlist request
            for line in System.sql.execute('select * from Playlist where User = ?', (self.username,)):
                listsend.append(str(line[0]) + '-' + line[2])

            servermessage = '|'.join(listsend)

            if not servermessage:
                servermessage = '<reply>Empty</reply>'

        elif action == 'getcover': # Album cover request, when not in client cache
            for line in System.sql.execute('select * from Library where ID = ?', (args[0],)):
                album = line[3]

            jpgpath = Directory.library + '/' + album + '.jpg'

            with open(jpgpath, 'rb') as openfile:
                readfile = openfile.read()
                self._client.write(readfile)
                servermessage = 0

        elif action == 'newplaylist': # New playlist request
            name = 'Playlist ' + args[0]
            System.sql.execute('insert into Playlist values (NULL, ?, ?)', (self.username, name))
            System.connection.commit()

            for line in System.sql.execute('select * from Playlist where User = ? and Name = ?', (self.username, name)):
                ID, self.username, name = line
                servermessage = str(ID) + '-' + name

        elif action == 'play': # Music stream request
            for line in System.sql.execute('select * from Library where ID = ?', (args[0],)):
                directory = line[5]

            songpath = Directory.library + '/' + directory

            with open(songpath, 'rb') as openfile:
                readfile = openfile.read()
                self._client.write(readfile)
                servermessage = 0
        
        try:
            print(servermessage)
            self.Reply(servermessage, action=True) # Information is sent via asymmetric encryption, RSA

        except AttributeError:
            self.Reply('stop') # File stream ending message

    def Listen(self):

        try:
            message = self._client.read().decode('utf-8')
            print(message)
            return loads(message)
        except decoder.JSONDecodeError:
            return self.Reply('Bad JSON construction', False)
        except UnicodeDecodeError:
            return self.Reply('Bad codec encode', False)

    def Reply(self, text, action=False, label=None, data=None):

        label = label or 'error'
        if action:
            label = label or 'success'

        reply = dumps({"message": {"type": label, "text": text}, "action": action, "data": data})
        self._client.write(reply.encode())

        return action