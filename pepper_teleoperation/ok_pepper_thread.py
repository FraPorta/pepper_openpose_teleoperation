# -*- encoding: UTF-8 -*-

import qi
from naoqi import ALProxy
import argparse
import sys
import time
import numpy as np
import audioop

import speech_recognition as sr
from threading import Thread

class OkPepperThread(Thread):
    def __init__(self, q_button, q_stop):
        # self.session = session
        self.text = None
        self.rec = False
        self.is_running = True
        
        self.q_button = q_button
        self.q_stop = q_stop
        
        # Speech recognizer  
        self.r = sr.Recognizer()
        
        # Call the Thread class's init function
        Thread.__init__(self)
        
        print("OkPepperThread started")
    
    # Override the run() function of Thread class
    def run(self):
        while self.is_running:
            if not self.q_stop.empty():
                command = self.q_stop.get(block=False, timeout= None)
                if command == "Rec":
                    self.rec = True
                elif command == "StopRec":
                    print('Stopped recording OkPepper')
                    self.rec = False
                elif command == "StopRun":
                    self.rec = False
                    self.is_running = False
                    
            
            if self.rec:
                self.text = self.recognize()
                if self.text is not None:
                    # text to lower case
                    txt = self.text.lower()
                    print(txt)
                    
                    # Voice commands for the buttons
                    if txt == 'connect':
                        self.q_button.put(txt)
                    elif txt == 'start talking':
                        self.q_button.put(txt)
                    elif txt == 'start pepper' or txt == 'start robot' or txt == 'start moving':
                        self.q_button.put('start pepper')
                    elif txt == 'stop robot' or txt == 'stop pepper' or txt == 'stop moving':
                        self.q_button.put('stop pepper')
                        
                    # # Voice commands to control Pepper position
                    # elif txt == 'move forward' or txt == 'go forward':
                    #     x = d
                    #     y = 0.0
                    #     theta = 0.0
                    #     self.motion.moveTo(x, y, theta, t)
                        
                    # elif txt == 'move backwards' or txt == 'go backwards' or\
                    #      txt == 'move backward' or txt == 'go backward' or\
                    #      txt == 'move back' or txt == 'go back':
                    #     x = -d
                    #     y = 0.0
                    #     theta = 0.0
                    #     self.motion.moveTo(x, y, theta, t)

                    # elif txt == 'move right' or txt == 'go right' or\
                    #      txt == 'move to the right' or txt == 'go to the right':
                    #     x = 0.0
                    #     y = d
                    #     theta = 0.0                         
                    #     self.motion.moveTo(x, y, theta, t)

                    # elif txt == 'move left' or txt == 'go left' or\
                    #      txt == 'move to the left' or txt == 'go to the left':
                    #     x = 0.0
                    #     y = -d
                    #     theta = 0.0
                    #     self.motion.moveTo(x, y, theta, t)
                        
                    # elif txt == 'rotate left' or txt == 'turn left':
                    #     x = 0.0
                    #     y = 0.0
                    #     theta = angle    
                    #     self.motion.moveTo(x, y, theta, t)
                    
                    # elif txt == 'rotate right' or txt == 'turn right':
                    #     x = 0.0
                    #     y = 0.0
                    #     theta = -angle
                    #     self.motion.moveTo(x, y, theta, t)

            else:
                if self.is_running: 
                    time.sleep(0.5)   
                 
        print("OkPepper thread terminated correctly")
        
    ## method recognize
    #
    #  Record voice from microphone and recognize it using Google Speech Recognition
    def recognize(self):
        # print(self.list_working_microphones())
        with sr.Microphone() as source:  
            recognized_text = None
            try:
                # Receive audio from microphone
                self.audio = self.r.listen(source, timeout=None)

                # received audio data, recognize it using Google Speech Recognition
                recognized_text = self.r.recognize_google(self.audio, language="en-EN")
                
            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

        return recognized_text
        
        
# Main initialization
if __name__ == "__main__":
    
    opt = OkPepperThread()
    opt.start()
    
    opt.join()
    print('Thread finished cleanly')