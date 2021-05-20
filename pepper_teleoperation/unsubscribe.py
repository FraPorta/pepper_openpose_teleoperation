import qi
import argparse
import sys
import time
import numpy as np
import math
from naoqi import ALProxy
import vision_definitions


def main(session, ip_addr, port):
    # Get the service ALVideoDevice.
    # video_service = ALProxy("ALVideoDevice", ip_addr, port)
    video_service = session.service("ALVideoDevice")
    results = []
    results.append(video_service.unsubscribe("python_client_0"))
    results.append(video_service.unsubscribe("python_client_1"))
    results.append(video_service.unsubscribe("python_client_2"))
    results.append(video_service.unsubscribe("python_client_3"))
    results.append(video_service.unsubscribe("python_client_4"))
    results.append(video_service.unsubscribe("python_client_5"))
    results.append(video_service.unsubscribe("python_client_6"))

    print(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="130.251.13.120",
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
    main(session, args.ip, args.port)