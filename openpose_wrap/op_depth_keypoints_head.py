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
import json
import time
from numpy.core.fromnumeric import size

# Kinect libraries
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectV2
from pykinect2 import PyKinectRuntime

# Local imports
from pykinect_lib.map_functions import *
import pykinect_lib.utils_PyKinectV2 as utils
from socket_send import SocketSend 

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

## function checkOcclusion
#
# check if a keypoint is occluded by something
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

## function get_head_pose
#
# calculate head pose using cv2 solvePnP
def get_head_pose(image_points, model_points, size=[1080,1920] ):
    
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


    (success, rotation_vector, translation_vector, inliers) = cv2.solvePnPRansac(model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_AP3P)
    
    if success:
        return rotation_vector
    else:
        return None

## function display
# 
# Display OpenPose output image
def display(datums, fps, frame):
    #datum = datums[0]
    color_img = datums.cvOutputData

    color_img = cv2.resize(color_img, (0,0), fx=0.65, fy=0.65) # Resize (1080, 1920, 4) into half (540, 960, 4)
    cv2.putText(color_img, str(fps)+" FPS", (5, 15), cv2.FONT_HERSHEY_SIMPLEX , 0.5, (20, 200, 15), 2, cv2.LINE_AA) # Write FPS on image
    cv2.putText(color_img, str(frame)+" frame", (5, 690), cv2.FONT_HERSHEY_SIMPLEX , 0.5, (20, 200, 15), 2, cv2.LINE_AA) # Write frames on image
    cv2.imshow("OpenPose 1.7.0", color_img)
    
    # check if the user wants to exit
    key = cv2.waitKey(1)
    return (key == 27)

## function displayDepthKeypoints
#
# display keypoints on depth image and calculate and send the camera frame 3D points to a socket publisher
def displayDepthKeypoints(datums, depth_frame, fps, frame, display):
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
        
        head_keys = ['0','15','16','17','18']
        head_dict = {}
        color_dict = {}
        
        # initialize variables
        color_point = [0, 0]
        
        # Reshape from 1D frame to 2D image
        depth_img = depth_frame.reshape(((depth_height, depth_width))).astype(np.uint16) 
        
        if display:
            # Apply colormap to depth image
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_img, alpha=255/2000), cv2.COLORMAP_JET) # Scale to display from 0 mm to 2000 mm
        
        # proceed only if a person was detected
        if body_keypoints is not None:
            for i in range(0,19): # extract only the needed depth points (upper body limbs)
                if i not in range(9,15): # don't extract leg keypoints
                    x = body_keypoints[0,i,0]
                    y = body_keypoints[0,i,1]
                    score = body_keypoints[0,i,2]
                    
                    color_point = [int(x),int(y)]
                    
                    # check if the keypoint was detected (or the score is sufficiently high)
                    if color_point[0] > 0 and color_point[1] > 0 and score > 0.6: 
                    
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
                                wp_dict[i] = world_point
                                
                                if i == 0 or i in range(15,19):
                                    color_dict[i] = color_point
                                    head_dict[i] = world_point
                                    
        # Get head keypoints for head pose
        # head_dict = {key: wp_dict[key] for key in head_keys}
        if color_dict and head_dict:
            if len(color_dict) > 4:
                if 17 in color_dict:
                    del color_dict[17]
                    del head_dict[17]
                elif 18 in color_dict:
                    del color_dict[18]
                    del head_dict[18]
                    
            if len(color_dict) == 4:   
                image_points = np.array(list(color_dict.values()), dtype=np.double)
                model_points = np.array(list(head_dict.values()))
                try:
                    head_pose = get_head_pose(image_points, model_points)
                    
                    if head_pose is not None:
                        print("Head pose: ", head_pose*180/np.pi)
                        wp_dict[20] = [float(head_pose[0]), float(head_pose[1]), float(head_pose[1])] 
                except cv2.error as e:
                    print(e)
                
                
        # if more than three keypoints are detcted as occluded, it may be that the user
        # moved his whole body from one frame to another, so we reset the depth values dictionary 
        if ko_count > 3:
            dv_previous = {}
        # Else, save the depth values for the next loop and send the pose
        else:
            dv_previous = dv_dict
            
        # Send keypoints to another python script via socket (PUB/SUB)
            ss.send(wp_dict)

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
            # sys.path.append(home + '/openpose/build/python/openpose/Release');
            sys.path.append(home + '/Downloads/openpose/build/python/openpose/Release'); # MSI
            # os.environ['PATH']  = os.environ['PATH'] + ';' + home + '/openpose/build/x64/Release;' +  home + '/openpose/build/bin;'
            os.environ['PATH']  = os.environ['PATH'] + ';' + home + '/Downloads/openpose/build/x64/Release;' +  home + '/Downloads/openpose/build/bin;' # MSI
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
    params["model_folder"] = home + "/Downloads/openpose/models/"  # MSI
    # params["model_folder"] = home + '/openpose/models/'
    params["net_resolution"] = "-1x192"         # select net resolution (necessary for low end graphic cards)
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

    # Initialize time counter
    t1 = time.perf_counter()

    # Initialize frame counter
    frame = 0

    # Main loop
    userWantsToExit = False
    while not userWantsToExit:

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

                    fps = math.floor(1/float(time_elapsed))

                    # Map color space keypoints to depth space 
                    userWantsToExit = displayDepthKeypoints(datum, depth_frame, fps, frame, display=True)

                    # Display OpenPose output image
                    userWantsToExit = display(datum, fps, frame)
                    
            else:
                break
        
except Exception as e:
    print(e)
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(exc_type, exc_tb.tb_lineno)
    sys.exit(-1)
    


'''  
# Print keypoints with depth errors (0          -> keypoint not detected anymore
#                                    high value -> background point detcted instead of keypoint)
# These keypoints were discarded
if dv_dict.keys() != wp_dict.keys():
    set_dv = set(dv_dict.keys())
    set_wp = set(wp_dict.keys())
    missing_keypoints = set_dv - set_wp
    missing_keypoints = list(missing_keypoints)
    for i in missing_keypoints:
        print("Error detecting %s: depth value %i" % (body_mapping[i], dv_dict.get(i)))
'''