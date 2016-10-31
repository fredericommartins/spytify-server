import sys
from os import system
from queue import Empty
from time import sleep


def Loading():

    for i in range(21):
        sys.stdout.write('\r')
        # the exact output you're looking for:
        sys.stdout.write("[%-20s] %d%%" % ('='*i, 5*i))
        sys.stdout.flush()
        sleep(0.25) # [=======] [######]


def Progress(pipe): # Installation and repairment process animation handler 

    system('setterm -cursor off')

    while True:
        for char in ['|', '/', '-', '\\']:
            print("Setting up ", char, end='\r')
            sleep(0.12)

            try:
                if pipe.get(False):
                    raise SystemExit

            except Empty:
                pass

    system('setterm -cursor on')