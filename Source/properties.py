from os import path
from sys import argv


class Static:

    currentpath = path.dirname(path.realpath(argv[0]))
    datapath = currentpath + '/data'
    temppath = currentpath + '/temp'
    libpath = currentpath + '/libr'
    sqlpath = datapath + '/database.sqlite3'
    loginpath = datapath + '/login.log'
    historypath = datapath + '/history.log'
    linkpath = temppath + '/link.log'