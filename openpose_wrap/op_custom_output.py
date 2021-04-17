# From Python
# It requires OpenCV installed for Python
import sys
import cv2
import os
from sys import platform
import argparse
from pathlib import Path
import numpy as np

# kinect libraries
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectV2
from pykinect2 import PyKinectRuntime
# local imports
from pykinect_lib.map_functions import *
import pykinect_lib.utils_PyKinectV2 as utils

# Result for BODY_25 (25 body parts consisting of COCO + foot)
#     {0,  "Nose"},
#     {1,  "Neck"},
#     {2,  "RShoulder"},
#     {3,  "RElbow"},
#     {4,  "RWrist"},
#     {5,  "LShoulder"},
#     {6,  "LElbow"},
#     {7,  "LWrist"},
#     {8,  "MidHip"},
#     {9,  "RHip"},
#     {10, "RKnee"},
#     {11, "RAnkle"},
#     {12, "LHip"},
#     {13, "LKnee"},
#     {14, "LAnkle"},
#     {15, "REye"},
#     {16, "LEye"},
#     {17, "REar"},
#     {18, "LEar"},
#     {19, "LBigToe"},
#     {20, "LSmallToe"},
#     {21, "LHeel"},
#     {22, "RBigToe"},
#     {23, "RSmallToe"},
#     {24, "RHeel"},
#     {25, "Background"}
# };



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


def getDepthKeypoints(datums):
    datum = datums[0]
    # print("Body keypoints: \n" + str(datum.poseKeypoints))
    body_keypoints = datum.poseKeypoints
    # first point
    
        
    if kinect.has_new_depth_frame():
        # get last depth frame
        depth_frame = kinect.get_last_depth_frame()
        
        # Reshape from 1D frame to 2D image
        depth_img = depth_frame.reshape(((depth_height, depth_width))).astype(np.uint16) 
            
        for i in range(0,7): # extract only the interesting depth points (upper body limbs)
            x = body_keypoints[0,i,0]
            y = body_keypoints[0,i,1]
            color_point = [int(x),int(y)]
            
            # if color_point is not zero (The keypoint was not detected)
            if color_point[0] != 0 and color_point[1] != 0 : 
            
                # extract depth point and correspondent depth value
                depth_point = color_point_2_depth_point(kinect, _DepthSpacePoint, kinect._depth_frame_data, color_point)
                print(depth_point)
                depth_value = depth_img[depth_point]
                print(depth_value) 
            
            


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
    
    # starting kinect to acquire depth data
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
                
            
                
            # printKeypoints(datumProcessed)
        else:
            break
except Exception as e:
    print(e)
    sys.exit(-1)