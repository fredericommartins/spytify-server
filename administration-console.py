#!/usr/bin/env python3

__author__ = "Frederico Martins"
__license__ = "GPLv3"
__version__ = 1.0

from ast import literal_eval
from collections import OrderedDict
from cmd import Cmd
from crypt import crypt
from Crypto import Random # Change for python built-in cryptography module
from Crypto.PublicKey import RSA
from datetime import datetime
from getpass import getpass
from multiprocessing import Process
from os import kill, path, popen, system
from pickle import dumps, loads
from queue import Queue
from readline import parse_and_bind
from signal import SIGKILL
from socket import socket, AF_INET, SO_REUSEADDR, SOL_SOCKET, SOCK_STREAM
from sqlite3 import connect, Error, sqlite_version
from textwrap import dedent
from threading import Thread
from time import sleep

from Source.cryptography import Authentication
from Source.database import Building, Cleanup, Formatted, Timing
from Source.log import History, Login
from Source.output import Help
from Source.process import Server
from Source.properties import Directory, File, System, Text
from Source.setup import Setup


class Startup(object):

    def __init__(self):

        if not path.exists(Directory.data): # Chech if a repair/install is needed
            Setup()
            raise SystemExit

        self.Login()
        Cleanup(System.sql, System.connection) # If --skip-database-build parameter invoked
        Building(System.sql, System.connection)
        Console().cmdloop(intro=self.Welcome())


    def Login(self):

        while True:
            password = getpass("Enter password (root): ")
            self.login = Authentication('root', password, 'Server')
            if self.login:
                break

            sleep(3)
            print("Wrong password.")


    def Welcome(self): # Program terminal welcome message

        system('clear')
        terminalwidth = popen('stty size', 'r').read().split()[1]

        print(dedent("""\
            {1}{0:^{5}}{4}


            Last login: {6} 
            Use {2}exit{4}, to leave the program.
            Use {2}help{4}, for program info.
            {3}SQLite3 {7}{4}
        """.format('Welcome to Spytify Server Administration Console', Text.Blue, Text.Underline, Text.Shade, Text.Close,
            terminalwidth, self.login, sqlite_version)))


class Console(Cmd):
    
    prompt = 'spytify# '
    file = None
    server = Server()

    def precmd(self, line):

        if line:
            print()

        self.previoustime = datetime.today().timestamp()
        History.Write(line)
        return line


    def postcmd(self, stop, line):

        if line:
            print()


    def emptyline(self):

        pass


    def do_help(self, arg):

        #if arg:

        Help()


    def do_exit(self, arg):

        System.sql.close()
        raise SystemExit


    def do_server(self, arg):

        if arg == 'start':
            self.server.Start()

        elif arg == 'stop':
            self.server.Stop()
            
        else:
            print('invalid command, use: server {start,stop}')


    def complete_server(self, text, line, begidx, endidx):

        auto = line.partition(' ')[2]
        offset = len(auto) - len(text)
        return [arg[offset:] for arg in ['start', 'stop'] if arg.startswith(auto)]


def Gorila(login): # Interface

    while True:
        try:
            command = input("spytify# ")
            lowcommand = command.lower()
            splitcommand = lowcommand.split(' ')
            previoustime = datetime.today().timestamp()

            History(command)

            #try:
            #    getattr(self, )

            if lowcommand == 'exit':
                raise KeyboardInterrupt

            elif not lowcommand:
                pass

            elif lowcommand == 'help':
                Help()
            
            elif lowcommand == 'server start':
                if not serverprocess.is_alive() == True:
                    serverprocess.start()
                    print("Server is currently {0}on{1}.\n".format(Text.Green, Text.Close))

                elif serverprocess.is_alive() == True:
                    print("Error, the server is already {0}on{1}.\n".format(Text.Green, Text.Close))

            elif lowcommand == 'server stop':
                if serverprocess.is_alive() == True:
                    serverprocess.terminate()

                    with open(File.link, 'r') as readlink:
                        connections = [literal_eval(line) for line in readlink][0]

                        for PID in connections.values(): # Kill all server connections/processes
                            kill(int(PID), SIGKILL)

                    with open(File.link, 'w', encoding='UTF-8') as writelink:
                        writelink.write('{}')

                    print("Server is currently {0}off{1}.\n".format(Text.Red, Text.Close))

                elif not serverprocess.is_alive() == True:
                    print("Error, the server is already {0}off{1}.\n".format(Text.Red, Text.Close))

            elif lowcommand == 'server status':
                if serverprocess.is_alive() == True:
                    print("{0}On{1}\n".format(Text.Green, Text.Close))

                elif not serverprocess.is_alive() == True:
                    print("{0}Off{1}\n".format(Text.Red, Text.Close))

            elif lowcommand == 'server connections':
                if serverprocess.is_alive() == True:
                    with open(File.link, 'r') as readlink:
                        connections = [literal_eval(line) for line in readlink][0]

                        if len(connections) == 0:
                            print("No active server connections.")

                        else:
                            for line in connections:
                                print("IP - {:<15} | PID - {}".format(line, connections[line]))

                        print()

                elif not serverprocess.is_alive() == True:
                    print("The server is not on.\n")

            elif all([splitcommand[0] == 'server', splitcommand[1] == 'kill']):
                with open(File.link, 'r') as readlink:
                    connections = [literal_eval(line) for line in readlink][0]

                    if int(splitcommand[2]) not in connections.values():
                        print("PID doesn't exist.")

                    else:
                        kill(int(splitcommand[2]), SIGKILL)

                        update = {IP: PID for IP, PID in connections.items() if PID != int(splitcommand[2])}

                        with open(File.link, 'w', encoding='UTF-8') as writelink:
                            writelink.write(str(update))

                        print("Connection killed.")

                    print()


            elif lowcommand ==  'server rebuild':
                animation = Thread(target=Loading, args=(pipe,))
                animation.start()
                Cleanup(sql, connection) # If --skip-database-build parameter invoked
                Building(pipe, sql, connection)
                animation.join()

            elif lowcommand == 'show tables':
                command = 'select name from sqlite_master where type=\'table\''
                Formatted(sql,  command)
                Timing(previoustime)

            elif splitcommand[0] == 'select':
                Formatted(sql, command) # Content is printed in a sorted fashion and with a sql-like table
                Timing(previoustime)

            elif all([splitcommand[0] == 'insert', splitcommand[2] == 'users']): # For every new user, the password is automatically converted to SHA512
                passwordhash = '\'' + crypt(command.split(', ')[1].strip('\'')) + '\'' 
                command = "{0}, {1}, {2}".format(command.split(', ')[0], passwordhash, command.split(', ')[2])
                sql.execute(command)
                connection.commit()

                Timing(previoustime)

            else:
                sql.execute(command)
                connection.commit()

                Timing(previoustime)

        except IndexError:
            print("Invalid command.")

        except UnboundLocalError:
            print("{0}The table has no records.{1}\n".format(Text.Italic, Text.Close))

        except AssertionError:
            print("Reboot the program in order to start the server again.\n")

        except Error as debug:
            print("Error ({0}).\n".format(debug))

        except KeyboardInterrupt:
            try:
                if not lowcommand == 'exit':
                    raise NameError

            except NameError:
                print()

            if serverprocess.is_alive() == True:
                serverprocess.terminate()

            try:
                with open(File.link, 'r') as readlink:
                    connections = [literal_eval(line) for line in readlink][0]

                    if not len(connections) == 0:
                        for PID in connections.values():
                            kill(int(PID), SIGKILL)

                    raise ProcessLookupError

            except ProcessLookupError:
                with open(File.link, 'w', encoding='UTF-8') as writelink:
                    writelink.write('{}')

                sql.close()
                raise SystemExit


try:
    Startup()

except KeyboardInterrupt:
    System.sql.close(), print()
    raise SystemExit