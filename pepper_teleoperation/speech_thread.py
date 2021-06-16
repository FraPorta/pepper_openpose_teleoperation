# -*- encoding: UTF-8 -*-

import qi
from naoqi import ALProxy
import argparse
import sys
import time
import numpy as np

import speech_recognition as sr
from threading import Thread

class SpeechThread(Thread):
    def __init__(self, session, q):
        
        self.session = session
        self.text = None
        self.rec = False
        self.is_running = True
        self.q = q
        
        # Speech recognizer  
        self.r = sr.Recognizer()
        
        # Call the Thread class's init function
        Thread.__init__(self)

        # Get the service ALTextToSpeech.
        self.tts = self.session.service("ALTextToSpeech")
    
    # Override the run() function of Thread class
    def run(self):
        while self.is_running:
            if self.rec:
                self.text = self.recognize()
                print(self.text)
                if self.text is not None:
                    self.tts.say(self.text)
                    self.q.put(self.text)
                # self.rec = False
                
            time.sleep(0.1)
            
        print("Thread ended correctly")

    ## method recognize
    #
    #  Record voice from microphone and recognize it using Google Speech Recognition
    def recognize(self):
        with sr.Microphone() as source:  
            recognized_text = None
            print("Say something! Pepper will repeat it")
            
            try:
                # Receive audio from microphone
                self.audio = self.r.listen(source, timeout=1)
            
                # received audio data, recognize it using Google Speech Recognition
                recognized_text = self.r.recognize_google(self.audio)
                
            except sr.WaitTimeoutError:
                print("Mic timeout passed")
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

        return recognized_text
        
        
# Main initialization
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="130.251.13.134",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    

    # Parse arguments
    args = parser.parse_args()
    ip_addr = args.ip 
    port = args.port
    session = qi.Session()
    
    # Try to connect to the robot
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
            "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
      
    st = SpeechThread(session)
    st.start()
    
    st.join()