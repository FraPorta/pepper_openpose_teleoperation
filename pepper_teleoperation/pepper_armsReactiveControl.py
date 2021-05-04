#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Use setAngles and setStiffnesses Methods"""

import qi
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
        
    # LElbowYaw saturation
    if REY is None:
        RElbowYaw = mProxy.getData("Device/SubDeviceList/RElbowYaw/Position/Actuator/Value")
    if REY < -2.0857:
        RElbowYaw = -2.0857
    elif REY > 2.0857:
        RElbowYaw = 2.0857

    # LElbowRoll saturation
    if RER is None:
        RElbowRoll = mProxy.getData("Device/SubDeviceList/RElbowRoll/Position/Actuator/Value")
    if RER < 0.0087:
        RElbowRoll = 0.0087
    elif RER > 1.5620:
        RElbowRoll = 1.5620

    
# def main(session):
def main():
    """
    This example uses the setAngles and setStiffnesses methods
    in order to simulate reactive control.
    """

    global LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll

    # # Get the service ALMotion.
    # motion_service  = session.service("ALMotion")

    # create proxy on ALMemory
    memProxy = ALProxy("ALMemory","localhost",9559)

    #get data. Val can be int, float, list, string
    # val = memProxy.getData("Device/SubDeviceList/LShoulderPitch/Position/Actuator/Value")

    # motion_service.setStiffnesses("LShoulderPitch", 1.0)
    
    # Initialize class KeypointsToAngles
    KtA = KeypointsToAngles()

    # Start loop to receive angles and control Pepper joints
    while KtA.start_flag:
        try:
            # Get angles from keypoints
            LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll = KtA.get_angles()
             
            joint_angles = {'LShoulderPitch':LShoulderPitch,
                            'LShoulderRoll':LShoulderRoll,
                            'LElbowYaw':LElbowYaw,
                            'LElbowRoll':LElbowRoll,
                            'RShoulderPitch':RShoulderPitch,
                            'RShoulderRoll':RShoulderRoll,
                            'RElbowYaw':RElbowYaw,
                            'RElbowRoll':RElbowRoll}
            
            # if LShoulderPitch is not None and LShoulderRoll is not None and LElbowYaw is not None and LElbowRoll is not None and \
            #    RShoulderPitch is not None and RShoulderRoll is not None and RElbowYaw is not None and RElbowRoll is not None:

            # Saturate angles to avoid exceding Pepper limits
            saturate_angles(memproxy, LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll)

            # Print angles
            print("LShoulderPitch:")
            print((LShoulderPitch * 180 )/ np.pi)

            print("LShoulderRoll:")
            print((LShoulderRoll * 180)/ np.pi)

            # # Example simulating reactive control
            # names = ["LShoulderPitch", "LShoulderRoll"]
            # angles = [LShoulderPitch,LShoulderRoll]
            # fractionMaxSpeed = 0.1
            # motion_service.setAngles(names,angles,fractionMaxSpeed)

            # wait half a second
            # time.sleep(0.1)

            # time.sleep(3.0)
            # motion_service.setStiffnesses("Head", 0.0)

        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            # Restart loop
            KtA.stop_receiving()
            main(session)
            # main()
            

if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--ip", type=str, default="127.0.0.1",
    #                     help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    # parser.add_argument("--port", type=int, default=9559,
    #                     help="Naoqi port number")

    # args = parser.parse_args()
    # session = qi.Session()
    # try:
    #     session.connect("tcp://" + args.ip + ":" + str(args.port))
    # except RuntimeError:
    #     print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
    #            "Please check your script arguments. Run with -h option for help.")
    #     sys.exit(1)
    # main(session)
    main()