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
    def __init__(self, q_button):
        # self.session = session
        self.text = None
        self.rec = False
        self.is_running = True
        
        self.q_button = q_button
        
        # Speech recognizer  
        self.r = sr.Recognizer()
        
        # Call the Thread class's init function
        Thread.__init__(self)
    
    # Override the run() function of Thread class
    def run(self):
        while self.is_running:
            # if not self.q_rec.empty():
            #     command = self.q_rec.get(block=False, timeout= None)
            #     if command == "Rec":
            #         self.rec = True
            #     elif command == "StopRec":
            #         self.rec = False
            #     elif command == "StopRun":
            #         self.is_running = False
            
            
            self.text = self.recognize()
            if self.text is not None:
                # text to lower case
                txt = self.text.lower()
                print(txt)
                
                if txt == 'connect':
                    self.q_button.put(txt)
                elif txt == 'start talking':
                    self.q_button.put(txt)
                elif txt == 'start peppa':
                    self.q_button.put('start pepper')
                

                # notify the GUI that the keyword was recognized
                # self.q.put(self.text)
            
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
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

        return recognized_text
        
        
# Main initialization
if __name__ == "__main__":
    
    opt = OkPepperThread()
    opt.start()
    
    opt.join()
    print('Thread finished cleanly')