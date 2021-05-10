#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Use setAngles and setStiffnesses Methods"""

import qi
from naoqi import ALProxy
import argparse
import sys
import time
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt


from keypoints_to_angles import KeypointsToAngles 

LShoulderPitch = LShoulderRoll = LElbowYaw = LElbowRoll = RShoulderPitch = RShoulderRoll = RElbowYaw = RElbowRoll = None
session = None

## function saturate_angles
#
# Saturate angles before using them for controlling Pepper joints
def saturate_angles(mProxy, LSP, LSR, LEY, LER, RSP, RSR, REY, RER, HP):
    global LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, HipPitch

    ## LEFT ##
    
    # LShoulderPitch saturation
    if LSP is None:
        LShoulderPitch = mProxy.getData("Device/SubDeviceList/LShoulderPitch/Position/Actuator/Value")
        # print("LSP")
    elif LSP < -2.0857:
        LShoulderPitch = -2.0857
    elif LSP > 2.0857:
        LShoulderPitch = 2.0857
    
    # LShoulderRoll saturation
    if LSR is None:
        LShoulderRoll = mProxy.getData("Device/SubDeviceList/LShoulderRoll/Position/Actuator/Value")
        # print("LSR")
    elif LSR < 0.0087:
        LShoulderRoll = 0.0087
    elif LSR > 1.5620:
        LShoulderRoll = 1.5620
        
    # LElbowYaw saturation
    if LEY is None:
        LElbowYaw = mProxy.getData("Device/SubDeviceList/LElbowYaw/Position/Actuator/Value")
        # print("LEY")
    elif LEY < -2.0857:
        LElbowYaw = -2.0857
    elif LEY > 2.0857:
        LElbowYaw = 2.0857

    # LElbowRoll saturation
    if LER is None:
        LElbowRoll = mProxy.getData("Device/SubDeviceList/LElbowRoll/Position/Actuator/Value")
        # print("LER")
    elif LER < -1.5620:
        LElbowRoll = -1.5620
    elif LER > -0.0087:
        LElbowRoll = -0.0087


    ## RIGHT ##

    # RShoulderPitch saturation
    if RSP is None:
        RShoulderPitch = mProxy.getData("Device/SubDeviceList/RShoulderPitch/Position/Actuator/Value")
        # print("RSP")
    elif RSP < -2.0857:
        RShoulderPitch = -2.0857
    elif RSP > 2.0857:
        RShoulderPitch = 2.0857
    
    # RShoulderRoll saturation
    if RSR is None:
        RShoulderRoll = mProxy.getData("Device/SubDeviceList/RShoulderRoll/Position/Actuator/Value")
        # print("RSR")
    elif RSR < -1.5620 :
        RShoulderRoll = -1.5620
    elif RSR > -0.0087:
        RShoulderRoll = -0.0087
        
    # RElbowYaw saturation
    if REY is None:
        RElbowYaw = mProxy.getData("Device/SubDeviceList/RElbowYaw/Position/Actuator/Value")
        # print("REY")
    elif REY < -2.0857:
        RElbowYaw = -2.0857
    elif REY > 2.0857:
        RElbowYaw = 2.0857

    # RElbowRoll saturation
    if RER is None:
        RElbowRoll = mProxy.getData("Device/SubDeviceList/RElbowRoll/Position/Actuator/Value")
        # print("RER")
    elif RER < 0.0087:
        RElbowRoll = 0.0087
    elif RER > 1.5620:
        RElbowRoll = 1.5620

    # HipPitch saturation: -1.0385 to 1.0385
    if HP is None:
        HipPitch = mProxy.getData("Device/SubDeviceList/HipPitch/Position/Actuator/Value")
        # print("RER")
    elif HP < -1.0385:
        HipPitch = -1.0385
    elif HP > 1.0385:
        HipPitch = 1.0385

    
def update_arr(arr, angle, window_length):

    # Temporary array to save data
    temp = np.zeros(window_length + 1)

    # Update last 6 values array
    for i in range(0,window_length-1):
        temp[i] = arr[i+1]
        
    temp[window_length] = angle

    arr = temp.copy()

    return arr


    
def main(session):
    """
    This example uses the setAngles and setStiffnesses methods
    in order to simulate reactive control.
    """

    global LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, HipPitch

    # Get the services ALMotion and ALRobotPosture
    motion_service  = session.service("ALMotion")
    posture_service = session.service("ALRobotPosture")

    # Wake up robot
    motion_service.wakeUp()

    # Send robot to Stand Init
    posture_service.goToPosture("StandInit", 0.5)

    # create proxy on ALMemory
    memProxy = ALProxy("ALMemory","130.251.13.154", 9559)

    # Set stiffness of the interested joints
    stiffness = 0.5
    motion_service.setStiffnesses("LShoulderPitch", stiffness)
    motion_service.setStiffnesses("LShoulderRoll",  stiffness)

    motion_service.setStiffnesses("LElbowYaw", stiffness)
    motion_service.setStiffnesses("LElbowRoll", stiffness)

    motion_service.setStiffnesses("RShoulderPitch", stiffness)
    motion_service.setStiffnesses("RShoulderRoll", stiffness)

    motion_service.setStiffnesses("RElbowYaw", stiffness)
    motion_service.setStiffnesses("RElbowRoll", stiffness)

    motion_service.setStiffnesses("HipPitch", stiffness)

    # Wait some time
    time.sleep(2)
    
    # Initialize class KeypointsToAngles
    KtA = KeypointsToAngles()

    # Filter parameters 
    ## MOLTO BUONI
    # fs = 5.3        # sample rate, Hz
    # cutoff = 1.0    # desired cutoff frequency of the filter, Hz , slightly higher than actual 0.05, 0.1 Hz
    # nyq = 0.5 * fs  # Nyquist Frequency
    # order = 2       # filter order

    fs = 5.3        # sample rate, Hz
    cutoff = 0.8   # desired cutoff frequency of the filter, Hz , slightly higher than actual 0.5 Hz
    nyq = 0.5 * fs  # Nyquist Frequency
    order = 1      # filter order
    normal_cutoff = cutoff / nyq # Cutoff freq for lowpass filter

    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False, output='ba') 

    # # Plot the frequency response.
    # w, h = signal.freqz(b, a)
    # plt.subplot(2, 1, 1)
    # plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
    # plt.plot(cutoff, 0.5*np.sqrt(2), 'ko')
    # plt.axvline(cutoff, color='k')
    # plt.xlim(0, 0.5*fs)
    # plt.title("Lowpass Filter Frequency Response")
    # plt.xlabel('Frequency [Hz]')
    # plt.grid()
    # plt.show()

    # b = signal.firwin(order + 1, cutoff)

    z_LSP = signal.lfilter_zi(b, a)   
    z_LSR = signal.lfilter_zi(b, a)   
    z_LEY = signal.lfilter_zi(b, a)   
    z_LER = signal.lfilter_zi(b, a)  

    z_RSP = signal.lfilter_zi(b, a)   
    z_RSR = signal.lfilter_zi(b, a)   
    z_REY = signal.lfilter_zi(b, a)   
    z_RER = signal.lfilter_zi(b, a)   
    
    z_HP = signal.lfilter_zi(b, a)   

    # Initialize array to store angles for filtering
    LSP_arr = []
    LSP_arr_filt = []
    # LSR_arr = np.zeros(window_length + 1)
    # LEY_arr = np.zeros(window_length + 1)
    # LER_arr = np.zeros(window_length + 1)

    # RSP_arr = np.zeros(window_length + 1)
    # RSR_arr = np.zeros(window_length + 1)
    # REY_arr = np.zeros(window_length + 1)
    # RER_arr = np.zeros(window_length + 1)

    # Threshold to control or not a joint
    thresh = 0

    # COunter
    count = 1

    # Initialize time counter
    t1 = time.time()
    time_elapsed = 0.0

    # Start loop to receive angles and control Pepper joints
    while KtA.start_flag:
        try:
            # Init array with names to control Pepper joints
            names = []
            angles = []

            # Get angles from keypoints
            LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, HipPitch = KtA.get_angles()

            # Saturate angles to avoid exceding Pepper limits
            saturate_angles(memProxy, LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, HipPitch)
            
            ### DATA REAL-TIME FILTERING ###
            # Update arrays 1
            LSP_arr.append(LShoulderRoll)
            # LSP_arr = update_arr(LSP_arr, LShoulderPitch, window_length)
            # LSR_arr = update_arr(LSR_arr, LShoulderRoll, window_length)
            # LEY_arr = update_arr(LEY_arr, LElbowYaw, window_length)
            # LER_arr = update_arr(LER_arr, LElbowRoll, window_length)

            # RSP_arr = update_arr(RSP_arr, RShoulderPitch, window_length)
            # RSR_arr = update_arr(RSR_arr, RShoulderRoll, window_length)
            # REY_arr = update_arr(REY_arr, RElbowYaw, window_length)
            # RER_arr = update_arr(RER_arr, RElbowRoll, window_length)

            # Filter data with Butterworth filter
            LShoulderPitch, z_LSP = signal.lfilter(b, a, [LShoulderPitch], zi=z_LSP )
            LShoulderRoll, z_LSR = signal.lfilter(b, a, [LShoulderRoll], zi=z_LSR)
            LElbowYaw, z_LEY = signal.lfilter(b, a, [LElbowYaw], zi=z_LEY)
            LElbowRoll, z_LER = signal.lfilter(b, a, [LElbowRoll], zi=z_LER)

            RShoulderPitch, z_RSP = signal.lfilter(b, a, [RShoulderPitch], zi=z_RSP)
            RShoulderRoll, z_RSR = signal.lfilter(b, a, [RShoulderRoll], zi=z_RSR)
            RElbowYaw, z_REY = signal.lfilter(b, a, [RElbowYaw], zi=z_REY)
            RElbowRoll, z_RER = signal.lfilter(b, a, [RElbowRoll], zi=z_RER)

            HipPitch, z_HP = signal.lfilter(b, a, [HipPitch], zi=z_HP)
            
            LSP_arr_filt.append(LShoulderRoll)
            # print(LShoulderPitch)
            
            # Extract the filtered angle
            # LShoulderPitch = LSP_arr[window_length]
            # LShoulderRoll = LSR_arr[window_length]
            # LElbowYaw = LEY_arr[window_length]
            # LElbowRoll = LER_arr[window_length]

            # RShoulderPitch = RSP_arr[window_length]
            # RShoulderRoll = RSR_arr[window_length]
            # RElbowYaw = REY_arr[window_length]
            # RElbowRoll = RER_arr[window_length]

            

            ### Pepper joints control ###
            # Both shoulders
            names_shoulders = ["LShoulderPitch","LShoulderRoll","RShoulderPitch","RShoulderRoll"]
            angles_shoulders = [float(LShoulderPitch), float(LShoulderRoll), float(RShoulderPitch), float(RShoulderRoll)]

            # Both elbows
            names_elbows = ["LElbowYaw", "LElbowRoll","RElbowYaw","RElbowRoll"]
            angles_elbows = [float(LElbowYaw), float(LElbowRoll), float(RElbowYaw), float(RElbowRoll)]

            # HipPitch
            names_hip = ["HipPitch"]
            angles_hip = [float(HipPitch)]

            # Both arms 
            names = ["LShoulderPitch","LShoulderRoll", "LElbowYaw", "LElbowRoll", \
                     "RShoulderPitch","RShoulderRoll", "RElbowYaw", "RElbowRoll"]
            angles = [float(LShoulderPitch), float(LShoulderRoll), float(LElbowYaw), float(LElbowRoll), \
                      float(RShoulderPitch), float(RShoulderRoll), float(RElbowYaw), float(RElbowRoll)]
            
            # Speed limits for the joints
            fractionMaxSpeed = 0.15

            fractionMaxSpeed_shoulders = 0.15
            fractionMaxSpeed_elbows = 0.15
            fractionMaxSpeed_hip = 0.1

            # if names and angles:
            #     motion_service.setAngles(names, angles, fractionMaxSpeed)
            #     motion_service.setAngles(names_hip,angles_hip, fractionMaxSpeed_hip)

            if names_shoulders and angles_shoulders and names_elbows and angles_elbows and time_elapsed > 2.0:
                
                motion_service.setAngles(names_shoulders, angles_shoulders, fractionMaxSpeed_shoulders)
                motion_service.setAngles(names_elbows, angles_elbows, fractionMaxSpeed_elbows)
                motion_service.setAngles(names_hip,angles_hip, fractionMaxSpeed_hip)
            
            time_elapsed = time.time() - t1
            print(time_elapsed)

            if time_elapsed > 30:
                break
        
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            # Restart loop
            KtA.stop_receiving()
            main(session)
            sys.exit(-1)

    # Plot power spectrum and time signal
    N_samples = len(LSP_arr)
    sampling_rate = N_samples/time_elapsed
    time_samples = np.arange(0, time_elapsed, 1/sampling_rate)

    data = np.array(LSP_arr)
    data_filt = np.array(LSP_arr_filt)
    
    fourier_transform = np.fft.rfft(data)

    abs_fourier_transform = np.abs(fourier_transform)

    power_spectrum = np.square(abs_fourier_transform)

    frequency = np.linspace(0, sampling_rate/2, len(power_spectrum))

    print ("Sampling rate: %f" % sampling_rate)

    fig, axs = plt.subplots(2)
    fig.suptitle('LSP Time signal and power spectrum')
    if len(frequency) == len(power_spectrum):
        axs[0].plot(frequency, power_spectrum)
        axs[0].set(xlabel='frequency [1/s]', ylabel='power')
        axs[0].set_title('Power Spectrum')

    if len(time_samples) == len(data):
        axs[1].plot(time_samples, data)
        axs[1].set(xlabel='time [s]', ylabel='LSP angle')
        axs[1].set_title('LSP angle signal')
        

    if len(time_samples) == len(data_filt):
        axs[1].plot(time_samples, data_filt)
        axs[1].legend(['signal', 'filtered'])
        # axs[1].set(xlabel='time [s]', ylabel='LSP angle filt')
        # axs[1].set_title('LSP angle signal _filtered')

    plt.show()

    

    



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="130.251.13.154",
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
    main(session)


'''
# Control the angle only if the difference from the last control angle is greater than thresh
            # Left arm
            # if np.linalg.norm( LSP_arr[window_length] - LSP_arr[window_length-1] ) > thresh :  
            #     names.append("LShoulderPitch")
            #     angles.append(float(LShoulderPitch))
            
            # if np.linalg.norm(LSR_arr[window_length] - LSR_arr[window_length-1]) > thresh : 
            #     names.append("LShoulderRoll")
            #     angles.append(float(LShoulderRoll))
            
            # if np.linalg.norm(LEY_arr[window_length] - LEY_arr[window_length-1]) > thresh : 
            #     names.append("LElbowYaw")
            #     angles.append(float(LElbowYaw))

            # if np.linalg.norm(LER_arr[window_length] - LER_arr[window_length-1]) > thresh : 
            #     names.append("LElbowRoll")
            #     angles.append(float(LElbowRoll))

            # # Right arm
            # if np.linalg.norm( RSP_arr[window_length] - RSP_arr[window_length-1] ) > thresh :  
            #     names.append("RShoulderPitch")
            #     angles.append(float(RShoulderPitch))
            
            # if np.linalg.norm(RSR_arr[window_length] - RSR_arr[window_length-1]) > thresh : 
            #     names.append("RShoulderRoll")
            #     angles.append(float(RShoulderRoll))
            
            # if np.linalg.norm(REY_arr[window_length] - REY_arr[window_length-1]) > thresh : 
            #     names.append("RElbowYaw")
            #     angles.append(float(RElbowYaw))

            # if np.linalg.norm(RER_arr[window_length] - RER_arr[window_length-1]) > thresh: 
            #     names.append("RElbowRoll")
            #     angles.append(float(RElbowRoll))

        ## Left arm ##
            # names = ["LShoulderPitch","LShoulderRoll", "LElbowYaw", "LElbowRoll"]
            # angles = [float(LShoulderPitch), float(LShoulderRoll), float(LElbowYaw), float(LElbowRoll)]

            # # Left shoulder
            # names = ["LShoulderPitch","LShoulderRoll"]
            # angles = [float(LShoulderPitch),float(LShoulderRoll)]

            # Left elbow
            # names = ["LElbowYaw", "LElbowRoll"]
            # angles = [float(LElbowYaw), float(LElbowRoll)]

            ## Right arm ##
            # names = ["RShoulderPitch","RShoulderRoll", "RElbowYaw", "RElbowRoll"]
            # angles = [float(RShoulderPitch), float(RShoulderRoll), float(RElbowYaw), float(RElbowRoll)]

            # Right shoulder
            # names = ["RShoulderPitch","RShoulderRoll"]
            # angles = [float(RShoulderPitch), float(RShoulderRoll)]

            # # Right elbow
            # names = [ "RElbowYaw","RElbowRoll"]
            # angles = [float(RElbowYaw), float(RElbowRoll)]

'''
'''
# # Update arrays 2
            # LSP_arr_filt = update_arr(LSP_arr, LShoulderPitch, window_length)
            # LSR_arr_filt = update_arr(LSR_arr, LShoulderRoll, window_length)
            # LEY_arr_filt = update_arr(LEY_arr, LElbowYaw, window_length)
            # LER_arr_filt = update_arr(LER_arr, LElbowRoll, window_length)

            # RSP_arr_filt = update_arr(RSP_arr, RShoulderPitch, window_length)
            # RSR_arr_filt = update_arr(RSR_arr, RShoulderRoll, window_length)
            # REY_arr_filt = update_arr(REY_arr, RElbowYaw, window_length)
            # RER_arr_filt = update_arr(RER_arr, RElbowRoll, window_length)
            
            # # Filter angles using a Savitzky-Golay filter
            # # Left arm
            # LSP_arr_filt = savgol_filter(LSP_arr_filt, window_length, polyorder)
            # LSR_arr_filt = savgol_filter(LSR_arr_filt, window_length, polyorder)
            # LEY_arr_filt = savgol_filter(LEY_arr_filt, window_length, polyorder)
            # LER_arr_filt = savgol_filter(LER_arr_filt, window_length, polyorder)
            # # Right arm
            # RSP_arr_filt = savgol_filter(RSP_arr_filt, window_length, polyorder)
            # RSR_arr_filt = savgol_filter(RSR_arr_filt, window_length, polyorder)
            # REY_arr_filt = savgol_filter(REY_arr_filt, window_length, polyorder)
            # RER_arr_filt = savgol_filter(RER_arr_filt, window_length, polyorder)

            # # Extract the filtered angle
            # LShoulderPitch = LSP_arr_filt[window_length]
            # LShoulderRoll = LSR_arr_filt[window_length]
            # LElbowYaw = LEY_arr_filt[window_length]
            # LElbowRoll = LER_arr_filt[window_length]

            # RShoulderPitch = RSP_arr_filt[window_length]
            # RShoulderRoll = RSR_arr_filt[window_length]
            # RElbowYaw = REY_arr_filt[window_length]
            # RElbowRoll = RER_arr_filt[window_length]
'''