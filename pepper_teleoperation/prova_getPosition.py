# -*- encoding: UTF-8 -*-

"""Example: Use getPosition Method"""

import qi
import argparse
import sys
import motion


def main(session):
    """
    This example uses the getPosition method.
    """
    # Get the service ALMotion.

    motion_service  = session.service("ALMotion")

    # Get transformation matrix with respect to Robot Torso frame
    frame           = motion.FRAME_TORSO
    useSensorValues = True
    
    name_hand       = "LWristYaw"
    a_t_T           = motion_service.getPosition(name_hand, frame, useSensorValues)
    print "Position of", name_hand, " in Torso is:"
    print a_t_T
    
    # Example showing how to get the position of the top camera
    name_head       = "HeadYaw"
    h_t_T           = motion_service.getPosition(name_head, frame, useSensorValues)
    print "Position of", name_head, " in Torso is:"
    print h_t_T


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