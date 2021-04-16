# From Python
# It requires OpenCV installed for Python
import sys
import cv2
import os
from sys import platform
import argparse
from pathlib import Path

# kinect libraries
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectV2
from pykinect2 import PyKinectRuntime
# local imports
from pykinect_lib.map_functions import *
import pykinect_lib.utils_PyKinectV2 as utils



def display(datums):
    datum = datums[0]
    cv2.imshow("OpenPose 1.7.0 - Tutorial Python API", datum.cvOutputData)
    key = cv2.waitKey(1)
    return (key == 27)

def displayInput(datums):
    datum = datums[0]
    cv2.imshow("Kinect Input Color Image", datum.cvInputData)
    key = cv2.waitKey(1)
    return (key == 27)


def getKeypoints(datums):
    # poseModel = op.PoseModel.BODY_25
    # print(op.getPoseBodyPartMapping(poseModel))
    # print(op.getPoseNumberBodyParts(poseModel))
    # print(op.getPosePartPairs(poseModel))
    # print(op.getPoseMapIndex(poseModel))
    
    datum = datums[0]
    # print("Body keypoints: \n" + str(datum.poseKeypoints))
    body_keypoints = datum.poseKeypoints
    # first point
    x = body_keypoints[0,0,0]
    y = body_keypoints[0,0,1]
    color = [int(x),int(y)]
    return color
    # print("Face keypoints: \n" + str(datum.faceKeypoints))
    # print("Left hand keypoints: \n" + str(datum.handKeypoints[0]))
    # print("Right hand keypoints: \n" + str(datum.handKeypoints[1]))

#def get_depth_point()

try:
    # Import Openpose (Windows/Ubuntu/OSX)
    home = str(Path.home())
    try:
        # Windows Import
        if platform == "win32":
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append(home + '/Downloads/openpose/build/python/openpose/Release');
            os.environ['PATH']  = os.environ['PATH'] + ';' + home + '/Downloads/openpose/build/x64/Release;' +  home + '/Downloads/openpose/build/bin;'
            import pyopenpose as op
        else:
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append('../../python');
            # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
            # sys.path.append('/usr/local/python')
            from openpose import pyopenpose as op
    except ImportError as e:
        print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
        raise e
    
    # Flags
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-display", action="store_true", help="Disable display.")
    args = parser.parse_known_args()

    # Custom Params (refer to include/openpose/flags.hpp for more parameters)
    params = dict()
    params["model_folder"] = "models/"          # specify folder where models are located
    params["net_resolution"] = "-1x256"         # select net resolution (necessary for low end graphic cards)
    params["camera"] = "1"                      # set '0' for webcam or '1' for kinect
    params["camera_resolution"] = "1920x1080"   # set camera resolution to the correct one for the kinect [comment if using webcam]
    params["number_people_max"] = "1"           # limit the number of recognized people to 1
     

    # Add others in path?
    for i in range(0, len(args[1])):
        curr_item = args[1][i]
        if i != len(args[1])-1: next_item = args[1][i+1]
        else: next_item = "1"
        if "--" in curr_item and "--" in next_item:
            key = curr_item.replace('-','')
            if key not in params:  params[key] = "1"
        elif "--" in curr_item and "--" not in next_item:
            key = curr_item.replace('-','')
            if key not in params: params[key] = next_item

    # Construct it from system arguments
    # op.init_argv(args[1])
    # oppython = op.OpenposePython()

    # Starting OpenPose
    opWrapper = op.WrapperPython(op.ThreadManagerMode.AsynchronousOut)
    opWrapper.configure(params)
    opWrapper.start()
    
    kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color |
                                             PyKinectV2.FrameSourceTypes_Depth )

    depth_width, depth_height = kinect.depth_frame_desc.Width, kinect.depth_frame_desc.Height # Default: 512, 424
    color_width, color_height = kinect.color_frame_desc.Width, kinect.color_frame_desc.Height # Default: 1920, 1080


    # Main loop
    userWantsToExit = False
    while not userWantsToExit:
        
        # Pop frame
        datumProcessed = op.VectorDatum()
        
        
        if opWrapper.waitAndPop(datumProcessed):
            if not args[0].no_display:
                
                # Display input image
                #userWantsToExit = displayInput(datumProcessed)
                # Display output image
                userWantsToExit = display(datumProcessed)
                
            if kinect.has_new_depth_frame():
                color_point = getKeypoints(datumProcessed)
                # extract depth point
                depth_point = color_point_2_depth_point(kinect, _DepthSpacePoint, kinect._depth_frame_data, color_point)
                print(depth_point)
                
            # printKeypoints(datumProcessed)
        else:
            break
except Exception as e:
    print(e)
    sys.exit(-1)