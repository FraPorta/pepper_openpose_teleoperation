# -*- encoding: UTF-8 -*-

import datetime
import qi
from naoqi import ALProxy
import argparse
import sys
import time
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import os
from Queue import Queue
from datetime import datetime
# local imports
from keypoints_to_angles import KeypointsToAngles 
from sensory_hub import DetectUserDepth, Person
from approach_user import ApproachUser

## class PepperApproachControl
#
# This class makes Pepper approach a User and then it will be teleoperated by an operator using 3d keypoints
class PepperApproachControl():
    
    # Class initialization: connect to Pepper robot
    def __init__(self, show_plot, approach_requested, approach_only, ip, port):
        
        self.LShoulderPitch = self.LShoulderRoll = self.LElbowYaw = self.LElbowRoll = self.RShoulderPitch = self.RShoulderRoll = self.RElbowYaw = self.RElbowRoll = self.HipPitch = None
        
        self.show_plot = show_plot
        self.approach_requested = approach_requested
        self.approach_only = approach_only
        self.ip_addr = ip 
        self.port = port
        self.time_elapsed = 0.0
        self.loop_interrupted = False

    def run(self):
        # Init NAOqi session
        session = qi.Session()
        
        # Try to connect to the robot
        try:
            session.connect("tcp://" + self.ip_addr + ":" + str(self.port))
        except RuntimeError:
            print ("Can't connect to Naoqi at ip \"" + self.ip_addr + "\" on port " + str(self.port) +".\n"
                "Please check your script arguments. Run with -h option for help.")
            sys.exit(1)
            
        # Try to approach the user (repeat until a user is approached)
        if approach_requested or approach_only:
            while not self.approach_user(session):
                time.sleep(1)
        
        # Start receiving keypoints and controlling Pepper joints
        if not approach_only:
            print("Waiting for keypoints...")
            self.joints_control(session)
    
    ##  function saturate_angles
    #
    #   Saturate angles before using them for controlling Pepper joints
    def saturate_angles(self, mProxy, LSP, LSR, LEY, LER, RSP, RSR, REY, RER, HP):
        # global LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, HipPitch
        # limit percentage for some angles 
        limit = 1.0
        
        ## LEFT ##
        # LShoulderPitch saturation
        if LSP is None:
            # LShoulderPitch = mProxy.getData("Device/SubDeviceList/LShoulderPitch/Position/Actuator/Value")
            self.LShoulderPitch = mProxy.getData("Device/SubDeviceList/LShoulderPitch/Position/Sensor/Value")
        elif LSP < -2.0857:
            self.LShoulderPitch = -2.0857
        elif LSP > 2.0857:
            self.LShoulderPitch = 2.0857
        
        # LShoulderRoll saturation
        if LSR is None:
            # LShoulderRoll = mProxy.getData("Device/SubDeviceList/LShoulderRoll/Position/Actuator/Value")
            self.LShoulderRoll = mProxy.getData("Device/SubDeviceList/LShoulderRoll/Position/Sensor/Value")
        elif LSR < 0.0087:
            self.LShoulderRoll = 0.0087
        elif LSR > 1.5620:
            self.LShoulderRoll = 1.5620
            
        # LElbowYaw saturation
        if LEY is None:
            # LElbowYaw = mProxy.getData("Device/SubDeviceList/LElbowYaw/Position/Actuator/Value")
            self.LElbowYaw = mProxy.getData("Device/SubDeviceList/LElbowYaw/Position/Sensor/Value")
        elif LEY < -2.0857*limit:
            self.LElbowYaw = -2.0857*limit
        elif LEY > 2.0857*limit:
            self.LElbowYaw = 2.0857*limit

        # LElbowRoll saturation
        if LER is None:
            # LElbowRoll = mProxy.getData("Device/SubDeviceList/LElbowRoll/Position/Actuator/Value")
            self.LElbowRoll = mProxy.getData("Device/SubDeviceList/LElbowRoll/Position/Sensor/Value")
        elif LER < -1.5620:
            self.LElbowRoll = -1.5620
        elif LER > -0.0087:
            self.LElbowRoll = -0.0087

        ## RIGHT ##
        # RShoulderPitch saturation
        if RSP is None:
            # RShoulderPitch = mProxy.getData("Device/SubDeviceList/RShoulderPitch/Position/Actuator/Value")
            self.RShoulderPitch = mProxy.getData("Device/SubDeviceList/RShoulderPitch/Position/Sensor/Value")
        elif RSP < -2.0857:
            self.RShoulderPitch = -2.0857
        elif RSP > 2.0857:
            self.RShoulderPitch = 2.0857
        
        # RShoulderRoll saturation
        if RSR is None:
            # RShoulderRoll = mProxy.getData("Device/SubDeviceList/RShoulderRoll/Position/Actuator/Value")
            self.RShoulderRoll = mProxy.getData("Device/SubDeviceList/RShoulderRoll/Position/Sensor/Value")
        elif RSR < -1.5620 :
            self.RShoulderRoll = -1.5620
        elif RSR > -0.0087:
            self.RShoulderRoll = -0.0087
            
        # RElbowYaw saturation
        if REY is None:
            # RElbowYaw = mProxy.getData("Device/SubDeviceList/RElbowYaw/Position/Actuator/Value")
            self.RElbowYaw = mProxy.getData("Device/SubDeviceList/RElbowYaw/Position/Sensor/Value")
        elif REY < -2.0857*limit:
            self.RElbowYaw = -2.0857*limit
        elif REY > 2.0857*limit:
            self.RElbowYaw = 2.0857*limit

        # RElbowRoll saturation
        if RER is None:
            # RElbowRoll = mProxy.getData("Device/SubDeviceList/RElbowRoll/Position/Actuator/Value")
            self.RElbowRoll = mProxy.getData("Device/SubDeviceList/RElbowRoll/Position/Sensor/Value")
        elif RER < 0.0087:
            self.RElbowRoll = 0.0087
        elif RER > 1.5620:
            self.RElbowRoll = 1.5620

        # HipPitch saturation: -1.0385 to 1.0385
        if HP is None:
            # HipPitch = mProxy.getData("Device/SubDeviceList/HipPitch/Position/Actuator/Value")
            self.HipPitch = mProxy.getData("Device/SubDeviceList/HipPitch/Position/Sensor/Value")
            # print("RER")
        elif HP < -1.0385:
            self.HipPitch = -1.0385
        elif HP > 1.0385:
            self.HipPitch = 1.0385
        
    ##  function plot_data
    #
    #   Plot raw and filtered angles at the end of the session
    def plot_data(self, axs, raw_data, filt_data, robot_data, name, time_elapsed, pos_x, pos_y, plot_PS=False):
        # Plot time signals (Raw and filtered)
        data = np.array(raw_data)
        N_samples = len(data)
        sampling_rate = N_samples/time_elapsed
        time_samples = np.arange(0, time_elapsed, 1/sampling_rate)
        
        if len(raw_data) > len(filt_data):
            filt_data.append(0.0)
        data_filt = np.array(filt_data)
        
        if len(raw_data) > len(robot_data):
            robot_data.append(0.0)
        data_robot = np.array(robot_data)
        
        '''
        if plot_PS:
            # POWER SPECTRUM
            fourier_transform = np.fft.rfft(data)
            abs_fourier_transform = np.abs(fourier_transform)
            power_spectrum = np.square(abs_fourier_transform)
            frequency = np.linspace(0, sampling_rate/2, len(power_spectrum))
            if len(frequency) == len(power_spectrum):
                axs[0].plot(frequency, power_spectrum)
                axs[0].set(xlabel='frequency [1/s]', ylabel='power')
                axs[0].set_title('Power Spectrum')
        '''
        
        if len(time_samples) == len(data):
            axs[pos_x, pos_y].plot(time_samples, data)
            axs[pos_x, pos_y].set(xlabel='time [s]', ylabel='Angle [rad]')
            axs[pos_x, pos_y].set_title('%s angle' % name)
            
        if len(time_samples) == len(data_filt):
            axs[pos_x, pos_y].plot(time_samples, data_filt)
            # axs[pos_x, pos_y].legend(['signal', 'filtered'])
        
        if len(time_samples) == len(data_robot):
            axs[pos_x, pos_y].plot(time_samples, data_robot)
            axs[pos_x, pos_y].legend(['signal', 'filtered', 'robot'])

    ##  function save_data
    #
    #   save raw and filtered angles at the end of the session
    def save_data(self, raw_data, filt_data, robot_data, name, time_elapsed, path):
        # Plot time signals (Raw and filtered)
        data = raw_data
        N_samples = len(data)
        sampling_rate = N_samples/time_elapsed
        time_samples = np.arange(0, time_elapsed, 1/sampling_rate)
        
        if len(raw_data) > len(filt_data):
            filt_data.append(0.0)
        data_filt = filt_data
        
        if len(raw_data) > len(robot_data):
            robot_data.append(0.0)
        data_robot = robot_data
        
        out = np.array([data, data_filt, data_robot, time_samples])
        
        np.savetxt(path + "/" + name + "_data.csv", 
                   out,
                   delimiter =", ", 
                   fmt ='% s')
        
        
    ##  function joints_control
    #
    #   This function uses the setAngles and setStiffnesses methods
    #   in order to perform reactive control on Pepper upper body.
    #   The joints angles are filtered in real-time using a Butterworth filter
    def joints_control(self, session):
        
        self.loop_interrupted = False
        
        # Get the services ALMotion and ALRobotPosture
        motion_service  = session.service("ALMotion")
        posture_service = session.service("ALRobotPosture")

        # Get the service ALMemory
        memProxy = session.service("ALMemory")
        
        # Wake up robot
        motion_service.wakeUp()

        # Send robot to Stand Init
        posture_service.goToPosture("StandInit", 0.5)

        # Set stiffness of the interested joints
        stiffness = 1
        motion_service.setStiffnesses("LShoulderPitch", stiffness)
        motion_service.setStiffnesses("LShoulderRoll",  stiffness)

        motion_service.setStiffnesses("LElbowYaw", stiffness)
        motion_service.setStiffnesses("LElbowRoll", stiffness)

        motion_service.setStiffnesses("RShoulderPitch", stiffness)
        motion_service.setStiffnesses("RShoulderRoll", stiffness)

        motion_service.setStiffnesses("RElbowYaw", stiffness)
        motion_service.setStiffnesses("RElbowRoll", stiffness)

        motion_service.setStiffnesses("HipPitch", stiffness)
        
        # Disable external collision protection
        # motion_service.setExternalCollisionProtectionEnabled("Arms", False)
        
        # Initialize class KeypointsToAngles
        KtA = KeypointsToAngles()

        # Filter parameters 
        fs = 5.3            # sample rate, Hz
        cutoff = 0.7        # desired cutoff frequency of the filter, Hz 
        nyq = 0.5 * fs      # Nyquist Frequency
        order = 1           # filter order
        normal_cutoff = cutoff / nyq    # Cutoff freq for lowpass filter

        # Filter poles
        b, a = signal.butter(order, normal_cutoff, btype='low', analog=False, output='ba') 

        # Initialize filters for each angle
        z_LSP = signal.lfilter_zi(b, a)   
        z_LSR = signal.lfilter_zi(b, a)   
        z_LEY = signal.lfilter_zi(b, a)   
        z_LER = signal.lfilter_zi(b, a)  

        z_RSP = signal.lfilter_zi(b, a)   
        z_RSR = signal.lfilter_zi(b, a)   
        z_REY = signal.lfilter_zi(b, a)   
        z_RER = signal.lfilter_zi(b, a)  
        
        # Hip filter initialization
        # Continuous (Head and Pitch)
        cutoff = 0.3    # desired cutoff frequency of the filter, Hz 
        order = 2       # filter order
        b_HP, a_HP = signal.butter(order, cutoff/nyq, btype='low', analog=False, output='ba') 
        z_HP = signal.lfilter_zi(b_HP, a_HP)   
        
        # Initialize arrays to store angles for plots
        # Left arm
        LSP_arr = []
        LSP_arr_filt = []
        LSP_arr_robot = []
        LSR_arr = []
        LSR_arr_filt = []
        LSR_arr_robot = []
        LEY_arr = []
        LEY_arr_filt = []
        LEY_arr_robot = []
        LER_arr = []
        LER_arr_filt = []
        LER_arr_robot = []
        
        # Right arm
        RSP_arr = []
        RSP_arr_filt= []
        RSP_arr_robot = []
        RSR_arr = []
        RSR_arr_filt = []
        RSR_arr_robot = []
        REY_arr = []
        REY_arr_filt = []
        REY_arr_robot = []
        RER_arr = []
        RER_arr_filt = []
        RER_arr_robot = []
        
        # Hip
        HP_arr = []
        HP_arr_filt = []
        HP_arr_robot = []
        
        # Initialize time counter
        t1 = time.time()
        self.time_elapsed = 0.0
        
        # All joints
        names = ["LShoulderPitch","LShoulderRoll", "LElbowYaw", "LElbowRoll", \
                 "RShoulderPitch","RShoulderRoll", "RElbowYaw", "RElbowRoll", \
                 "HipPitch"]
        
        # Speed limits for the joints
        fractionMaxSpeed = 0.15

        print("Start controlling Pepper joints!")
        
        # Start loop to receive angles and control Pepper joints
        while KtA.start_flag and not self.loop_interrupted:
            try:
                # Get angles from keypoints
                self.LShoulderPitch, self.LShoulderRoll, self.LElbowYaw, self.LElbowRoll,\
                self.RShoulderPitch, self.RShoulderRoll, self.RElbowYaw, self.RElbowRoll,\
                self.HipPitch = KtA.get_angles()

                # Saturate angles to avoid exceding Pepper limits
                self.saturate_angles(memProxy,\
                                     self.LShoulderPitch, self.LShoulderRoll, self.LElbowYaw, self.LElbowRoll,\
                                     self.RShoulderPitch, self.RShoulderRoll, self.RElbowYaw, self.RElbowRoll,\
                                     self.HipPitch)
                
                # Store raw angles lists for plots
                if self.show_plot and self.time_elapsed > 2.0:
                    LSP_arr.append(self.LShoulderPitch)
                    LSR_arr.append(self.LShoulderRoll)
                    LEY_arr.append(self.LElbowYaw)
                    LER_arr.append(self.LElbowRoll)

                    RSP_arr.append(self.RShoulderPitch)
                    RSR_arr.append(self.RShoulderRoll)
                    REY_arr.append(self.RElbowYaw)
                    RER_arr.append(self.RElbowRoll)

                    HP_arr.append(self.HipPitch)
                
                ### REAL-TIME DATA FILTERING ###
                # Filter data with Butterworth filter
                self.LShoulderPitch, z_LSP = signal.lfilter(b, a, [self.LShoulderPitch], zi=z_LSP )
                self.LShoulderRoll, z_LSR = signal.lfilter(b, a, [self.LShoulderRoll], zi=z_LSR)
                self.LElbowYaw, z_LEY = signal.lfilter(b, a, [self.LElbowYaw], zi=z_LEY)
                self.LElbowRoll, z_LER = signal.lfilter(b, a, [self.LElbowRoll], zi=z_LER)

                self.RShoulderPitch, z_RSP = signal.lfilter(b, a, [self.RShoulderPitch], zi=z_RSP)
                self.RShoulderRoll, z_RSR = signal.lfilter(b, a, [self.RShoulderRoll], zi=z_RSR)
                self.RElbowYaw, z_REY = signal.lfilter(b, a, [self.RElbowYaw], zi=z_REY)
                self.RElbowRoll, z_RER = signal.lfilter(b, a, [self.RElbowRoll], zi=z_RER)

                self.HipPitch, z_HP = signal.lfilter(b_HP, a_HP, [self.HipPitch], zi=z_HP)
                
                # Store filtered angles for plots
                if self.show_plot and self.time_elapsed > 2.0:
                    LSP_arr_filt.append(self.LShoulderPitch[0])
                    LSR_arr_filt.append(self.LShoulderRoll[0])
                    LEY_arr_filt.append(self.LElbowYaw[0])
                    LER_arr_filt.append(self.LElbowRoll[0])

                    RSP_arr_filt.append(self.RShoulderPitch[0])
                    RSR_arr_filt.append(self.RShoulderRoll[0])
                    REY_arr_filt.append(self.RElbowYaw[0])
                    RER_arr_filt.append(self.RElbowRoll[0])
                    
                    HP_arr_filt.append(self.HipPitch[0])
                
                ### Pepper joints control ###
                # Control angles list 
                angles = [float(self.LShoulderPitch), float(self.LShoulderRoll), float(self.LElbowYaw), float(self.LElbowRoll), \
                    float(self.RShoulderPitch), float(self.RShoulderRoll), float(self.RElbowYaw), float(self.RElbowRoll), float(self.HipPitch)]
                # print("After ",float(self.RElbowYaw)*180/np.pi, float(self.RElbowRoll)*180/np.pi)
                # print("Left ",float(self.LElbowYaw)*180/np.pi, float(self.LElbowRoll)*180/np.pi)
                ## Send control commands to the robot if 2 seconds have passed (Butterworth Filter initialization time) ##
                if self.time_elapsed > 2.0:
                    motion_service.setAngles(names, angles, fractionMaxSpeed)
                    
                    # Store robot angles lists for plots
                    if self.show_plot:
                        LSP_arr_robot.append(memProxy.getData("Device/SubDeviceList/LShoulderPitch/Position/Sensor/Value"))
                        LSR_arr_robot.append(memProxy.getData("Device/SubDeviceList/LShoulderRoll/Position/Sensor/Value"))
                        LEY_arr_robot.append(memProxy.getData("Device/SubDeviceList/LElbowYaw/Position/Sensor/Value"))
                        LER_arr_robot.append(memProxy.getData("Device/SubDeviceList/LElbowRoll/Position/Sensor/Value"))

                        RSP_arr_robot.append(memProxy.getData("Device/SubDeviceList/RShoulderPitch/Position/Sensor/Value"))
                        RSR_arr_robot.append(memProxy.getData("Device/SubDeviceList/RShoulderRoll/Position/Sensor/Value"))
                        REY_arr_robot.append(memProxy.getData("Device/SubDeviceList/RElbowYaw/Position/Sensor/Value"))
                        RER_arr_robot.append(memProxy.getData("Device/SubDeviceList/RElbowRoll/Position/Sensor/Value"))

                        HP_arr_robot.append(memProxy.getData("Device/SubDeviceList/HipPitch/Position/Sensor/Value"))
                
                # Update time elapsed
                self.time_elapsed = time.time() - t1
            
            # If the user stops the script with CTRL+C, interrupt loop
            except KeyboardInterrupt:
                self.loop_interrupted = True
                    
            # Catch other exceptions
            except Exception as e:
                print(e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print(exc_type, exc_tb.tb_lineno)
                # Stop loop
                KtA.stop_receiving()
                # sys.exit(-1)
                
        # show plots of the joints angles
        if self.show_plot:
            now = datetime.now()
            # dd/mm/YY H:M:S
            dt_string = now.strftime("%d_%m_%Y_%H-%M-%S")
            
            if not os.path.exists("angles_data"):
                os.mkdir("angles_data")
                
            path = "angles_data/" + dt_string
            try:
                os.mkdir(path)
                
                # Plot joint angles
                self.save_data(LSP_arr, LSP_arr_filt, LSP_arr_robot, 'LSP', self.time_elapsed, path)
                self.save_data(LSR_arr, LSR_arr_filt, LSR_arr_robot, 'LSR', self.time_elapsed, path)
                self.save_data(LEY_arr, LEY_arr_filt, LEY_arr_robot, 'LEY', self.time_elapsed, path)
                self.save_data(LER_arr, LER_arr_filt, LER_arr_robot, 'LER', self.time_elapsed, path)

                self.save_data(RSP_arr, RSP_arr_filt, RSP_arr_robot, 'RSP', self.time_elapsed, path)
                self.save_data(RSR_arr, RSR_arr_filt, RSR_arr_robot, 'RSR', self.time_elapsed, path)
                self.save_data(REY_arr, REY_arr_filt, REY_arr_robot, 'REY', self.time_elapsed, path)
                self.save_data(RER_arr, RER_arr_filt, RER_arr_robot, 'RER', self.time_elapsed, path)

                self.save_data(HP_arr,  HP_arr_filt,  HP_arr_robot,  'HP',  self.time_elapsed, path)
                
            except OSError:
                print ("Creation of the directory %s failed" % path)
                
            # Create figure with 12 subplots
            fig, axs = plt.subplots(3,3)
            fig.suptitle('Joints angles')

            # Plot joint angles
            self.plot_data(axs, LSP_arr, LSP_arr_filt, LSP_arr_robot, 'LSP', self.time_elapsed, pos_x=0, pos_y=0)
            self.plot_data(axs, LSR_arr, LSR_arr_filt, LSR_arr_robot, 'LSR', self.time_elapsed, pos_x=0, pos_y=1)
            self.plot_data(axs, LEY_arr, LEY_arr_filt, LEY_arr_robot, 'LEY', self.time_elapsed, pos_x=0, pos_y=2)
            self.plot_data(axs, LER_arr, LER_arr_filt, LER_arr_robot, 'LER', self.time_elapsed, pos_x=1, pos_y=0)

            self.plot_data(axs, RSP_arr, RSP_arr_filt, RSP_arr_robot, 'RSP', self.time_elapsed, pos_x=1, pos_y=1)
            self.plot_data(axs, RSR_arr, RSR_arr_filt, RSR_arr_robot, 'RSR', self.time_elapsed, pos_x=1, pos_y=2)
            self.plot_data(axs, REY_arr, REY_arr_filt, REY_arr_robot, 'REY', self.time_elapsed, pos_x=2, pos_y=0)
            self.plot_data(axs, RER_arr, RER_arr_filt, RER_arr_robot, 'RER', self.time_elapsed, pos_x=2, pos_y=1)

            self.plot_data(axs, HP_arr,  HP_arr_filt,  HP_arr_robot,  'HP',  self.time_elapsed, pos_x=2, pos_y=2)
            
            print("Showing angles plots, close to terminate the program.")
            plt.show()

        print("Program terminated cleanly!")
                
    ##  function approach_user
    #
    #   Pepper searches for a person and then approaches it        
    def approach_user(self, session):
        # Approach the user
        apar = ""
        cpar = "1"
        
        dud = DetectUserDepth(session, None, False)
        dud.start()
        
        au = ApproachUser(apar, cpar, session)
        au.run()

        dud.stop()
        
        return au.user_approached
    
# Main 
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="130.251.13.191",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    
    parser.add_argument("--show_plots", type=int, default=1,
                        help="Select 1 if you want to see the plots when you interrupt the script with the keyboard")
    parser.add_argument("--approach_user", type=int, default=0,
                        help="Select 1 if you want Pepper to search and approach a user in the room before teleoperation")
    parser.add_argument("--approach_only", type=int, default=0,
                        help="Select 1 if you want Pepper to only search and approach a user in the room without teleoperation")

    # Parse arguments
    args = parser.parse_args()
    show_plot = bool(args.show_plots)
    approach_requested = bool(args.approach_user)
    approach_only = bool(args.approach_only)
    ip_addr = args.ip 
    port = args.port
    
    pac = PepperApproachControl(show_plot, approach_requested, approach_only, ip_addr, port)
    pac.run()
    
