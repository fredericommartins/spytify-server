from crypt import crypt

from Source.log import Login
from Source.properties import System


def Authentication(username, password, location): # User lookup and authentication # Remove location, find another way, vulnerable from client side

    System.sql.execute('select * from Users where username=?', (username,))

    for column in System.sql:
        if column:
            hashedtext = column[1] # Database hashed password
            typed, salt, hashed = filter(None, hashedtext.split('$'))
            hashingtext = crypt(password, '${}${}$'.format(typed, salt)) # Received hashed password

            if hashingtext == hashedtext:
                logentry = Login.Read(username)
                Login.Write(username, location, 'successful')

                if location == 'Server':
                    return logentry

                elif location.split(' ')[0] == 'Client':
                    encryption = clientkey.encrypt('success'.encode('UTF-8'), 1024) # Encrypted message to the client
                    client.send(encryption[0]) 
                    Interface.Client(username, login)

            else:
                Login.Write(username, location, 'failed')