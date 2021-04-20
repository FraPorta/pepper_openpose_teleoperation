# From Python
# It requires OpenCV installed for Python
import sys
import cv2
import os
from sys import platform
import argparse
from pathlib import Path
import numpy as np
import math
import matplotlib.pyplot as plt

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
    color_img = datum.cvOutputData
    color_img_resize = cv2.resize(color_img, (0,0), fx=0.5, fy=0.5) # Resize (1080, 1920, 4) into half (540, 960, 4)
    cv2.imshow("OpenPose 1.7.0", color_img_resize)
    
    key = cv2.waitKey(1)
    return (key == 27)

'''
def displayInput(datums):
    datum = datums[0]
    cv2.imshow("Kinect Input Color Image", datum.cvInputData)
    
    key = cv2.waitKey(1)
    return (key == 27)
'''

def getDepthKeypoints(datums):
    datum = datums[0]
    # get Body keypoints
    body_keypoints = datum.poseKeypoints
    
    # create dictionary for keypoints in depth/world coordinates
    wp_dict = {}
    dp_dict = {}
    dv_dict = {}
    
    if kinect.has_new_depth_frame():
        # get last depth frame
        depth_frame = kinect.get_last_depth_frame()
        
        # Reshape from 1D frame to 2D image
        depth_img = depth_frame.reshape(((depth_height, depth_width))).astype(np.uint16) 
        
        for i in range(1,8): # extract only the needed depth points (upper body limbs)
            x = body_keypoints[0,i,0]
            y = body_keypoints[0,i,1]
            color_point = [int(x),int(y)]
            
            # if color_point is not zero (The keypoint was not detected)
            if color_point[0] != 0 and color_point[1] != 0 : 
            
                # map color point to correspondent depth point  
                depth_point = color_point_2_depth_point(kinect, _DepthSpacePoint, kinect._depth_frame_data, color_point)
                
                if depth_point[0] < depth_height and depth_point[1] < depth_width:
                    if (not math.isinf(depth_point[0])) and (not math.isinf(depth_point[1])):
                        depth_value = depth_img[depth_point[1], depth_point[0]]
                        
                        # Add depth points and value to respective dictionaries
                        dp_dict[i] = depth_point
                        dv_dict[i] = depth_value
                        
                        # Map depth point to world point (x, y, z in meters in camera frame)
                        world_point = depth_point_2_world_point(kinect, _DepthSpacePoint, depth_point, depth_value) 
                        
                        if depth_value != 0:
                            # Add world point to the dictionary
                            wp_dict[i] = world_point
                
        # show keypoints on depth image
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_img, alpha=255/1500), cv2.COLORMAP_JET) # Scale to display from 0 mm to 1500 mm
        # draw markers for keypoints on depth image
        for i in dp_dict.keys():
            cv2.drawMarker(depth_colormap, (dp_dict[i][0], dp_dict[i][1]), (0,0,0), markerType=cv2.MARKER_SQUARE, markerSize=5, thickness=5, line_type=cv2.LINE_AA)
        # show image
        cv2.imshow('Depth image with keypoints', depth_colormap)
        
        # print(dp_dict)
        # print(dv_dict)
        print(wp_dict)
        
        '''
        data_list = list(wp_dict.values())
        data = np.array(data_list)
        for i in wp_dict.keys():
            xdata = data[:,0]
            ydata = data[:,1]
            zdata = data[:,2]
        
        ax.scatter3D(xdata, ydata, zdata, c=zdata, cmap='Greens');
        plt.show()
        '''
        
        key = cv2.waitKey(1)
        return (key == 27)
            
            

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
    #params["model_folder"] = "models/"          # specify folder where models are located
    params["model_folder"] = "C:/Users/franc/Downloads/pepper_openpose_teloperation/openpose_wrap/models/" 
    params["net_resolution"] = "-1x256"         # select net resolution (necessary for low end graphic cards)
    params["camera"] = "0"                      # 
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
    
    # starting kinect to acquire depth data
    kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Depth)

    # Starting OpenPose
    opWrapper = op.WrapperPython(op.ThreadManagerMode.AsynchronousOut)
    opWrapper.configure(params)
    opWrapper.start()
    #opWrapper.execute()
    
    depth_width, depth_height = kinect.depth_frame_desc.Width, kinect.depth_frame_desc.Height # Default: 512, 424
    color_width, color_height = kinect.color_frame_desc.Width, kinect.color_frame_desc.Height # Default: 1920, 1080

    # Main loop
    userWantsToExit = False
    while not userWantsToExit:
        
        # Pop frame
        datumProcessed = op.VectorDatum()
        
        if opWrapper.waitAndPop(datumProcessed):
            
            # map color space keypoints to depth space 
            # getDepthKeypoints(datumProcessed)
            
            if not args[0].no_display:
                # Display OpenPose output image
                userWantsToExit = display(datumProcessed)
                # Map color space keypoints to depth space 
                userWantsToExit = getDepthKeypoints(datumProcessed)
                
                    
        else:
            break
        
except Exception as e:
    print(e)
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(exc_type, exc_tb.tb_lineno)
    sys.exit(-1)