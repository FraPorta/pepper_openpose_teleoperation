import numpy as np
import cv2
import time
import threading
from threading import Thread, ThreadError

# Stream Ip camera
class Cam():

    def __init__(self, url):
    
        self.stream = stream = cv2.VideoCapture(url)

        self.thread_cancelled = False
        self.thread = Thread(target=self.run)
        print("Camera initialised")

    def start(self):
        self.thread.start()
        print("Camera stream started")
    
    def run(self):
        bytes=''
        while not self.thread_cancelled:
            try:
                r, f = self.stream.read()
                cv2.imshow('IP Camera stream',f)

                if cv2.waitKey(1) == 27:
                    exit(0)
            except ThreadError:
                self.thread_cancelled = True
        
        
    def is_running(self):
        return self.thread.isAlive()
      
    
    def shut_down(self):
        self.thread_cancelled = True
        #block while waiting for thread to terminate
        while self.thread.isAlive():
            time.sleep(1)
        return True

  
    
if __name__ == "__main__":
    url = 'rtsp://laboratorium:cam159753@130.251.13.106:6554/stream_0'
    cam = Cam(url)
    cam.start()