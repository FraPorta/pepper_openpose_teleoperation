#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Use getTransform Method"""

import qi
import argparse
import sys
import motion


def main(session):
    """
    This example uses the getTransform method.
    """
    # Get the services ALMotion & ALRobotPosture.

    motion_service  = session.service("ALMotion")

    # Example showing how to get the end of the right arm as a transform
    # represented in torso space. The result is a 4 by 4 matrix composed
    # of a 3*3 rotation matrix and a column vector of positions.
    # name  = 'RArm'
    # frame  = motion.FRAME_TORSO
    # useSensorValues  = True
    # result = motion_service.getTransform(name, frame, useSensorValues)
    # for i in range(0, 4):
    #     for j in range(0, 4):
    #         print result[4*i + j],
    #     print ''
    
    name  = 'HeadPitch'
    frame  = motion.FRAME_TORSO
    
    useSensorValues  = True
    result = motion_service.getTransform(name, frame, useSensorValues)
    for i in range(0, 4):
        for j in range(0, 4):
            print result[4*i + j],
        print ''


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="130.251.13.108",
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
