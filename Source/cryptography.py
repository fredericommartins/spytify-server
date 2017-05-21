from crypt import crypt

from Source.log import Login
from Source.properties import System


def Authentication(username, password, location): # User lookup and authentication # Remove location, find another way, vulnerable from client side

    System.sql.execute('select password from Users where username=?', (username,))
    
    hashed = System.sql.fetchone()
    if hashed:
        hashed = hashed[0]
        typed, salt = filter(None, hashed.split('$')[:3])
        password = crypt(password, '${}${}$'.format(typed, salt)) # Received hashed password

        if password == hashed:
            logentry = Login.Read(username)
            Login.Write(username, location, 'successful')

            return logentry

        else:
            Login.Write(username, location, 'failed')

    return None


# openssl genrsa -des3 -out server.orig.key 2048
# openssl rsa -in server.orig.key -out server.key
# openssl req -new -key server.key -out server.csr
# openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt