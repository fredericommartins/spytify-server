from datetime import datetime

from Source.output import Text
from Source.properties import File


class History(object):

    def Read():

        #history = []
        
        with open(File.history, 'r') as openhistory: 
            openhistory.read()


    def Write(command): # Logs all executed commands

        if command: # To prevent newline logging
            with open(File.history, 'a') as openhistory: 
                openhistory.write("Date: {1} | # {0}\n".format(command, datetime.now().replace(microsecond=0)))


class Login(object):

    def Read(username):

        with open(File.login, 'r') as openlogin: # Use logging instead
            for entry in reversed(list(openlogin)): # Last user login
                if entry.split(' ')[1] == username:
                    return entry.split('|')[1].split(': ')[-1]

            return '{0}Não há login registado{1}'.format(Text.Italic, Text.Close)

    def Write(username, location, event):

        with open(File.login, 'a') as openlogin:
            openlogin.write('User: {0:<12} | Login {3}: {2} | In: {1}\n'.format(username, location, datetime.now().replace(microsecond=0), event))