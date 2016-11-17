from multiprocessing import Process
from queue import Queue

from Source.communication import Listener, Retrieve
from Source.output import Text


class Server(object):

    pipe = Queue()
    serverprocess = Process(target=Listener, args=(pipe,))

    def Start(self):

        if not self.serverprocess.is_alive():
            self.pipe = Queue()
            self.serverprocess = Process(target=Listener, args=(self.pipe,))
            self.serverprocess.start()
            print("Server is currently {0}on{1}.\n".format(Text.Green, Text.Close))

        elif self.serverprocess.is_alive():
            print("Error, the server is already {0}on{1}.\n".format(Text.Green, Text.Close))


    def Stop(self):

        if self.serverprocess.is_alive():
            connections = Retrieve(self.pipe, True)
            for PID in connections.values(): # Kill all server connections
                kill(int(PID), SIGKILL)

            self.serverprocess.terminate()
            print("Server is currently {0}off{1}.\n".format(Text.Red, Text.Close))