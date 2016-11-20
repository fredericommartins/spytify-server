from multiprocessing import Queue, Process

from Source.communication import Listener, Retrieve
from Source.properties import Text


class Server(object):

    pipe = Queue()
    listener = Process(target=Listener, args=(pipe,))

    def Start(self):

        if not self.listener.is_alive():
            self.pipe = Queue()
            self.listener = Process(target=Listener, args=(self.pipe,))
            self.listener.start()
            print("Server is currently {0}on{1}.".format(Text.Green, Text.Close))

        elif self.listener.is_alive():
            print("Error, the server is already {0}on{1}.".format(Text.Green, Text.Close))


    def Stop(self):

        if self.listener.is_alive():
            pool = Retrieve(self.pipe, True)
            for process in pool.values():
                process.shutdown()
                #kill(int(PID), SIGKILL)

            self.listener.terminate()
            print("Server is currently {0}off{1}.".format(Text.Red, Text.Close))

        elif not self.listener.is_alive():
            print("Error, the server is already {0}off{1}.".format(Text.Red, Text.Close))