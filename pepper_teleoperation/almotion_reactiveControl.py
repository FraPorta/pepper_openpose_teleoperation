#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Use setAngles and setStiffnesses Methods"""

import qi
from naoqi import ALProxy
import argparse
import sys
import time



def main(session):
    """
    This example uses the setAngles and setStiffnesses methods
    in order to simulate reactive control.
    """
    # Get the service ALMotion.

    motion_service  = session.service("ALMotion")
   
    # posture_service = session.service("ALRobotPosture")

    # Wake up robot
    # motion_service.wakeUp()

    # Send robot to Stand Init
    # posture_service.goToPosture("StandInit", 0.5)

    motion_service.setStiffnesses("LShoulderPitch", 1.0)
    motion_service.setStiffnesses("LShoulderRoll", 1.0)
    


    time.sleep(1)

    # create proxy on ALMemory
    mProxy = ALProxy("ALMemory","130.251.13.150",9559)

    # ## LEFT ##
    LShoulderPitch = mProxy.getData("Device/SubDeviceList/LShoulderPitch/Position/Actuator/Value")
    LShoulderRoll = mProxy.getData("Device/SubDeviceList/LShoulderRoll/Position/Actuator/Value")
    LElbowYaw = mProxy.getData("Device/SubDeviceList/LElbowYaw/Position/Actuator/Value")
    LElbowRoll = mProxy.getData("Device/SubDeviceList/LElbowRoll/Position/Actuator/Value")
    ## RIGHT ##
    RShoulderPitch = mProxy.getData("Device/SubDeviceList/RShoulderPitch/Position/Actuator/Value")
    RShoulderRoll = mProxy.getData("Device/SubDeviceList/RShoulderRoll/Position/Actuator/Value")
    RElbowYaw = mProxy.getData("Device/SubDeviceList/RElbowYaw/Position/Actuator/Value")
    RElbowRoll = mProxy.getData("Device/SubDeviceList/RElbowRoll/Position/Actuator/Value")

    joint_angles = {'LShoulderPitch':LShoulderPitch,
                    'LShoulderRoll':LShoulderRoll,
                    'LElbowYaw':LElbowYaw,
                    'LElbowRoll':LElbowRoll,
                    'RShoulderPitch':RShoulderPitch,
                    'RShoulderRoll':RShoulderRoll,
                    'RElbowYaw':RElbowYaw,
                    'RElbowRoll':RElbowRoll}
    
    print(joint_angles)
    
    
    # Example simulating reactive control
    names = ["LShoulderPitch","LShoulderRoll"]
    angles = [0.5,0.5]
    fractionMaxSpeed = 0.1
    motion_service.setAngles(names,angles,fractionMaxSpeed)
    # wait half a second
    time.sleep(0.2)
    # change target
    angles =[0.6,0.6]
    motion_service.setAngles(names,angles,fractionMaxSpeed)
    # wait half a second
    time.sleep(0.2)
    # change target
    angles = [0.7,0.7]
    motion_service.setAngles(names,angles,fractionMaxSpeed)
    time.sleep(0.2)
    # change target
    angles =[0.8,0.8]
    motion_service.setAngles(names,angles,fractionMaxSpeed)
    # wait half a second
    time.sleep(0.2)

    time.sleep(3.0)
    motion_service.setStiffnesses("LShoulderPitch", 0.0)
    motion_service.setStiffnesses("LShoulderRoll", 0.0)
    


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