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

class SpeechThread(Thread):
    def __init__(self, session, q, q_rec, q_button):
        
        self.session = session
        self.text = None
        self.rec = False
        self.is_running = True
        self.q_text = q
        self.q_rec = q_rec
        
        self.q_button = q_button
        
        # Speech recognizer  
        self.r = sr.Recognizer()
        
        # Call the Thread class's init function
        Thread.__init__(self)
        print("SpeechThread started")
        # Get the service ALTextToSpeech.
        self.tts = self.session.service("ALTextToSpeech")
        self.motion = self.session.service("ALMotion")
    
    # Override the run() function of Thread class
    def run(self):
        # time to perform the movements
        t = 3
        # distance covered by every movement
        d = 0.4
        # angle of rotation
        angle = 0.261799*2
        
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
                    
                    # Voice commands to control Pepper position and the GUI
                    if txt == 'move forward' or txt == 'go forward':
                        x = d
                        y = 0.0
                        theta = 0.0
                        self.motion.moveTo(x, y, theta, t)
                        
                    elif txt == 'move backwards' or txt == 'go backwards' or\
                         txt == 'move backward' or txt == 'go backward' or\
                         txt == 'move back' or txt == 'go back':
                        x = -d
                        y = 0.0
                        theta = 0.0
                        self.motion.moveTo(x, y, theta, t)

                    elif txt == 'move right' or txt == 'go right' or\
                         txt == 'move to the right' or txt == 'go to the right':
                        x = 0.0
                        y = -d
                        theta = 0.0                         
                        self.motion.moveTo(x, y, theta, t)

                    elif txt == 'move left' or txt == 'go left' or\
                         txt == 'move to the left' or txt == 'go to the left':
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
                        
                    elif txt == 'stop talking':
                        self.q_button.put(txt)
                    
                    elif txt == 'start pepper' or txt == 'start robot' or txt == 'start moving':
                        self.q_button.put('start pepper')
                    
                    elif txt == 'stop pepper' or txt == 'stop robot' or txt == 'stop moving':
                        self.q_button.put('stop pepper') 
                    
                    elif txt == 'watch right' or txt == 'look right' or txt == 'luke wright' or txt == 'look to the right':
                        self.motion.setStiffnesses("HeadYaw", 1)
                        # self.motion.setStiffnesses("HeadPitch", 1)
                        names = ['HeadYaw']
                        angles = [-angle]
                        self.motion.setAngles(names, angles, 0.15)     
                    elif txt == 'watch left' or txt == 'look left' or txt == 'look to the left':
                        self.motion.setStiffnesses("HeadYaw", 1)
                        # self.motion.setStiffnesses("HeadPitch", 1)
                        names = ['HeadYaw']
                        angles = [angle]
                        self.motion.setAngles(names, angles, 0.15)   
                    elif txt == 'watch up' or txt == 'look up':
                        self.motion.setStiffnesses("HeadPitch", 1)
                        # self.motion.setStiffnesses("HeadPitch", 1)
                        names = ['HeadPitch']
                        angles = [-angle/2]
                        self.motion.setAngles(names, angles, 0.15)       
                    elif txt == 'watch down' or txt == 'look down':
                        self.motion.setStiffnesses("HeadPitch", 1)
                        # self.motion.setStiffnesses("HeadPitch", 1)
                        names = ['HeadPitch']
                        angles = [angle/2]
                        self.motion.setAngles(names, angles, 0.15)       
                    else:
                        # Repeat the recognized text
                        self.tts.say(self.text)
                        
                    # Put text in a queue for the GUI
                    self.q_text.put(self.text) 
            else:
                if self.is_running: 
                    time.sleep(0.5)
                     
        # self.q_text.put("Speech thread terminated correctly")            
        print("Speech thread terminated correctly")

        
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
                # print("Google Speech Recognition could not understand audio")
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
    
    
    '''
    # Override the run() function of Thread class
    def run(self):
        # mics = self.list_working_microphones()
        # print(mics)
        # if mics:
        while self.is_running:
            if not self.q_rec.empty():
                command = self.q_rec.get(block=False, timeout= None)
                if command == "Rec":
                    self.rec = True
                elif command == "StopRec":
                    self.rec = False
                elif command == "StopRun":
                    self.is_running = False
            
            if self.rec:
                self.text = self.recognize()
                if self.text is not None:
                    self.tts.say(self.text)
                    self.q.put(self.text)
            time.sleep(0.1)
            
        print("Speech thread terminated correctly")
        # else:
        #     print("No Working mics)
        
    
    def list_working_microphones(self):
        """
        Returns a dictionary mapping device indices to microphone names, for microphones that are currently hearing sounds. When using this function, ensure that your microphone is unmuted and make some noise at it to ensure it will be detected as working.
        Each key in the returned dictionary can be passed to the ``Microphone`` constructor to use that microphone. For example, if the return value is ``{3: "HDA Intel PCH: ALC3232 Analog (hw:1,0)"}``, you can do ``Microphone(device_index=3)`` to use that microphone.
        """
        pyaudio_module = sr.Microphone.get_pyaudio()
        audio = pyaudio_module.PyAudio()
        try:
            result = {}
            for device_index in range(audio.get_device_count()):
                device_info = audio.get_device_info_by_index(device_index)
                device_name = device_info.get("name")
                assert isinstance(device_info.get("defaultSampleRate"), (float, int)) and device_info["defaultSampleRate"] > 0, "Invalid device info returned from PyAudio: {}".format(device_info)
                try:
                    # read audio
                    pyaudio_stream = audio.open(
                        input_device_index=device_index, channels=1, format=pyaudio_module.paInt16,
                        rate=int(device_info["defaultSampleRate"]), input=True
                    )
                    try:
                        buffer = pyaudio_stream.read(1024)
                        if not pyaudio_stream.is_stopped(): pyaudio_stream.stop_stream()
                    finally:
                        pyaudio_stream.close()
                except Exception:
                    continue

                # compute RMS of debiased audio
                energy = -audioop.rms(buffer, 2)
                energy_bytes = chr(energy & 0xFF) + chr((energy >> 8) & 0xFF) if bytes is str else bytes([energy & 0xFF, (energy >> 8) & 0xFF])  # Python 2 compatibility
                debiased_energy = audioop.rms(audioop.add(buffer, energy_bytes * (len(buffer) // 2), 2), 2)

                if debiased_energy > 30:  # probably actually audio
                    result[device_index] = device_name
        finally:
            audio.terminate()
        return result
    '''
    