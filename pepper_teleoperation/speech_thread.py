# -*- encoding: UTF-8 -*-

import qi
from naoqi import ALProxy
import argparse
import sys
import time
import numpy as np
import audioop
import threading
import math

import speech_recognition as sr
from threading import Thread

from head_motion import HeadMotionThread

class SpeechThread(Thread):
    def __init__(self, session, q, q_rec, q_button):
        
        self.session = session
        self.text = None
        self.rec = False
        self.is_running = True
        self.q_text = q
        self.q_rec = q_rec
        
        self.q_button = q_button
        self.arm_tracking_event = threading.Event()
        self.stop_event = threading.Event()
        
        self.hmt = HeadMotionThread(self.session, self.arm_tracking_event, self.stop_event)
        self.hmt.start()
        
        # Speech recognizer  
        self.r = sr.Recognizer()
        
        # Call the Thread class's init function
        Thread.__init__(self)
        print("SpeechThread started")
        
        # Get the service ALTextToSpeech.
        self.tts = self.session.service("ALTextToSpeech")
        self.motion = self.session.service("ALMotion")
        self.life_service = self.session.service("ALAutonomousLife")
        self.blink_service = self.session.service("ALAutonomousBlinking")
    
    # Override the run() function of Thread class
    def run(self):
        # time to perform the movements
        t = 3
        # distance covered by every movement
        d = 0.5
        # angle of rotation 45 degrees
        angle = math.pi/4
        
        with sr.Microphone(device_index=1) as source:  
            self.r.adjust_for_ambient_noise(source, duration=1)  # listen for 1 second to calibrate the energy threshold for ambient noise levels
        
        # main loop
        while self.is_running:
            # check for signals from the GUI
            if not self.q_rec.empty():
                command = self.q_rec.get(block=False, timeout= None)
                if command == "Rec":
                    self.rec = True
                elif command == "StopRec":
                    self.rec = False
                elif command == "StopRun":
                    self.rec = False
                    self.is_running = False
                    
            # Voice recognition
            if self.rec:
                self.text = self.recognize()
                if self.text is not None:
                    # text to lower case
                    txt = self.text.lower()
                    
                    # # disable autonomous blinking if activated
                    # if self.blink_service.isEnabled():
                    #         self.blink_service.setEnabled(False)
                    try:      
                        # Voice commands to control Pepper position and the GUI
                        if txt == 'move forward' or txt == 'go forward' or txt == 'forward':
                            x = d
                            y = 0.0
                            theta = 0.0
                            self.motion.moveTo(x, y, theta, t)
                            
                        elif txt == 'move backwards' or txt == 'go backwards' or\
                            txt == 'move backward' or txt == 'go backward' or\
                            txt == 'move back' or txt == 'go back' or txt == 'back':
                            x = -d
                            y = 0.0
                            theta = 0.0
                            self.motion.moveTo(x, y, theta, t)

                        elif txt == 'move right' or txt == 'go right' or\
                            txt == 'move to the right' or txt == 'go to the right' or txt == 'right':
                            x = 0.0
                            y = -d
                            theta = 0.0                         
                            self.motion.moveTo(x, y, theta, t)

                        elif txt == 'move left' or txt == 'go left' or\
                            txt == 'move to the left' or txt == 'go to the left' or txt == 'left':
                            x = 0.0
                            y = d
                            theta = 0.0
                            self.motion.moveTo(x, y, theta, t)
                            
                        elif txt == 'rotate left' or txt == 'turn left':
                            x = 0.0
                            y = 0.0
                            
                            theta = angle    
                            self.motion.moveTo(x, y, theta, t)
                        
                        elif txt == 'rotate right' or txt == 'turn right':
                            x = 0.0
                            y = 0.0
                            theta = -angle
                            self.motion.moveTo(x, y, theta, t)
                        
                        elif txt == 'turn around':
                            x = 0.0
                            y = 0.0
                            theta = math.pi
                            self.motion.moveTo(x, y, theta, t)
                            
                        elif txt == 'stop talking':
                            self.q_button.put(txt)
                        
                        elif txt == 'start pepper' or txt == 'start robot' or txt == 'start moving':
                            self.q_button.put('start pepper')
                        
                        elif txt == 'stop pepper' or txt == 'stop robot' or txt == 'stop moving':
                            self.q_button.put('stop pepper') 
                        
                        elif txt == 'watch right' or txt == 'look right' or txt == 'luke wright' or txt == 'look to the right':
                            self.life_service.stopAll()
                            # self.life_service.setState('disabled')
                            # stop arm tracking
                            if self.arm_tracking_event.is_set():
                                self.arm_tracking_event.clear()
                            
                            # stop user tracking
                            if self.life_service.getAutonomousAbilityEnabled("BasicAwareness"):
                                self.life_service.setAutonomousAbilityEnabled("BasicAwareness", False)
                            # move head right
                            self.motion.setStiffnesses("HeadYaw", 1)
                            # self.motion.setStiffnesses("HeadPitch", 1)
                            names = ['HeadYaw']
                            angles = [-angle]
                            self.motion.setAngles(names, angles, 0.15)     
                        elif txt == 'watch left' or txt == 'look left' or txt == 'look to the left' or txt=="luke left":
                            self.life_service.stopAll()
                            # self.life_service.setState('disabled')
                            # stop arm tracking
                            if self.arm_tracking_event.is_set():
                                self.arm_tracking_event.clear()
                            # stop user tracking
                            if self.life_service.getAutonomousAbilityEnabled("BasicAwareness"):
                                self.life_service.setAutonomousAbilityEnabled("BasicAwareness", False)
                            # move head left
                            self.motion.setStiffnesses("HeadYaw", 1)
                            # self.motion.setStiffnesses("HeadPitch", 1)
                            names = ['HeadYaw']
                            angles = [angle]
                            self.motion.setAngles(names, angles, 0.15)   
                            
                        elif txt == 'watch up' or txt == 'look up' or txt == "luke up":
                            self.life_service.stopAll()
                            # self.life_service.setState('disabled')
                            # stop arm tracking
                            if self.arm_tracking_event.is_set():
                                self.arm_tracking_event.clear()
                            
                            # stop user tracking
                            if self.life_service.getAutonomousAbilityEnabled("BasicAwareness"):
                                self.life_service.setAutonomousAbilityEnabled("BasicAwareness", False)
                            # MOVE HEAD UP
                            self.motion.setStiffnesses("HeadPitch", 1)
                            # self.motion.setStiffnesses("HeadPitch", 1)
                            names = ['HeadPitch']
                            angles = [-angle/2]
                            self.motion.setAngles(names, angles, 0.15)    
                            
                        elif txt == 'watch down' or txt == 'look down' or txt == "luke down":
                            self.life_service.stopAll()
                            # self.life_service.setState('disabled')
                            # stop arm tracking
                            if self.arm_tracking_event.is_set():
                                self.arm_tracking_event.clear()
                            # stop user tracking
                            if self.life_service.getAutonomousAbilityEnabled("BasicAwareness"):
                                self.life_service.setAutonomousAbilityEnabled("BasicAwareness", False)
                            # move head down
                            self.motion.setStiffnesses("HeadPitch", 1)
                            # self.motion.setStiffnesses("HeadPitch", 1)
                            names = ['HeadPitch']
                            angles = [angle/2]
                            self.motion.setAngles(names, angles, 0.15)    
                        
                        elif txt == 'watch ahead' or txt == 'look ahead' or txt == "luke ahead" or txt == "look forward" or txt == "watch forward":
                            self.life_service.stopAll()
                            # self.life_service.setState('disabled')
                            # stop arm tracking
                            if self.arm_tracking_event.is_set():
                                self.arm_tracking_event.clear()
                            # stop user tracking
                            if self.life_service.getAutonomousAbilityEnabled("BasicAwareness"):
                                self.life_service.setAutonomousAbilityEnabled("BasicAwareness", False)
                                
                            # move head down
                            self.motion.setStiffnesses("HeadPitch", 1)
                            self.motion.setStiffnesses("HeadYaw", 1)
                            names = ['HeadYaw', 'HeadPitch']
                            angles = [0, 0]
                            self.motion.setAngles(names, angles, 0.15)    
                            
                        elif txt =="track arm" or txt == "follow arm" or txt=="truck arm" or txt == "truck art"  or txt == "track art" or txt == "hollow armor" or txt=="hollow arm":
                            self.text = "follow arm"
                            self.life_service.stopAll()
                            # self.life_service.setState('disabled')
                            if self.life_service.getAutonomousAbilityEnabled("BasicAwareness"):
                                self.life_service.setAutonomousAbilityEnabled("BasicAwareness", False)
                            if not self.arm_tracking_event.is_set():
                                self.arm_tracking_event.set()
                            
                        elif txt =="stop tracking" or txt == "stop following" or txt == "stop arm tracking" or txt == "stop arm following":
                            if self.arm_tracking_event.is_set():
                                self.arm_tracking_event.clear()
                            
                        elif txt =="track user" or txt == "truck user":
                            if self.arm_tracking_event.is_set():
                                self.arm_tracking_event.clear()
                            self.life_service.setAutonomousAbilityEnabled("BasicAwareness", True)
                            
                        elif txt == 'stop focus':
                            self.life_service.stopAll()
                        else:
                            if self.session.isConnected():
                                # Repeat the recognized text
                                self.tts.say(self.text)
                            
                        # Put text in a queue for the GUI
                        self.q_text.put(self.text) 
                    except RuntimeError as e:
                        print(e)
                        print("Error:", self.text)
            else:
                if self.is_running: 
                    time.sleep(0.5)
                    
        # stop arm tracking thread
        self.arm_tracking_event.set()
        self.stop_event.set()     
        self.hmt.join()
          
        # self.q_text.put("Speech thread terminated correctly")            
        print("Speech thread terminated correctly")

        
    ## method recognize
    #
    #  Record voice from microphone and recognize it using Google Speech Recognition
    def recognize(self):
        
        with sr.Microphone(device_index=1) as source:  
            # print(source.list_working_microphones())
            # print(source.list_microphone_names())
            # print(source.device_index)
            # self.r.adjust_for_ambient_noise(source, duration=0.5)  # listen for 1 second to calibrate the energy threshold for ambient noise levels
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="130.251.13.113",
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
    