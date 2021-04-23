import zmq
import time
import json

class SocketSend:
    ctx = None
    sock = None

    ## method init
    # 
    # class initialization 
    def __init__(self):
        # initialize socket
        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(zmq.PUB)

        # try socket bind
        try: 
            self.sock.bind("tcp://*:1234")
        except zmq.error.ZMQError as e:
            print(e)
            sys.exit(-1)
    
    ## method send
    #
    # convert dictionary to json and send it via tcp socket
    def send(self, msg_dict):
        msg_json = json.dumps(msg_dict)  
        self.sock.send_string(msg_json)

    ## method close
    # 
    # close socket
    def close(self):
        self.sock.close()
        self.ctx.term()