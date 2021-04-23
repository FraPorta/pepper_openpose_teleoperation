#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Use angleInterpolationWithSpeed Method"""

import qi
import argparse
import sys
import time
import almath


def main(session):
    """
    This example uses the angleInterpolationWithSpeed method,
    more precisely, its effect on reactivity.
    """
    # Get the service ALMotion.

    motion_service  = session.service("ALMotion")

    motion_service.setStiffnesses("Head", 1.0)

    # Head Start to zeros
    names             = "Head"
    targetAngles      = [0.0, 0.0]
    maxSpeedFraction  = 0.2 # Using 20% of maximum joint speed
    motion_service.angleInterpolationWithSpeed(names, targetAngles, maxSpeedFraction)

    # Example showing a reactive control with time function angleInterpolation
    # Goal: after 1.0 second, retarget from 20 to 50 degree: smooth transition

    # Interpolate the head yaw to 20 degrees in 2.0 seconds
    # With _async=True, angleInterpolation become non-blocking
    names      = "HeadYaw"
    angleLists = 20.0*almath.TO_RAD
    timeLists  = 2.0
    isAbsolute = True
    motion_service.angleInterpolation(names, angleLists, timeLists, isAbsolute, _async=True)
    time.sleep(0.5)

    # Call getTaskList to have the previous angleInterpolation task number
    taskList = motion_service.getTaskList()

    # Prepare the next target to 50.0 degrees in 1.0 second
    angleLists = 50.0*almath.TO_RAD
    timeLists  = 1.0
    motion_service.angleInterpolation(names, angleLists, timeLists, isAbsolute, _async=True)
    time.sleep(0.5)

    # Kill the first angleInterpolation (go to 20.0 degrees), the second start
    # smoothly from the current joint position and velocity (go to 50 degrees)
    motion_service.killTask(taskList[0][1])

    time.sleep(2.0)
    motion_service.setStiffnesses("Head", 0.0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
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
