from datetime import datetime
from os import path
from sqlite3 import connect
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
    #pid = '/var/run/spytify.pid'


class System:

    present = datetime.now().replace(microsecond=0)
    connection = connect(File.sql)
    sql = connection.cursor()
    port = 55400


class Text:

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