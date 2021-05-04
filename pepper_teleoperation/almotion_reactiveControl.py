#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Use setAngles and setStiffnesses Methods"""

import qi
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

    motion_service.setStiffnesses("Head", 1.0)

    # Example simulating reactive control
    names = "HeadYaw"
    angles = 0.3
    fractionMaxSpeed = 0.1
    motion_service.setAngles(names,angles,fractionMaxSpeed)
    # wait half a second
    time.sleep(0.5)
    # change target
    angles = 0.0
    motion_service.setAngles(names,angles,fractionMaxSpeed)
    # wait half a second
    time.sleep(0.5)
    # change target
    angles = 0.1
    motion_service.setAngles(names,angles,fractionMaxSpeed)

    time.sleep(3.0)
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