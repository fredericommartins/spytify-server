from os import popen, system
from time import sleep

from Source.communication import Pipe


def Loading(pipe, libsize): # Database initial insertion animation

    system('setterm -cursor off')

    done = Pipe(pipe, True)

    while done:
        freescreen = int(popen('stty size', 'r').read().split()[1]) - 26 # Calculate free screen size for progression bar
        percentage = round(done/libsize*100)
        progression = round(percentage*freescreen/100)

        print("Building database: [{0:<{2}}] {1}%".format('='*progression, percentage, freescreen), end='\r')

        done = Pipe(pipe, True)

    system('setterm -cursor on')


def Progress(pipe): # Installation and repairment process animation

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