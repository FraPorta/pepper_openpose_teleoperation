import zmq
import time
import json

class ZMQpush:
    ctx = None
    sock = None

    def __init__(self):

        ctx = zmq.Context()
        sock = ctx.socket(zmq.PUSH)

        try: 
            sock.bind("tcp://*:1234")
        except zmq.error.ZMQError as e:
            print(e)
            sock.close()
            sock.bind("tcp://*:1234")
