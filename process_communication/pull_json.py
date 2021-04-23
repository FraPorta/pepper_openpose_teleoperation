# import naoqi
# import qi
import zmq
import json
import time
import socket

# Get local ip address
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname) 

ctx = zmq.Context()
sock = ctx.socket(zmq.PULL)
sock.connect("tcp://%s:1234" % local_ip)

print("Starting receiver loop ...")
while True:
    json_msg = sock.recv()
    wp_dict = json.loads(json_msg)
    print(wp_dict.keys())
    print(wp_dict.values())


sock.close()
ctx.term()
