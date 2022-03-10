import zmq
import time
import json
import sys

## class SocketSendSignal
#
# This class creates a ZeroMQ socket to send data over TCP 
class SocketSendSignal:
    ## method init
    # 
    # class initialization 
    def __init__(self):
        # initialize socket
        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(zmq.REQ)

        # try socket bind
        try: 
            self.sock.bind("tcp://*:1235")
        except zmq.error.ZMQError as e:
            print(e)
            sys.exit(-1)
    
    ## method send
    #
    # convert dictionary to json and send it via tcp socket
    def send(self, msg):
        # msg = json.dumps(msg_dict)
        self.sock.send(msg)
        # Wait for reply
        msg_in = self.sock.recv()
        print(msg_in)

    ## method close
    # 
    # close socket
    def close(self):
        self.sock.close()
        self.ctx.term()