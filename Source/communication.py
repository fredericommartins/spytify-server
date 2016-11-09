from queue import Empty


def Retrieve(pipe, condition=False): # Queue exception handler

    try:
       output = pipe.get(condition)

    except Empty:
        return

    return output