
# From Python
# It requires OpenCV installed for Python
import sys
import cv2
import os
from sys import platform
import argparse
from pathlib import Path

try:
    # Import Openpose (Windows/Ubuntu/OSX)
    home = str(Path.home())
    print(home)
    try:
        # Windows Import
        if platform == "win32":
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append(home + '/openpose/build/python/openpose/Release');
            os.environ['PATH']  = os.environ['PATH'] + ';' + home + '/openpose/build/x64/Release;' +  home + '/openpose/build/bin;'
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
    parser.add_argument("--image_path", default="../../../examples/media/COCO_val2014_000000000192.jpg", help="Process an image. Read all standard formats (jpg, png, bmp, etc.).")
    args = parser.parse_known_args()

    # Custom Params (refer to include/openpose/flags.hpp for more parameters)
    params = dict()
    params["model_folder"] = home + '/openpose/models/'
    # params["net_resolution"] = "-1x256"
    # kinect v2 as camera
    params["camera"] = "-1"
    params["camera_resolution"] = "1920x1080"

    
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
    '''
    poseModel = op.PoseModel.BODY_25
    print(op.getPoseBodyPartMapping(poseModel))
    body_mapping = op.getPoseBodyPartMapping(poseModel)
    print(body_mapping[0]) # out: Nose
    '''
    #print(op.getPoseNumberBodyParts(poseModel))
    #print(op.getPosePartPairs(poseModel))
    #print(op.getPoseMapIndex(poseModel))
    
    # Starting OpenPose
    opWrapper = op.WrapperPython(op.ThreadManagerMode.Synchronous)
    opWrapper.configure(params)
    opWrapper.execute()
    
    
except Exception as e:
    print(e)
    sys.exit(-1)
