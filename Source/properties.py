from os import path
from sys import argv


class Directory:

    main = path.dirname(path.realpath(argv[0])) # To remove later
    #conf = '/etc/spytify'
    data = path.join(main, 'data')
    #data = '/var/lib/spytify/data'
    library = path.join(main, 'libr')
    #library = '/var/lib/spytify/library'
    log = path.join(main, 'data')
    #log = '/var/log/spytify'


class File:

    #conf = path.join(Directory.conf, 'spytify.conf')
    history = path.join(Directory.log, 'history.log')
    login = path.join(Directory.log, 'login.log')
    sql = path.join(Directory.data, 'database.sqlite3') # Replace sqlite3 with mariadb and other SQL servers, change code to make possible to establish connections between server and db