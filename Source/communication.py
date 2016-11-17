from collections import OrderedDict
from queue import Empty
from socket import setdefaulttimeout, socket, AF_INET, SO_REUSEADDR, SOL_SOCKET, SOCK_STREAM

#from Source.properties import System


def Retrieve(pipe, condition=False): # Queue exception handler

    try:
       output = pipe.get(condition)

    except Empty:
        return

    return output


def Listener(pipe): # Socket server setup

    pool = OrderedDict()
    server = socket()

    server.settimeout(1)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server.bind(('', 55400))

    while True:
        try:
            server.listen()
            client, address = server.accept()
            pool[address] = Process(target=Handler, args=(client, address)) # Creates a new process for each new user
            pool[address].start()

        except OSError as debug:
            if not type(debug).__name__ == 'timeout':
                print("\nError starting the server ({})\n\n".format(debug), end='spytify# \r') # Change with logging

        except KeyboardInterrupt:
            raise SystemExit


def Handler(client, address):

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
            servermessage = 'Invalid characteres'

        if arguments[0] == 'getsession': # Session begin request
            session = arguments[1]

            with open(File.login, 'r') as login:
                for line in reversed(list(login)):
                    servermessage = 'nologin'
                    logIP = line.split('|')[-1].split(':')[-2].strip()
                    logsession = line[-14:].strip()
                    logtry = line.split('|')[1].split(' ')[2].strip(':')

                    if logIP == address[0]:
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
            servermessage = 'Username or Password incorrect'

            if len(arguments) == 4:   
                action, username, password, session = arguments
                Authentication(username, password, 'Client | IP: ' + address[0] + ':' + str(address[1]) + ' - ' + session)

            else:
                action, username, password = arguments
                Authentication(username, password, 'Client | IP: ' + address[0] + ':' + str(address[1]))
            
        try:
            encryption = clientkey.encrypt(servermessage.encode('UTF-8'), 1024)
            client.send(encryption[0])

        except (BrokenPipeError, ConnectionResetError): # Refresh connection handle when hang by the client
            try:
                update = {IP: PID for IP, PID in connections.items() if PID != int(connections[address].pid)}

                with open(File.link, 'w', encoding='UTF-8') as writelink:
                    writelink.write(str(update))

                raise SystemExit

            except KeyError:
                raise SystemExit