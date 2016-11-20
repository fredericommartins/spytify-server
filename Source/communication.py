from collections import OrderedDict
from crypt import crypt
from multiprocessing import Process
from queue import Empty
from socket import socket
from ssl import wrap_socket

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
    try:
        server.bind(('', 44355))
        server.listen()

    except OSError as debug:
        print("\n{0}".format(debug))

    while True:
        try:
            pipe.put(pool, block=False)
            client, address = server.accept()
            sslsocket = wrap_socket(client, server_side=True, certfile="Others/server.crt", keyfile="Others/server.key", ciphers=ciphers)
            pool[address] = Process(target=API, args=(sslsocket, address)) # Creates a new process for each new user
            pool[address].start()

        except OSError as debug:
            if not type(debug).__name__ == 'timeout':
                print("\nError starting the server ({})\n\n".format(debug)) # Change with logging

        except KeyboardInterrupt:
            raise SystemExit


class API(object):

    def __init__(self, client, address):

        self.address = address
        self.client = client

        while True:
            self.message = self.client.read().decode().split(' ')
            if self.Assert():
                self.Session()
                break

            self.client.write('Invalid characteres'.encode())

            #client.write('success'.encode()) 
            #Interface.Client(username, login)

    
    def Assert(self):

        try:
            for each in message:
                if not each:
                    raise ValueError

                for char in each:
                    if char not in 'ABCDEFGHIJLMNOPQRSTUVXZKYWabcdefghijlmnopqrstuvxzkyw0123456789_.@':
                        raise ValueError

        except ValueError:
            return False

        return True


    def Session(self):

        if action == 'getsession': # Session begin request # automatic login
            with open(File.login, 'r') as login:
                for line in reversed(list(login)):
                    servermessage = 'nologin'
                    logIP = line.split('|')[-1].split(':')[-2].strip()
                    logsession = line[-14:].strip()
                    logtry = line.split('|')[1].split(' ')[2].strip(':')

                    if logIP == address[0]:
                        if logtry == 'success' and node == logsession: # Check the user last login
                            username = line.split(':')[1].split('|')[0].strip() 

                            for line in sql.execute('select * from Users where username = ?', (username,)):
                                username, password, mail = line

                            servermessage = 'session ' + username # In case user as chosen to save session
                            break

                        else: 
                            break # In case it has not saved session

        elif action == 'register' and len(arguments) == 4: # New user request 
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

        elif action == 'login': #and len(arguments) == 3: # Login request
            servermessage = 'Username or Password incorrect'

            if len(arguments) == 4:   
                action, username, password, session = arguments
                Authentication(username, password, 'Client | IP: ' + address[0] + ':' + str(address[1]) + ' - ' + session)

            else:
                action, username, password = arguments
                Authentication(username, password, 'Client | IP: ' + address[0] + ':' + str(address[1]))
            
        try:
            self.client.write(servermessage.encode())

        except (BrokenPipeError, ConnectionResetError): # Refresh connection handle when hang by the client
            try:
                update = {IP: PID for IP, PID in connections.items() if PID != int(connections[address].pid)}

                with open(File.link, 'w', encoding='UTF-8') as writelink:
                    writelink.write(str(update))

                raise SystemExit

            except KeyError:
                raise SystemExit


    def Client(username, login): # Client handshake

        while True:
            try:
                self.Communicate(username)

            except (BrokenPipeError, ConnectionResetError): # Refresh the connections, if a client hangs
                try:
                    update = {IP: PID for IP, PID in connections.items() if PID != int(connections[clientIP[0]])}

                    with open(File.link, 'w', encoding='UTF-8') as writelink:
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

            jpgpath = Directory.library + '/' + album + '.jpg'

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

            songpath = Directory.library + '/' + directory

            with open(songpath, 'rb') as openfile:
                readfile = openfile.read()
                client.send(readfile)
                servermessage = 0
        
        try:
            encryption = clientkey.encrypt(servermessage.encode('UTF-8'), 1024) # Files are sent unencrypted
            client.send(encryption[0]) # Information is sent via asymmetric encryption, RSA

        except AttributeError:
            client.send('stop'.encode()) # File stream ending message