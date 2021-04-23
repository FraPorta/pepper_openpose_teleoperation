import zmq
import time
import json

class ZMQpull:
    ctx = None
    sock = None

    # Get local ip address
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname) 

    ## method init
    # 
    # class initialization 
    def __init__(self):
        # initialize socket
        ctx = zmq.Context()
        sock = ctx.socket(zmq.PULL)

        # try socket connect
        try: 
            sock.connect("tcp://%s:1234" % local_ip)
        except Exception as e:
            print(e)
            sys.exit(-1)
    
    ## method receive_keypoints
    #
    # start receiving 3D keypoints dict
    def receive_keypoints(self, msg_dict):
        json_msg = sock.recv()
        # json_msg = sock.recv_string()
        wp_dict = json.loads(json_msg)
        return wp_dict

    ## method close
    # 
    # close socket
    def close(self):
        sock.close()
        ctx.term()