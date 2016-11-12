from cmd import Cmd

from Source.output import Help, Welcome


class Console(Cmd):
    
    prompt = 'spytify# '
    file = None

    #def do_help(self, arg):

    #    Help()


    def do_exit(self, arg):

        raise SystemExit


    def do_server(self, arg):
        'Some help message'

        print(test)