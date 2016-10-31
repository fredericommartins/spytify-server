from os import popen, system
from sys import stdout
from time import sleep

from Source.communication import Pipe


def Loading(pipe, libsize):

    system('setterm -cursor off')

    while True:
        n = Pipe(pipe, True)
        percentage = round(n/libsize*100)

        stdout.write('\r')
        stdout.write("Building database: [%-100s] %d%%" % ('='*percentage, percentage))
        stdout.flush()
        sleep(0.25)

    system('setterm -cursor on')


def Progress(pipe): # Installation and repairment process animation handler 

    system('setterm -cursor off')

    done = False

    while not done:
        for char in ['|', '/', '-', '\\']:
            print("Setting up ", char, end='\r')
            sleep(0.12)
            done = Pipe(pipe)
            
            if done:
                break

    system('setterm -cursor on')