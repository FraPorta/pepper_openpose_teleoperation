#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Use setAngles and setStiffnesses Methods"""

import qi
from naoqi import ALProxy
import argparse
import sys
import time
import numpy as np


from keypoints_to_angles import KeypointsToAngles 

LShoulderPitch = LShoulderRoll = LElbowYaw = LElbowRoll = RShoulderPitch = RShoulderRoll = RElbowYaw = RElbowRoll = None
session = None

## function saturate_angles
#
# Saturate angles before using them for controlling Pepper joints
def saturate_angles(mProxy, LSP, LSR, LEY, LER, RSP, RSR, REY, RER):
    global LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll

    ## LEFT ##
    
    # LShoulderPitch saturation
    if LSP is None:
        LShoulderPitch = mProxy.getData("Device/SubDeviceList/LShoulderPitch/Position/Actuator/Value")
    elif LSP < -2.0857:
        LShoulderPitch = -2.0857
    elif LSP > 2.0857:
        LShoulderPitch = 2.0857
    
    # LShoulderRoll saturation
    if LSR is None:
        LShoulderRoll = mProxy.getData("Device/SubDeviceList/LShoulderRoll/Position/Actuator/Value")
    elif LSR < 0.0087:
        LShoulderRoll = 0.0087
    elif LSR > 1.5620:
        LShoulderRoll = 1.5620
        
    # LElbowYaw saturation
    if LEY is None:
        LElbowYaw = mProxy.getData("Device/SubDeviceList/LElbowYaw/Position/Actuator/Value")
    elif LEY < -2.0857:
        LElbowYaw = -2.0857
    elif LEY > 2.0857:
        LElbowYaw = 2.0857

    # LElbowRoll saturation
    if LER is None:
        LElbowRoll = mProxy.getData("Device/SubDeviceList/LElbowRoll/Position/Actuator/Value")
    elif LER < -1.5620:
        LElbowRoll = -1.5620
    elif LER > -0.0087:
        LElbowRoll = -0.0087


    ## RIGHT ##

    # RShoulderPitch saturation
    if RSP is None:
        RShoulderPitch = mProxy.getData("Device/SubDeviceList/RShoulderPitch/Position/Actuator/Value")
    elif RSP < -2.0857:
        RShoulderPitch = -2.0857
    elif RSP > 2.0857:
        RShoulderPitch = 2.0857
    
    # RShoulderRoll saturation
    if RSR is None:
        RShoulderRoll = mProxy.getData("Device/SubDeviceList/RShoulderRoll/Position/Actuator/Value")
    elif RSR < -1.5620 :
        RShoulderRoll = -1.5620
    elif RSR > -0.0087:
        RShoulderRoll = -0.0087
        
    # RElbowYaw saturation
    if REY is None:
        RElbowYaw = mProxy.getData("Device/SubDeviceList/RElbowYaw/Position/Actuator/Value")
    elif REY < -2.0857:
        RElbowYaw = -2.0857
    elif REY > 2.0857:
        RElbowYaw = 2.0857

    # RElbowRoll saturation
    if RER is None:
        RElbowRoll = mProxy.getData("Device/SubDeviceList/RElbowRoll/Position/Actuator/Value")
    elif RER < 0.0087:
        RElbowRoll = 0.0087
    elif RER > 1.5620:
        RElbowRoll = 1.5620

    
def main(session):
    """
    This example uses the setAngles and setStiffnesses methods
    in order to simulate reactive control.
    """

    global LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll

    # Get the services ALMotion and ALRobotPosture
    motion_service  = session.service("ALMotion")
    posture_service = session.service("ALRobotPosture")

    # Wake up robot
    motion_service.wakeUp()

    # Send robot to Stand Init
    posture_service.goToPosture("StandInit", 0.5)

    # create proxy on ALMemory
    memProxy = ALProxy("ALMemory","130.251.13.150",9559)

    motion_service.setStiffnesses("LShoulderPitch", 0.2)
    motion_service.setStiffnesses("LShoulderRoll", 0.2)

    motion_service.setStiffnesses("LElbowYaw", 0.2)
    motion_service.setStiffnesses("LElbowRoll", 0.2)

    motion_service.setStiffnesses("RShoulderPitch", 0.2)
    motion_service.setStiffnesses("RShoulderRoll", 0.2)

    motion_service.setStiffnesses("RElbowYaw", 0.2)
    motion_service.setStiffnesses("RElbowRoll", 0.2)

    # Wait some time
    time.sleep(2)
    
    # Initialize class KeypointsToAngles
    KtA = KeypointsToAngles()

    # Start loop to receive angles and control Pepper joints
    while KtA.start_flag:
        try:
            # Get angles from keypoints
            LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll = KtA.get_angles()
            # print(RElbowYaw)

            # Saturate angles to avoid exceding Pepper limits
            saturate_angles(memProxy, LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll)

            ## Print angles ##
            # print("LShoulderPitch:")
            # # print((LShoulderPitch * 180 )/ np.pi)
            # print(float(LShoulderPitch))
            # print("LShoulderRoll:")
            # # print((LShoulderRoll * 180)/ np.pi)
            # print(float(LShoulderRoll))

            # print("LElbowYaw:")
            # print((LElbowYaw * 180 )/ np.pi)
            # # print(float(LElbowYaw))
            # print("LElbowRoll:")
            # print((LElbowRoll * 180)/ np.pi)
            # # print(float(LElbowRoll))

            ### Pepper joints control ###

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

            # Both shoulders
            # names = ["LShoulderPitch","LShoulderRoll","RShoulderPitch","RShoulderRoll"]
            # angles = [float(LShoulderPitch), float(LShoulderRoll), float(RShoulderPitch), float(RShoulderRoll)]

            # Both arms
            names = ["LShoulderPitch","LShoulderRoll", "LElbowYaw", "LElbowRoll", \
                     "RShoulderPitch","RShoulderRoll", "RElbowYaw", "RElbowRoll"]
            angles = [float(LShoulderPitch), float(LShoulderRoll), float(LElbowYaw), float(LElbowRoll), \
                      float(RShoulderPitch), float(RShoulderRoll), float(RElbowYaw), float(RElbowRoll)]
            
            fractionMaxSpeed = 0.1
            motion_service.setAngles(names,angles,fractionMaxSpeed)

        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            # Restart loop
            KtA.stop_receiving()
            # main(session)
            # main()
            sys.exit(-1)
            

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="130.251.13.150",
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
    # main()