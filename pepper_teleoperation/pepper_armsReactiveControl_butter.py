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

# LShoulderPitch = LShoulderRoll = LElbowYaw = LElbowRoll = RShoulderPitch = RShoulderRoll = RElbowYaw = RElbowRoll = None
# session = None

## function saturate_angles
#
# Saturate angles before using them for controlling Pepper joints
def saturate_angles(mProxy, LSP, LSR, LEY, LER, RSP, RSR, REY, RER, HP, HEY):
    global LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, HipPitch, HeadYaw

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
    
    # HeadYaw saturation: -2.0857 to 2.0857
    if HEY is None:
        HeadYaw = mProxy.getData("Device/SubDeviceList/HeadYaw/Position/Actuator/Value")
        # print("RER")
    elif HEY < -2.0857:
        HeadYaw = -2.0857
    elif HEY > 2.0857:
        HeadYaw = 2.0857

    
def update_arr(arr, angle, window_length):

    # Temporary array to save data
    temp = np.zeros(window_length + 1)

    # Update last 6 values array
    for i in range(0,window_length-1):
        temp[i] = arr[i+1]
        
    temp[window_length] = angle

    arr = temp.copy()

    return arr

## function plot_data
#
# Plot raw and filtered angles at the end of the session
def plot_data(axs, raw_data, filt_data, name, time_elapsed, pos_x, pos_y, plot_PS=False):
    # Plot power spectrum and time signals (Raw and filtered)
    data = np.array(raw_data)
    data_filt = np.array(filt_data)

    N_samples = len(data)
    sampling_rate = N_samples/time_elapsed
    time_samples = np.arange(0, time_elapsed, 1/sampling_rate)

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

    if len(time_samples) == len(data):
        axs[pos_x, pos_y].plot(time_samples, data)
        axs[pos_x, pos_y].set(xlabel='time [s]', ylabel='Angle [rad]')
        axs[pos_x, pos_y].set_title('%s angle' % name)
        
    if len(time_samples) == len(data_filt):
        axs[pos_x, pos_y].plot(time_samples, data_filt)
        axs[pos_x, pos_y].legend(['signal', 'filtered'])

    # print ("Sampling rate: %f" % sampling_rate)

## function main
#
#
def main(session, ip_addr, port, show_plot):
    """
    This example uses the setAngles and setStiffnesses methods
    in order to perform reactive control.
    """

    global LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, HipPitch, HeadYaw

    # Get the services ALMotion and ALRobotPosture
    motion_service  = session.service("ALMotion")
    posture_service = session.service("ALRobotPosture")

    # Wake up robot
    motion_service.wakeUp()

    # Send robot to Stand Init
    posture_service.goToPosture("StandInit", 0.5)

    # Create proxy on ALMemory
    memProxy = ALProxy("ALMemory", ip_addr, port)

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

    motion_service.setStiffnesses("HeadYaw", stiffness)

    # Wait some time
    # time.sleep(2)
    
    # Initialize class KeypointsToAngles
    KtA = KeypointsToAngles()

    # Filter parameters 
    ## MOLTO BUONI
    # fs = 5.3        # sample rate, Hz
    # cutoff = 1.0    # desired cutoff frequency of the filter, Hz 
    # nyq = 0.5 * fs  # Nyquist Frequency
    # order = 2       # filter order

    ## PROVA
    fs = 5.3            # sample rate, Hz
    cutoff = 0.7        # desired cutoff frequency of the filter, Hz 
    nyq = 0.5 * fs      # Nyquist Frequency
    order = 1           # filter order

    normal_cutoff = cutoff / nyq    # Cutoff freq for lowpass filter

    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False, output='ba') 

    # # Plot the frequency response of the filter
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

    # Initialize filters for each angle
    z_LSP = signal.lfilter_zi(b, a)   
    z_LSR = signal.lfilter_zi(b, a)   
    z_LEY = signal.lfilter_zi(b, a)   
    z_LER = signal.lfilter_zi(b, a)  

    z_RSP = signal.lfilter_zi(b, a)   
    z_RSR = signal.lfilter_zi(b, a)   
    z_REY = signal.lfilter_zi(b, a)   
    z_RER = signal.lfilter_zi(b, a)   
    
    b_HP, a_HP = signal.butter(order, 0.3/nyq, btype='low', analog=False, output='ba') 
    z_HP = signal.lfilter_zi(b_HP, a_HP)   

    # Initialize arrays to store angles for plots
    # Left arm
    LSP_arr = []
    LSP_arr_filt = []
    LSR_arr = []
    LSR_arr_filt = []
    LEY_arr = []
    LEY_arr_filt = []
    LER_arr = []
    LER_arr_filt = []
    # Right arm
    RSP_arr = []
    RSP_arr_filt= []
    RSR_arr = []
    RSR_arr_filt = []
    REY_arr = []
    REY_arr_filt = []
    RER_arr = []
    RER_arr_filt = []
    # Hip
    HP_arr = []
    HP_arr_filt = []

    # Initialize time counter
    t1 = time.time()
    time_elapsed = 0.0

    # Start loop to receive angles and control Pepper joints
    while KtA.start_flag:
        try:
            # Init lists to control Pepper joints
            names = []
            angles = []

            # Get angles from keypoints
            LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, HipPitch, HeadYaw = KtA.get_angles()

            # Saturate angles to avoid exceding Pepper limits
            saturate_angles(memProxy, LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, HipPitch, HeadYaw)
            
            if show_plot:
                # Update lists for plots
                LSP_arr.append(LShoulderPitch)
                LSR_arr.append(LShoulderRoll)
                LEY_arr.append(LElbowYaw)
                LER_arr.append(LElbowRoll)

                RSP_arr.append(RShoulderPitch)
                RSR_arr.append(RShoulderRoll)
                REY_arr.append(RElbowYaw)
                RER_arr.append(RElbowRoll)

                HP_arr.append(HipPitch)

            ### DATA REAL-TIME FILTERING ###
            # Filter data with Butterworth filter
            LShoulderPitch, z_LSP = signal.lfilter(b, a, [LShoulderPitch], zi=z_LSP )
            LShoulderRoll, z_LSR = signal.lfilter(b, a, [LShoulderRoll], zi=z_LSR)
            LElbowYaw, z_LEY = signal.lfilter(b, a, [LElbowYaw], zi=z_LEY)
            LElbowRoll, z_LER = signal.lfilter(b, a, [LElbowRoll], zi=z_LER)

            RShoulderPitch, z_RSP = signal.lfilter(b, a, [RShoulderPitch], zi=z_RSP)
            RShoulderRoll, z_RSR = signal.lfilter(b, a, [RShoulderRoll], zi=z_RSR)
            RElbowYaw, z_REY = signal.lfilter(b, a, [RElbowYaw], zi=z_REY)
            RElbowRoll, z_RER = signal.lfilter(b, a, [RElbowRoll], zi=z_RER)

            HipPitch, z_HP = signal.lfilter(b_HP, a_HP, [HipPitch], zi=z_HP)
            
            if show_plot:
                # Store filtered angles for plots
                LSP_arr_filt.append(LShoulderPitch)
                LSR_arr_filt.append(LShoulderRoll)
                LEY_arr_filt.append(LElbowYaw)
                LER_arr_filt.append(LElbowRoll)

                RSP_arr_filt.append(RShoulderPitch)
                RSR_arr_filt.append(RShoulderRoll)
                REY_arr_filt.append(RElbowYaw)
                RER_arr_filt.append(RElbowRoll)
                
                HP_arr_filt.append(HipPitch)
            
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

            # HeadYaw
            names_hey = ["HeadYaw"]
            angles_hey = [float(HeadYaw)]

            # Arms 
            names = ["LShoulderPitch","LShoulderRoll", "LElbowYaw", "LElbowRoll", \
                     "RShoulderPitch","RShoulderRoll", "RElbowYaw", "RElbowRoll"]
            angles = [float(LShoulderPitch), float(LShoulderRoll), float(LElbowYaw), float(LElbowRoll), \
                      float(RShoulderPitch), float(RShoulderRoll), float(RElbowYaw), float(RElbowRoll)]
            
            # Speed limits for the joints
            fractionMaxSpeed = 0.15

            fractionMaxSpeed_shoulders = 0.15
            fractionMaxSpeed_elbows = 0.15
            fractionMaxSpeed_hip = 0.1

            # Send control commands to the robot if 2 seconds have passed (Butterworth Filter initialization time) 
            # All joints with the same speed
            # if names and angles and time_elapsed > 2.0:
            #     motion_service.setAngles(names, angles, fractionMaxSpeed)
            #     motion_service.setAngles(names_hip,angles_hip, fractionMaxSpeed_hip)

            # Different joints have different speeds
            # if names_shoulders and angles_shoulders and names_elbows and angles_elbows and time_elapsed > 2.0:
                
            #     motion_service.setAngles(names_shoulders, angles_shoulders, fractionMaxSpeed_shoulders)
            #     motion_service.setAngles(names_elbows, angles_elbows, fractionMaxSpeed_elbows)
            #     motion_service.setAngles(names_hip,angles_hip, fractionMaxSpeed_hip)
            
            time_elapsed = time.time() - t1
            # print(time_elapsed)
            
        
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            # Restart loop
            KtA.stop_receiving()
            main(session)
            sys.exit(-1)
        
        except KeyboardInterrupt:
            if show_plot:
                # Create figure with 9 subplots
                fig, axs = plt.subplots(3,3)
                fig.suptitle('Joints angles over time')

                # Plot joint angles
                plot_data(axs, LSP_arr, LSP_arr_filt, 'LSP', time_elapsed, pos_x=0, pos_y=0)
                plot_data(axs, LSR_arr, LSR_arr_filt, 'LSR', time_elapsed, pos_x=0, pos_y=1)
                plot_data(axs, LEY_arr, LEY_arr_filt, 'LEY', time_elapsed, pos_x=0, pos_y=2)
                plot_data(axs, LER_arr, LER_arr_filt, 'LER', time_elapsed, pos_x=1, pos_y=0)

                plot_data(axs, RSP_arr, RSP_arr_filt, 'RSP', time_elapsed, pos_x=1, pos_y=1)
                plot_data(axs, RSR_arr, RSR_arr_filt, 'RSR', time_elapsed, pos_x=1, pos_y=2)
                plot_data(axs, REY_arr, REY_arr_filt, 'REY', time_elapsed, pos_x=2, pos_y=0)
                plot_data(axs, RER_arr, RER_arr_filt, 'RER', time_elapsed, pos_x=2, pos_y=1)

                plot_data(axs, HP_arr,  HP_arr_filt,  'HP',  time_elapsed, pos_x=2, pos_y=2)

                # Show plot
                plt.show()
                sys.exit(1)
            else:
                sys.exit(1)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="130.251.13.154",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--show_plots", type=bool, default=True,
                        help="Select True if you want to see the plots when you interrupt the script with the keyboard")

    args = parser.parse_args()
    show_plot = args.show_plots
    ip_addr = args.ip 
    port = args.port
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session, ip_addr, port, show_plot)


'''
# Plot power spectrum and time signals (Raw and filtered)
    # N_samples = len(LSP_arr)
    # sampling_rate = N_samples/time_elapsed
    # time_samples = np.arange(0, time_elapsed, 1/sampling_rate)

    # data = np.array(LSP_arr)
    # data_filt = np.array(LSP_arr_filt)
    
    # fourier_transform = np.fft.rfft(data)

    # abs_fourier_transform = np.abs(fourier_transform)

    # power_spectrum = np.square(abs_fourier_transform)

    # frequency = np.linspace(0, sampling_rate/2, len(power_spectrum))

    # print ("Sampling rate: %f" % sampling_rate)

    # fig, axs = plt.subplots(2)
    # fig.suptitle('LSP Time signal and power spectrum')
    # if len(frequency) == len(power_spectrum):
    #     axs[0].plot(frequency, power_spectrum)
    #     axs[0].set(xlabel='frequency [1/s]', ylabel='power')
    #     axs[0].set_title('Power Spectrum')

    # if len(time_samples) == len(data):
    #     axs[1].plot(time_samples, data)
    #     axs[1].set(xlabel='time [s]', ylabel='LSP angle')
    #     axs[1].set_title('LSP angle signal')
        

    # if len(time_samples) == len(data_filt):
    #     axs[1].plot(time_samples, data_filt)
    #     axs[1].legend(['signal', 'filtered'])

    # plt.show()
'''