import zmq
import time
import json
import socket
import sys

class SocketReceive:
    ctx = None
    sock = None

    ## method init
    # 
    # class initialization 
    def __init__(self):
        # initialize socket
        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(zmq.SUB)

        # Get local ip address
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname) 

        # try socket connect
        try: 
            self.sock.connect("tcp://%s:1234" % local_ip)
            self.sock.subscribe('') # subscribe to every topic sent by the publisher

        except Exception as e:
            print(e)
            sys.exit(-1)
    
    def __del__(self):
        self.sock.close()
        self.ctx.destroy()
    
    ## method receive_keypoints
    #
    # start receiving 3D keypoints dict
    def receive_keypoints(self):
        try:
            json_msg = self.sock.recv()
            # json_msg = sock.recv_string()
            wp_dict = json.loads(json_msg)
            return wp_dict
        except Exception as e:
            print(e)
            sys.exit(-1)

    ## method close
    # 
    # close socket
    def close(self):
        self.sock.close()
        self.ctx.term()


class SocketReceiveSignal:
    ctx = None
    sock = None

    ## method init
    # 
    # class initialization 
    def __init__(self):
        # initialize socket
        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(zmq.REP)

        # Get local ip address
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname) 

        # try socket connect
        try: 
            self.sock.connect("tcp://%s:1235" % local_ip)
            # self.sock.subscribe('') # subscribe to every topic sent by the publisher

        except Exception as e:
            print(e)
            sys.exit(-1)
    
    def __del__(self):
        self.sock.close()
        self.ctx.destroy()
    
    ## method receive_keypoints
    #
    # receive signal 
    def receive(self): 
        try:
            # msg: Start
            #      Stop
            msg = self.sock.recv(flags=zmq.NOBLOCK)
            print(str(msg))
            # A message has been received
            self.sock.send_string('Received ' + str(msg))
            if msg:
                return msg
            else:
                return None

        except zmq.Again as e:
            return None
            
            

    ## method close
    # 
    # close socket
    def close(self):
        self.sock.close()
        self.ctx.term()