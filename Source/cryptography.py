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

                return logentry

            else:
                Login.Write(username, location, 'failed')


# openssl genrsa -des3 -out server.orig.key 2048
# openssl rsa -in server.orig.key -out server.key
# openssl req -new -key server.key -out server.csr
# openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt