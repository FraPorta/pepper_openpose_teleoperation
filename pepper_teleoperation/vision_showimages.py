"""Example: Get an image. Display it and save it using PIL."""

import qi
import argparse
import sys
import time
import cv2
import numpy as np
import math
from naoqi import ALProxy
import vision_definitions



def main(session, ip_addr, port):
    try:
        """
        First get an image, then show it on the screen with PIL.
        """
        # Get the service ALVideoDevice.
        video_service = session.service("ALVideoDevice")

        cameraID = 0   # Top Camera
        resolution = vision_definitions.kQVGA  # 320 * 240
        colorSpace = vision_definitions.kBGRColorSpace
        # colorSpace = vision_definitions.kYUV422ColorSpace
        
        fps = 5
        
        videoClient = video_service.subscribe("python_client", resolution, colorSpace, fps)
        print "Client name: ", videoClient
        if videoClient != '':
            video_service.setParam(vision_definitions.kCameraSelectID, cameraID)

            userWantsToExit = False
            while not userWantsToExit:
                t0 = time.time()

                # x = threading.Thread(target=thread_function, args=(video_service, t0, videoClient))
                # x.start()
                
                # Get a camera image.
                # image[6] contains the image data passed as an array of ASCII chars.
                pepperImage = video_service.getImageRemote(videoClient)

                t1 = time.time()

                time_elapsed = float(t1 - t0)

                if time_elapsed > 0.0:
                    fps = 1/time_elapsed

                # Time the image transfer.
                print "Fps: %.2f" % fps

                # video_service.releaseImage(videoClient)

                if pepperImage is not None:
                    # Get the image size and pixel array.
                    imageWidth = pepperImage[0]
                    imageHeight = pepperImage[1]
                    img_array = pepperImage[6]
                    img_str = str(bytearray(img_array))
                    
                    video_service.releaseImage(videoClient)

                    # # Reshape array to show the image 
                    nparr = np.fromstring(img_str, np.uint8)
                    img_np = nparr.reshape(((imageHeight, imageWidth, 3))).astype(np.uint8)

                    scale_percent = 200 # percent of original size
                    width = int(img_np.shape[1] * scale_percent / 100)
                    height = int(img_np.shape[0] * scale_percent / 100)
                    dim = (width, height)

                    # resize image
                    img_np = cv2.resize(img_np, dim, interpolation = cv2.INTER_AREA)

                    # Write FPS on the
                    # cv2.putText(img_np, str(fps)+" FPS", (5, 15), cv2.FONT_HERSHEY_SIMPLEX , 0.5, (20, 200, 15), 2, cv2.LINE_AA) # Write FPS on image

                    # # Show the image with cv2
                    cv2.imshow("Pepper camera", img_np)
                    key = cv2.waitKey(1)
                    # If user press Esc, exit from the loop
                    if key == 27:
                        userWantsToExit = False

            # Unsubscribe from the video service
            video_service.unsubscribe(videoClient)

        else: 
            print("Video client not found.")
    except KeyboardInterrupt:
        # Unsubscribe from the video service
        video_service.unsubscribe(videoClient)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="130.251.13.109",
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