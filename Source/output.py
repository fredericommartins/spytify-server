from os import listdir, popen, system
from sqlite3 import sqlite_version
from textwrap import dedent
from time import sleep

from Source.communication import Retrieve
from Source.properties import Directory

def Help(): # Dynamic help

    print(dedent("""\
        Server:

          # server start                                         |  Start the socket server.
          # server stop                                          |  Stop the socket server.
          # server status                                        |  Print server status.
          # server connections                                   |  Print for active connections.
          # server kill PID                                      |  Terminate an existing connection.
          # server rebuild                                       |  Rebuild database based on musics in libr folder.

        SQL:

          # show tables                                          |  Print existing tables.
          # select * from sqlite_master where type='table'       |  Print existing tables and their schemas.
          # create table TABLE(TITLE text, TITLE int)            |  Create a new table.
          # drop table TABLE                                     |  Delete specified table.
          # select * from TABLE                                  |  Print table records.
          # insert into TABLE values('PARAMETER', 'PARAMETER')   |  Insert new line in table.
          # delete from TABLE where TITLE='PARAMETER'            |  Delete specified line.
    """))

    #print("Server:")

    #for each in class.server:
        #print(" # server {0:<40} |  {1}".format(each, each.help)) # each.help = annotations, each = methods

    #print("SQL:")

    #for each in class.sql:
        #print(" # {0:<40} |  {1}".format(each, each.help))


def Loading(pipe): # Database initial insertion animation

    system('setterm -cursor off')

    data = Retrieve(pipe, True)

    while data:
        freescreen = int(popen('stty size', 'r').read().split()[1]) - 26 # Calculate free screen size for progression bar
        libsize = len(listdir(Directory.library))
        percentage = round(data/libsize*100)
        progression = round(percentage*freescreen/100)

        print("{0}Building database: [{1:<{3}}] {2}%".format('\x1b[2K', '='*progression, percentage, freescreen), end='\r')

        data = Retrieve(pipe, True)

    print("\n")
    system('setterm -cursor on')


def Progress(pipe): # Installation and repairment process animation

    system('setterm -cursor off')

    data = False

    while not data:
        for char in ['|', '/', '-', '\\']:
            print("Setting up ", char, end='\r')
            sleep(0.12)
            data = Retrieve(pipe)
            
            if data:
                break

    system('setterm -cursor on')


def Welcome(login): # Program terminal welcome message

    system('clear')
    terminalwidth = popen('stty size', 'r').read().split()[1]

    print(dedent("""\
        {1}{0:^{5}}{4}


        Last login: {6} 
        Use {2}exit{4}, to leave the program.
        Use {2}help{4}, for program info.
        {3}SQLite3 {7}{4}
    """.format('Welcome to Spytify Server Administration Console', Text.Blue, Text.Underline, Text.Shade, Text.Close,
        terminalwidth, login, sqlite_version)))


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