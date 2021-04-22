import naoqi
import qi
import zmq
import json

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.bind("tcp://*:5555")

while True:
    #  Wait for next request from client
    message = socket.recv()
    print("Received request: %s" % message)

    
    #  Send reply back to client
    socket.send(b"World")

