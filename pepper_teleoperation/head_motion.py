# -*- encoding: UTF-8 -*-

"""Use getTransform Method to get the yaw and pitch to control the head to point the arm end-effector"""

import qi
import argparse
import sys
import motion
import time
import random

from scipy import signal
import numpy as np
from threading import Thread


class HeadMotionThread(Thread):
    def __init__(self, session, event_arm, event_stop):
        # Get the service ALMotion
        self.motion_service = session.service("ALMotion")
        self.life_service = session.service("ALAutonomousLife")
        
        self.is_running = True
        self.first_time = True
        self.e_arm = event_arm
        self.e_stop = event_stop
        
        # getTransform parameters
        self.name_arm         = 'RArm'
        self.name_head        = 'HeadPitch'
        self.frame            =  motion.FRAME_TORSO
        self.useSensorValues  =  False
        
        self.names = ["HeadYaw", "HeadPitch"]
        
        # filter init
        # Filter parameters 
        fs  = 15            # sample rate, Hz
        nyq = 0.5 * fs      # Nyquist Frequency
        
        cutoff        = 1            # desired cutoff frequency of the filter, Hz 
        order         = 1               # filter order
        normal_cutoff = cutoff / nyq    # Cutoff freq for lowpass filter

        # Filter poles
        self.b, self.a = signal.butter(order, normal_cutoff, btype='low', analog=False, output='ba') 

        # Initialize filters for each angle
        self.z_Y = signal.lfilter_zi(self.b, self.a)   
        self.z_P = signal.lfilter_zi(self.b, self.a)   
        
        # Call the Thread class's init function
        Thread.__init__(self)
        
        print("HeadMotionThread started")
    
    def run(self):
        
        # main loop
        while self.is_running:
            if self.e_arm.isSet():
                self.follow_arm()
            else:
                # print("Not tracking arm")
                self.e_arm.wait()
            if self.e_stop.isSet():
                self.is_running = False
        
        print("HeadMotionThread ended correctly")
            
    ## method follow_arm
    #
    # make the head follow the arm with the camera attached
    def follow_arm(self):
        if self.first_time:
            # self.disable_autonomous_movements()
            stiffness = 1
            self.motion_service.setStiffnesses("HeadYaw", stiffness)
            self.motion_service.setStiffnesses("HeadPitch", stiffness)
            
        self.first_time = False
        
        # t0 = time.time()
        
        # Get the end of the right arm and of the head 
        # as a transform represented in torso space. The result is a 4 by 4
        # matrix composed of a 3*3 rotation matrix and a column vector of positions.
        ta_T_list = self.motion_service.getTransform(self.name_arm,  self.frame, self.useSensorValues)
        th_T_list = self.motion_service.getTransform(self.name_head, self.frame, self.useSensorValues)
        
        # get matrices from list
        ta_T, ta_R, tO_a = self.get_matrices_from_list(ta_T_list)
        th_T, th_R, tO_h = self.get_matrices_from_list(ta_T_list)
        
        # invert transformation matrix
        ht_T = self.invert_transf_matrix(th_T_list)
        # at_T = self.invert_transf_matrix(ta_T_list)
        
        # multiply to get transformation matrix from head to arm
        # ha_T = np.matmul(at_T, th_T)
        ah_T = np.matmul(ht_T, ta_T)
        
        # Get yaw and pitch and saturate them
        # yaw, pitch = self.get_euler_angles(ha_T)
        yaw, pitch = self.get_euler_angles(ah_T)
        
        pitch = pitch - 0.174533*2 # 10 degrees * 2
        
        # print("Yaw: ", yaw * 180/np.pi)
        # print("Pitch: ", pitch * 180/np.pi)
        # print("Pitch: ", pitch * 180/np.pi)
        
        yaw, pitch = self.saturate_angles(yaw[0], pitch[0])
        
        ### REAL-TIME DATA FILTERING ###
        # Filter data with Butterworth filter
        yaw, self.z_Y = signal.lfilter(self.b, self.a, [yaw], zi=self.z_Y)
        pitch, self.z_P = signal.lfilter(self.b, self.a, [pitch], zi=self.z_P)
        
        # print("Yaw: ", yaw * 180/np.pi)
        # print("Pitch: ", pitch * 180/np.pi)
        
        self.motion_service.setAngles(self.names, [float(yaw), float(pitch)], 0.1)
        
        # t1 = time.time()
        
        # time_elapsed = t1 - t0
        
        # print("fs: ", 1/time_elapsed)

    ## method disable_autonomous_movements
    #
    #  Disable some Autonomous Life capabilities
    def disable_autonomous_movements(self):
        # BackgroundMovement	Defines which slight movements the robot does autonomously when its limbs are not moving.	ALBackgroundMovement
        # BasicAwareness	    Allows the robot to react to the environment to establish and keep eye contact with people.	ALBasicAwareness
        # ListeningMovement	    Enables some slight movements showing that the robot is listening.	ALListeningMovement
        # SpeakingMovement      Enables to start autonomously movements during the speech of the robot.	ALSpeakingMovement
        self.life_service.setAutonomousAbilityEnabled("BasicAwareness", False)
        self.life_service.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.life_service.setAutonomousAbilityEnabled("ListeningMovement", False)
        self.life_service.setAutonomousAbilityEnabled("SpeakingMovement", False)
    
    
    ## method get_matrices_from_list
    #
    #  arrange transformation matrix from list to numpy array.
    #  Also get rotation matrix and vector between the two frames  
    def get_matrices_from_list(self, T_list):
        # arrange transformation matrix into numpy array 
        T = np.array([[T_list[0],  T_list[1] , T_list[2] , T_list[3]],
                      [T_list[4],  T_list[5] , T_list[6] , T_list[7]],
                      [T_list[8],  T_list[9] , T_list[10], T_list[11]],
                      [T_list[12], T_list[13], T_list[14], T_list[15]]])
        
        R = np.array([[T_list[0],  T_list[1] , T_list[2]],
                      [T_list[4],  T_list[5] , T_list[6]],
                      [T_list[8],  T_list[9] , T_list[10]]])
        
        O = np.array([[T_list[3]],
                      [T_list[7]],
                      [T_list[11]]])
        
        return T, R, O
    
    ## method invert_transf_matrix
    #
    #  invert a transformation matrix in list form
    def invert_transf_matrix(self, T_list):
        """
        transpose a transformation matrix
        """
        T,R,O = self.get_matrices_from_list(T_list)
        
        # Invert matrix
        t_R = np.transpose(R)
        t_O = np.matmul(t_R, O)
        temp1 = np.concatenate((t_R, t_O), axis=1)
        temp2 = np.array([[0.,0.,0.,1.]])
        
        inv_T = np.concatenate((temp1, temp2))
        
        return inv_T

    ## method get_euler_angles
    #
    #  get yaw and pitch of the arm w.r.t the head frame 
    #  from the transformation matrix
    def get_euler_angles(self, T):
        d = T[:3, 3:4]
        x = d[0]
        y = d[1]
        z = d[2]
        pitch = np.arctan2(np.sqrt(x**2 + y**2), z)
        yaw   = np.arctan2(y, x)
        
        return yaw, pitch
    
    ## method saturate_angles
    #
    #  saturate the yaw and pitch angles to avoid out of range commands for the head
    def saturate_angles(self, yaw, pitch):
        # yaw angle must be from -2.0857 to 2.0857
        if yaw < -2.0857:
            y = -2.0857 
        elif yaw > 2.0857:
            y = 2.0857
        else:
            y = yaw
        
        # pitch angle must be from -0.7068 to 0.4451
        if pitch < -0.7068:
            p = -0.7068
        elif pitch > 0.4451:
            p = 0.4450
        else:
            p = pitch
        
        return y, p
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="130.251.13.131",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
        
    hm = HeadMotionThread(session)
    hm.is_running = True
    hm.run()
    
