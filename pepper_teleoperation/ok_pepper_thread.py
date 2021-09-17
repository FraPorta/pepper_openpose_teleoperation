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

            else:
                if self.is_running: 
                    time.sleep(0.5)   
                 
        print("OkPepper thread terminated correctly")
        
    ## method recognize
    #
    #  Record voice from microphone and recognize it using Google Speech Recognition
    def recognize(self):
        # print(self.list_working_microphones())
        with sr.Microphone(device_index=1) as source:  
            self.r.adjust_for_ambient_noise(source, duration=0.5)  # listen for 0.5 second to calibrate the energy threshold for ambient noise levels
            recognized_text = None
            try:
                # Receive audio from microphone
                self.audio = self.r.listen(source, timeout=1, phrase_time_limit=3)
                
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