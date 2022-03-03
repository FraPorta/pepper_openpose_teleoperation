# From Python
# It requires OpenCV and Pykinect2 installed for Python
import sys
import cv2
import os
from sys import platform
import argparse
from pathlib import Path
import numpy as np
import math
import time
from datetime import datetime
from numpy.core.fromnumeric import size

# Kinect libraries
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectV2
from pykinect2 import PyKinectRuntime

# Local imports
from pykinect_lib.map_functions import *
import pykinect_lib.utils_PyKinectV2 as utils
from socket_send import SocketSend
from socket_receive import SocketReceiveSignal

# BODY_25 model keypoints (25 body parts consisting of COCO + foot)
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

depth_fps_counter = 0
color_fps_counter = 0
dv_previous = {}

##  function checkOcclusion
#
#   check if a keypoint is occluded by something
def checkOcclusion(bodyPart, prev_depths, current_depth):
    # threshShoulders = 50   # mm
    # threshElbows = 70      # mm
    threshShoulders = 80   # mm
    threshElbows = 90      # mm

    # new_depth = current_depth
    # Check if the keypoint is present in both dictionaries
    if bodyPart in prev_depths:
        diff = int(prev_depths.get(bodyPart)) - int(current_depth)
        # Case neck and shoulders
        if bodyPart == 1 or bodyPart == 2 or bodyPart == 5 or bodyPart == 15  or bodyPart == 16  or bodyPart == 17  or bodyPart == 18:
            # If the value is above the threshold ( the new keypoint is much closer to the camera ) the keypoint is occluded
            if diff > threshShoulders:
                # print("Body part occluded: %s" % body_mapping.get(bodyPart))
                # print("Difference (mm): %i" % diff)
                if diff > 1000:
                    return False
                else:
                    return True
        # Case elbows
        if bodyPart == 3 or bodyPart == 6:
            # If the value is above the threshold ( the new keypoint is much closer to the camera ) the keypoint is occluded
            if diff > threshElbows:
                # print("Body part occluded: %s" % body_mapping.get(bodyPart))
                # print("Difference (mm): %i" % diff)
                if diff > 1000:
                    return False
                else:
                    return True
    return False

## function store_keypoints
#
#  save the keypoints in a file with timestamp
def store_keypoints(wp_dict, filename):
    if wp_dict:
        temp_dict = wp_dict.copy()
        temp_dict['timestamp'] = datetime.now().strftime('%H:%M:%S.%f')
        file = filename + '/keypoints_sent.txt'
        # print(file)
        with open(file,'a') as f: 
            f.write(str(temp_dict))
            f.write("\n")

'''
##  function get_head_pose
#
#   calculate head pose using cv2 solvePnP
def get_head_pose(image_points, model_points, size=[1080,1920]):
    # Camera internals
    focal_length = size[1]
    center = (size[1]/2, size[0]/2)
    camera_matrix = np.array(
                            [[focal_length, 0, center[0]],
                            [0, focal_length, center[1]],
                            [0, 0, 1]], dtype = "double"
                            )

    dist_coeffs = np.zeros((4,1)) # Assuming no lens distortion
    # Works with 4
    # (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_P3P)
    # Get head rotation and translation vector 
    (success, rotation_vector, translation_vector) = cv2.solveP3P(model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_AP3P)

    if success:
        return rotation_vector, translation_vector
    else:
        return None
'''

##  function display
# 
#   Display OpenPose output image
def display(datums, fps, frame):
    #datum = datums[0]
    color_img = datums.cvOutputData
    
    color_img = cv2.resize(color_img, (0,0), fx=0.5, fy=0.5) # Resize (1080, 1920, 4) into half (540, 960, 4)
    cv2.putText(color_img, str(fps)+" FPS", (5, 15), cv2.FONT_HERSHEY_SIMPLEX , 0.5, (20, 200, 15), 2, cv2.LINE_AA) # Write FPS on image
    cv2.putText(color_img, str(frame)+" frame", (5, 690), cv2.FONT_HERSHEY_SIMPLEX , 0.5, (20, 200, 15), 2, cv2.LINE_AA) # Write frames on image
    cv2.imshow("OpenPose 1.7.0", color_img)
    
    # check if the user wants to exit
    key = cv2.waitKey(1)
    return (key == 27)

##  function displayDepthKeypoints
#
#   display keypoints on depth image and calculate and send the camera frame 3D points to a socket publisher
def displayDepthKeypoints(datums, depth_frame, fps, frame, filename,saveKeypoints, display):
    global dv_previous
    keypointOccluded = False
    
    # get Body keypoints
    body_keypoints = datums.poseKeypoints
    
    try:
        # create dictionary for keypoints in depth/world coordinates
        wp_dict = {}
        dp_dict = {}
        dv_dict = {}
        ko_count = 0
        
        # head_dict = {}
        # color_dict = {}
        
        # initialize variables
        color_point = [0, 0]
        
        # Reshape from 1D frame to 2D image
        depth_img = depth_frame.reshape(((depth_height, depth_width))).astype(np.uint16) 
        
        if display:
            # Apply colormap to depth image
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_img, alpha=255/2000), cv2.COLORMAP_JET) # Scale to display from 0 mm to 2000 mm
        
        # proceed only if a person was detected
        if body_keypoints is not None:
            for i in range(0,9): # extract only the needed depth points (upper body limbs)
                # if i not in range(9,15): # don't extract leg keypoints
                x = body_keypoints[0,i,0]
                y = body_keypoints[0,i,1]
                # score = body_keypoints[0,i,2]
                
                color_point = [int(x),int(y)]
                
                # check if the keypoint was detected 
                # if color_point[0] > 0 and color_point[1] > 0 and score > 0.6: 
                if color_point[0] > 0 and color_point[1] > 0:
                    # map color point to correspondent depth point  
                    depth_point = color_point_2_depth_point(kinect, _DepthSpacePoint, kinect._depth_frame_data, color_point)
                    
                    if depth_point[0] < depth_height and depth_point[1] < depth_width and not math.isinf(depth_point[0]) and not math.isinf(depth_point[1]):

                        # extract depth value from depth image
                        depth_value = depth_img[depth_point[1], depth_point[0]]

                        # Check if the keypoint is occluded
                        if dv_previous and depth_value > 0 and depth_value < 3000:
                            keypointOccluded = checkOcclusion(i, dv_previous, depth_value)

                        # If keypoint is occluded, mantain the previous depth
                        if keypointOccluded:
                            if i in dv_previous:
                                depth_value = dv_previous.get(i)
                                ko_count += 1
                        
                        # Add depth points and value to respective dictionaries
                        dp_dict[i] = depth_point
                        dv_dict[i] = depth_value
                        
                        if display:
                            # Draw keypoint on depth image
                            cv2.drawMarker(depth_colormap, (depth_point[0], depth_point[1]), (0,0,0), markerType=cv2.MARKER_SQUARE, markerSize=5, thickness=5, line_type=cv2.LINE_AA)

                        # Add world point to the dictionary if the depth value is not zero and not higher than 3 meters
                        if depth_value > 0 and depth_value < 3000:
                            # Map depth point to world point (x, y, z in meters in camera frame)
                            world_point = depth_point_2_world_point(kinect, _DepthSpacePoint, depth_point, depth_value) 
                            # wp_dict[i] = world_point
                            wp_dict[str(i)] = world_point
                            
                            # if i == 0 or i in range(15,17):
                            # # if i == 0 or i in range(15,19):
                            #     color_dict[i] = color_point
                            #     head_dict[i] = world_point
                
                
        # if more than three keypoints are detected as occluded, it may be that the user
        # moved his whole body from one frame to another, so we reset the depth values dictionary 
        if ko_count > 3:
            dv_previous = {}
        # Else, save the depth values for the next loop 
        else:
            dv_previous = dv_dict
            
        # Send keypoints to another python script via socket (PUB/SUB)
        ss.send(wp_dict)
        
        # Save keypoints in a file when are used to calculate angles for pepper joints
        if saveKeypoints:
            store_keypoints(wp_dict, filename)

        if display:
            # Write FPS on image
            cv2.putText(depth_colormap, str(fps)+" FPS", (5, 15), cv2.FONT_HERSHEY_SIMPLEX , 0.5, (20, 200, 15), 2, cv2.LINE_AA) 
            cv2.putText(depth_colormap, str(frame)+" frame", (5, 410), cv2.FONT_HERSHEY_SIMPLEX , 0.5, (20, 200, 15), 2, cv2.LINE_AA) 

            # Show depth image with markers
            cv2.imshow('Depth image with keypoints', depth_colormap)

        # Show image for at least 1 ms and check if the user wants to exit
        key = cv2.waitKey(1)
        return (key == 27)
        
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_tb.tb_lineno)
        sys.exit(-1)

try:
    # Import Openpose (Windows/Ubuntu/OSX)
    home = str(Path.home())
    try:
        # Windows Import
        if platform == "win32":
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append(home + '/openpose/build/python/openpose/Release');
            # sys.path.append(home + '/Downloads/openpose/build/python/openpose/Release'); # MSI
            os.environ['PATH']  = os.environ['PATH'] + ';' + home + '/openpose/build/x64/Release;' +  home + '/openpose/build/bin;'
            # os.environ['PATH']  = os.environ['PATH'] + ';' + home + '/Downloads/openpose/build/x64/Release;' +  home + '/Downloads/openpose/build/bin;' # MSI
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
    # Change path to point to the models folder 
    params["model_folder"] = home + '/openpose/models/'  
    # params["model_folder"] = home + "/Downloads/openpose/models/"  # MSI
    
    # params["net_resolution"] = "-1x192"         # select net resolution (necessary for low end graphic cards)
    # params["face"] = "true"
    # params["face_net_resolution"] = "240x240"
    # params["hand"] = "true"
    # params["hand_net_resolution"] = "256x256"
    # params["camera"] = "-1"                     # automatically select camera input (-1)
    # params["camera_resolution"] = "1920x1080"   # set camera resolution to the correct one for the kinect [comment if using webcam]
    params["number_people_max"] = "1"           # limit the number of recognized people to 1
    # params["process_real_time"] = "true"
    params["net_resolution_dynamic"] = "0"      # recommended 1 for small GPUs (to avoid out of memory"" 
                                                # errors but maximize speed) and 0 for big GPUs (for maximum accuracy and speed).");
                                                                                            
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

    # Starting Kinect to acquire depth and color data
    kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Depth)

    # Starting OpenPose
    opWrapper = op.WrapperPython(op.ThreadManagerMode.Asynchronous)
    opWrapper.configure(params)
    opWrapper.start()
    
    # Get dictionary for body parts mapping
    poseModel = op.PoseModel.BODY_25
    body_mapping = op.getPoseBodyPartMapping(poseModel)
    
    # Extract depth and color images width and height
    depth_width, depth_height = kinect.depth_frame_desc.Width, kinect.depth_frame_desc.Height # Default: 512, 424
    color_width, color_height = kinect.color_frame_desc.Width, kinect.color_frame_desc.Height # Default: 1920, 1080

    # Initialize socket to send keypoints
    ss = SocketSend()
    sr = SocketReceiveSignal()

    # Initialize time counter
    t1 = time.perf_counter()

    # Initialize frame counter
    frame = 0

    # Main loop
    userWantsToExit = False
    saveKeypoints = False
    filename = None
    
    # Create folder to save keypoints if it does not exist 
    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y_%H-%M-%S")      
    if not os.path.exists("keypoints_data"):
        os.mkdir("keypoints_data")
                
    while not userWantsToExit:
        # Check if the user is using the keypoints to control Pepper
        msg = sr.receive()
        
        # Check if the signal for recording or stop recording keypoints was received
        if msg == b'Start':
            now = datetime.now()
            dt_string = now.strftime("%d_%m_%Y_%H-%M-%S")
            filename = "keypoints_data/" + dt_string 
            os.mkdir(filename)
            saveKeypoints = True
        elif msg == b'Stop':
            saveKeypoints = False
        
        # When new color and depth frames are available elaborate them with Openpose
        if kinect.has_new_depth_frame() and kinect.has_new_color_frame():
            
            # Get Kinect last depth frame
            depth_frame = kinect.get_last_depth_frame()
            # Get Kinect last color frame
            color_frame = kinect.get_last_color_frame()

            # Reshape input color image
            color_img = color_frame.reshape(((color_height, color_width, 4))).astype(np.uint8)
           
            # Convert image to BGR to make it viable as OpenPose input
            color_img_bgr = cv2.cvtColor(color_img, cv2.COLOR_BGRA2BGR)

            # Instantiate OpenPose Datum object
            datum = op.Datum()

            # Use Kinect color image as InputData for OpenPose 
            datum.cvInputData = color_img_bgr

            # Proceed if OpenPose processed the frame 
            if opWrapper.emplaceAndPop(op.VectorDatum([datum])):
                if not args[0].no_display:

                    # Update frame number
                    frame += 1

                    # Calculate fps 
                    time_elapsed = time.perf_counter() - t1
                    t1 = time.perf_counter()

                    fps = round(1/float(time_elapsed),1)

                    # Map color space keypoints to depth space 
                    userWantsToExit = displayDepthKeypoints(datum, depth_frame, fps, frame, filename, saveKeypoints, display=False)

                    # Display OpenPose output image
                    userWantsToExit = display(datum, fps, frame)  
            else:
                break
# Catch exceptions    
except Exception as e:
    print(e)
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(exc_type, exc_tb.tb_lineno)
    sys.exit(-1)
    