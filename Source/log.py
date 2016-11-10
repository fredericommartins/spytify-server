from datetime import datetime

from Source.properties import File


def History(command): # Logs all executed commands in history.log

    if command: # To prevent newline logging
        with open(File.history, 'a') as history: 
            history.write("Date: {1} | # {0}\n".format(command, datetime.now().replace(microsecond=0)))