from queue import Empty


def Pipe(pipe, condition=False):

    try:
       output = pipe.get(condition)

    except Empty:
        return

    return output