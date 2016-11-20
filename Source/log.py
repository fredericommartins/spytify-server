from datetime import datetime

from Source.properties import File, Text


class History(object):

    def Read():
        
        with open(File.history, 'r') as openhistory: 
            openhistory.read()


    def Write(command): # Logs all executed commands

        if command: # To prevent newline logging
            with open(File.history, 'a') as openhistory: 
                openhistory.write("Date: {1} | # {0}\n".format(command, datetime.now().replace(microsecond=0)))


class Login(object):

    def Read(username):

        try:
            with open(File.login, 'r') as openlogin: # Use logging instead
                for entry in reversed(list(openlogin)): # Last user login registered
                    if entry.split(' ')[1] == username:
                        return entry.split('|')[1].split(': ')[-1]

                raise FileNotFoundError

        except FileNotFoundError:
            return '{0}Não há login registado{1}'.format(Text.Italic, Text.Close)

    def Write(username, location, event):

        with open(File.login, 'a') as openlogin:
            login = 'Login {0}: {1}'.format(event, datetime.now().replace(microsecond=0))
            openlogin.write('User: {0:<24} | {1:<37} | In: {2}\n'.format(username, login, location))