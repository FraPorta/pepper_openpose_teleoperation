# -*- encoding: UTF-8 -*-

import qi
from naoqi import ALProxy
import argparse
import sys
import time
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

# local imports
from keypoints_to_angles import KeypointsToAngles 
from sensory_hub import DetectUserDepth, Person
from approach_user import ApproachUser


LShoulderPitch = LShoulderRoll = LElbowYaw = LElbowRoll = RShoulderPitch = RShoulderRoll = RElbowYaw = RElbowRoll = HipPitch = HeadYaw = HeadPitch = None
HEY_arr = HEY_arr_filt = time_elapsed = None

##  function saturate_angles
#
#   Saturate angles before using them for controlling Pepper joints
def saturate_angles(mProxy, LSP, LSR, LEY, LER, RSP, RSR, REY, RER, HP, HEY, HEP):
    global LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, HipPitch, HeadYaw, HeadPitch
    # limit percentage for some angles 
    limit = 0.5
     
    ## LEFT ##
    # LShoulderPitch saturation
    if LSP is None:
        # LShoulderPitch = mProxy.getData("Device/SubDeviceList/LShoulderPitch/Position/Actuator/Value")
        LShoulderPitch = mProxy.getData("Device/SubDeviceList/LShoulderPitch/Position/Sensor/Value")
    elif LSP < -2.0857:
        LShoulderPitch = -2.0857
    elif LSP > 2.0857:
        LShoulderPitch = 2.0857
    
    # LShoulderRoll saturation
    if LSR is None:
        # LShoulderRoll = mProxy.getData("Device/SubDeviceList/LShoulderRoll/Position/Actuator/Value")
        LShoulderRoll = mProxy.getData("Device/SubDeviceList/LShoulderRoll/Position/Sensor/Value")
    elif LSR < 0.0087:
        LShoulderRoll = 0.0087
    elif LSR > 1.5620:
        LShoulderRoll = 1.5620
        
    # LElbowYaw saturation
    if LEY is None:
        # LElbowYaw = mProxy.getData("Device/SubDeviceList/LElbowYaw/Position/Actuator/Value")
        LElbowYaw = mProxy.getData("Device/SubDeviceList/LElbowYaw/Position/Sensor/Value")
    elif LEY < -2.0857:
        LElbowYaw = -2.0857
    elif LEY > 2.0857:
        LElbowYaw = 2.0857

    # LElbowRoll saturation
    if LER is None:
        # LElbowRoll = mProxy.getData("Device/SubDeviceList/LElbowRoll/Position/Actuator/Value")
        LElbowRoll = mProxy.getData("Device/SubDeviceList/LElbowRoll/Position/Sensor/Value")
    elif LER < -1.5620:
        LElbowRoll = -1.5620
    elif LER > -0.0087:
        LElbowRoll = -0.0087


    ## RIGHT ##
    # RShoulderPitch saturation
    if RSP is None:
        # RShoulderPitch = mProxy.getData("Device/SubDeviceList/RShoulderPitch/Position/Actuator/Value")
        RShoulderPitch = mProxy.getData("Device/SubDeviceList/RShoulderPitch/Position/Sensor/Value")
    elif RSP < -2.0857:
        RShoulderPitch = -2.0857
    elif RSP > 2.0857:
        RShoulderPitch = 2.0857
    
    # RShoulderRoll saturation
    if RSR is None:
        # RShoulderRoll = mProxy.getData("Device/SubDeviceList/RShoulderRoll/Position/Actuator/Value")
        RShoulderRoll = mProxy.getData("Device/SubDeviceList/RShoulderRoll/Position/Sensor/Value")
        # print("RSR")
    elif RSR < -1.5620 :
        RShoulderRoll = -1.5620
    elif RSR > -0.0087:
        RShoulderRoll = -0.0087
        
    # RElbowYaw saturation
    if REY is None:
        # RElbowYaw = mProxy.getData("Device/SubDeviceList/RElbowYaw/Position/Actuator/Value")
        RElbowYaw = mProxy.getData("Device/SubDeviceList/RElbowYaw/Position/Sensor/Value")
    elif REY < -2.0857:
        RElbowYaw = -2.0857
    elif REY > 2.0857:
        RElbowYaw = 2.0857

    # RElbowRoll saturation
    if RER is None:
        # RElbowRoll = mProxy.getData("Device/SubDeviceList/RElbowRoll/Position/Actuator/Value")
        RElbowRoll = mProxy.getData("Device/SubDeviceList/RElbowRoll/Position/Sensor/Value")
    elif RER < 0.0087:
        RElbowRoll = 0.0087
    elif RER > 1.5620:
        RElbowRoll = 1.5620

    # HipPitch saturation: -1.0385 to 1.0385
    if HP is None:
        # HipPitch = mProxy.getData("Device/SubDeviceList/HipPitch/Position/Actuator/Value")
        HipPitch = mProxy.getData("Device/SubDeviceList/HipPitch/Position/Sensor/Value")
        # print("RER")
    elif HP < -1.0385:
        HipPitch = -1.0385
    elif HP > 1.0385:
        HipPitch = 1.0385
    
    # HeadYaw saturation: -2.0857 to 2.0857
    limit = 0.6
    if HEY is None:
        # HeadYaw = mProxy.getData("Device/SubDeviceList/HeadYaw/Position/Actuator/Value")
        HeadYaw = mProxy.getData("Device/SubDeviceList/HeadYaw/Position/Sensor/Value")
    elif HEY > 2.0857*limit:
        HeadYaw = 2.0857*limit
    elif HEY < -2.0857*limit:
        HeadYaw = -2.0857*limit
        
    # elif HEY_arr:
    #     if abs(HEY_arr[-1] - HEY) < 0.3 and time_elapsed > 2.0:
    #         HeadYaw = HEY_arr[-1]
        
    # # HeadPitch saturation: -0.7068 to 0.4451
    # if HEP is None:
    #     HeadPitch = mProxy.getData("Device/SubDeviceList/HeadPitch/Position/Actuator/Value")
    # elif HEP < -0.7068:
    #     HeadPitch = -0.7068
    # elif HEP > 0.4451:
    #     HeadPitch = 0.4451 
    

##  function plot_data
#
#   Plot raw and filtered angles at the end of the session
def plot_data(axs, raw_data, filt_data, robot_data, name, time_elapsed, pos_x, pos_y, plot_PS=False):
    # Plot time signals (Raw and filtered)
    data = np.array(raw_data)
    N_samples = len(data)
    sampling_rate = N_samples/time_elapsed
    time_samples = np.arange(0, time_elapsed, 1/sampling_rate)
    
    
    data_filt = np.array(filt_data)
    if len(time_samples) != len(robot_data):
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

        
        
##  function joints_control
#
#   This function uses the setAngles and setStiffnesses methods
#   in order to perform reactive control on Pepper upper body.
#   The joints angles are filtered in real-time using a Butterworth filter
def joints_control(session, ip_addr, port, show_plot):
    """
    This function uses the setAngles and setStiffnesses methods
    in order to perform reactive control on Pepper upper body.
    """

    global LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, HipPitch, HeadYaw, HeadPitch
    global HEY_arr, HEY_arr_filt, time_elapsed
    
    loop_interrupted = False
    
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
    # motion_service.setStiffnesses("HeadYaw", stiffness)
    # motion_service.setStiffnesses("HeadPitch", stiffness)

    # Set fixed head pitch angle
    # motion_service.setAngles("HeadPitch", 0.0 , 0.5)
    
    # Disable external collision protection
    motion_service.setExternalCollisionProtectionEnabled("Arms", False)
    
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
    
    # Head and Hip filters initialization
    # Continuous (Head and Pitch)
    b_HP, a_HP = signal.butter(2, 0.3/nyq, btype='low', analog=False, output='ba') 
    # Steps (only for the head)
    # b_HP, a_HP = signal.butter(2, 0.1/nyq, btype='low', analog=False, output='ba') 
    
    z_HP = signal.lfilter_zi(b_HP, a_HP)   
    z_HEY = signal.lfilter_zi(b_HP, a_HP)   
    z_HEP = signal.lfilter_zi(b_HP, a_HP)   

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
    
    # Head
    HEY_arr = []
    HEY_arr_filt = []
    HEP_arr = []
    HEP_arr_filt = []

    # Initialize time counter
    t1 = time.time()
    time_elapsed = 0.0

    print("Start controlling Pepper joints!")
    
    # Start loop to receive angles and control Pepper joints
    while KtA.start_flag and not loop_interrupted:
        try:
            
            
            # # Init lists to control Pepper joints
            # names = []
            # angles = []

            # Get angles from keypoints
            LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, HipPitch, HeadYaw, HeadPitch = KtA.get_angles()

            # Saturate angles to avoid exceding Pepper limits
            saturate_angles(memProxy, LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, HipPitch, HeadYaw, HeadPitch)
            
            if show_plot and time_elapsed > 2.0:
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
                HEY_arr.append(HeadYaw)
                HEP_arr.append(HeadPitch)
                

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
            HeadYaw, z_HEY = signal.lfilter(b_HP, a_HP, [HeadYaw], zi=z_HEY)
            # HeadPitch, z_HEP = signal.lfilter(b_HP, a_HP, [HeadPitch], zi=z_HEP)
          
            if show_plot and time_elapsed > 2.0:
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
                HEY_arr_filt.append(HeadYaw)
                HEP_arr_filt.append(HeadPitch)
            
            
            ### Pepper joints control ###
            # HeadYaw
            names_hey = ["HeadYaw"]
            if HeadYaw < 0.3 and HeadYaw > -0.3:
                angles_hey = [0.0]
            else:
                angles_hey = [float(HeadYaw)]
            '''
            elif HeadYaw >= 0.3 and HeadYaw < 0.7:
                angles_hey = [0.45]
            elif HeadYaw >= 0.7 and HeadYaw < 1.0:
                angles_hey = [0.85]
            elif HeadYaw >= 1.0 and HeadYaw < 2.0857:
                angles_hey = [1.0]
            
            elif HeadYaw > -0.7 and HeadYaw <= -0.3:
                angles_hey = [-0.45]
            elif HeadYaw > -1.0 and HeadYaw <= -0.7:
                angles_hey = [-0.85]
            elif HeadYaw > -2.0857 and HeadYaw <= -1.0:
                angles_hey = [-1.0]
            
            print(angles_hey)
            '''
            
            # All joints
            names = ["LShoulderPitch","LShoulderRoll", "LElbowYaw", "LElbowRoll", \
                     "RShoulderPitch","RShoulderRoll", "RElbowYaw", "RElbowRoll", "HipPitch"]
            angles = [float(LShoulderPitch), float(LShoulderRoll), float(LElbowYaw), float(LElbowRoll), \
                      float(RShoulderPitch), float(RShoulderRoll), float(RElbowYaw), float(RElbowRoll), float(HipPitch)]
            
            # Speed limits for the joints
            fractionMaxSpeed = 0.15
            fractionMaxSpeed_head = 0.15

            ## Send control commands to the robot if 2 seconds have passed (Butterworth Filter initialization time) ##
            # All joints with the same speed
            if time_elapsed > 2.0:
                motion_service.setAngles(names, angles, fractionMaxSpeed)
                # motion_service.setAngles(names_hey, angles_hey, fractionMaxSpeed_head)
            
            if show_plot and time_elapsed > 2.0:
                # Update lists for plots
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
            time_elapsed = time.time() - t1
        
        # If the user stops the script with CTRL+C, interrupt loop
        except KeyboardInterrupt:
            loop_interrupted = True
                
        # Catch other exceptions
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            # Restart loop
            KtA.stop_receiving()

            sys.exit(-1)
            
    # show plots of the joints angles
    if show_plot:
        # Create figure with 12 subplots
        fig, axs = plt.subplots(3,3)
        fig.suptitle('Joints angles over time')

        # Plot joint angles
        plot_data(axs, LSP_arr, LSP_arr_filt, LSP_arr_robot, 'LSP', time_elapsed, pos_x=0, pos_y=0)
        plot_data(axs, LSR_arr, LSR_arr_filt, LSR_arr_robot, 'LSR', time_elapsed, pos_x=0, pos_y=1)
        plot_data(axs, LEY_arr, LEY_arr_filt, LEY_arr_robot, 'LEY', time_elapsed, pos_x=0, pos_y=2)
        plot_data(axs, LER_arr, LER_arr_filt, LER_arr_robot, 'LER', time_elapsed, pos_x=1, pos_y=0)

        plot_data(axs, RSP_arr, RSP_arr_filt, RSP_arr_robot, 'RSP', time_elapsed, pos_x=1, pos_y=1)
        plot_data(axs, RSR_arr, RSR_arr_filt, RSR_arr_robot, 'RSR', time_elapsed, pos_x=1, pos_y=2)
        plot_data(axs, REY_arr, REY_arr_filt, REY_arr_robot, 'REY', time_elapsed, pos_x=2, pos_y=0)
        plot_data(axs, RER_arr, RER_arr_filt, RER_arr_robot, 'RER', time_elapsed, pos_x=2, pos_y=1)

        plot_data(axs, HP_arr,  HP_arr_filt,  HP_arr_robot,  'HP',  time_elapsed, pos_x=2, pos_y=2)
        # plot_data(axs, HEY_arr, HEY_arr_filt, 'HEY', time_elapsed, pos_x=2, pos_y=1)
        # plot_data(axs, HEP_arr, HEP_arr_filt, 'HEP', time_elapsed, pos_x=2, pos_y=2)

        # Show plot
        plt.show()
    
    print("Program terminated cleanly")
            
##  function approach_user
#
#   Pepper searches for a person and then approaches it        
def approach_user(session):
    # Approach the user
    apar = ""
    cpar = "1"
    
    dud = DetectUserDepth(session, None, False)
    dud.start()
    
    au = ApproachUser(apar, cpar, session)
    au.run()

    dud.stop()
    
    return au.user_approached
    
# Main initialization
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


    args = parser.parse_args()
    show_plot = bool(args.show_plots)
    approach_requested = bool(args.approach_user)
    approach_only = bool(args.approach_only)
    
    ip_addr = args.ip 
    port = args.port
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    
    # Try to approach the user (repeat until a user is approached)
    if approach_requested or approach_only:
        while not approach_user(session):
            time.sleep(1)
    
    # Start receiving keypoints and controlling Pepper joints
    if not approach_only:
        print("Waiting for keypoints...")
        joints_control(session, ip_addr, port, show_plot)
        


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