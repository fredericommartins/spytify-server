from os import path
from sys import argv


class Directory:

    main = path.dirname(path.realpath(argv[0])) # To remove later
    data = main + '/data'
    #data = '/var/lib/spytify/data'
    library = main + '/libr'
    #library = '/var/lib/spytify/library'
    log = main + '/data'
    #log = '/var/log/spytify'


class File:

    history = Directory.log + '/history.log'
    login = Directory.log + '/login.log'
    sql = Directory.data + '/database.sqlite3' # Replace sqlite3 with mariadb and other SQL servers, change code to make possible to establish connections between server and db