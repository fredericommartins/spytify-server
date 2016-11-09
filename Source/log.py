from datetime import datetime


def History(command, historypath): # Logs all executed commands in history.log

    if command: # To prevent newline logging
        with open(historypath, 'a') as history: 
            history.write("Date: {1} | # {0}\n".format(command, datetime.now().replace(microsecond=0)))