import cv2
import numpy as np
import time

from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectV2
from pykinect2 import PyKinectRuntime
# local imports
from pykinect_lib.map_functions import *
import pykinect_lib.utils_PyKinectV2 as utils

#############################
### Kinect runtime object ###
#############################
kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color |
                                         PyKinectV2.FrameSourceTypes_Depth )

depth_width, depth_height = kinect.depth_frame_desc.Width, kinect.depth_frame_desc.Height # Default: 512, 424
color_width, color_height = kinect.color_frame_desc.Width, kinect.color_frame_desc.Height # Default: 1920, 1080


while True:
    ##############################
    ### Get images from camera ###
    ##############################
    if kinect.has_new_color_frame() and \
       kinect.has_new_depth_frame():
        
        # extract depth point
        #depth_point = color_point_2_depth_point(kinect, _DepthSpacePoint, kinect._depth_frame_data, color_point)
        
        color_frame      = kinect.get_last_color_frame()
        depth_frame      = kinect.get_last_depth_frame()
        
        #########################################
        ### Reshape from 1D frame to 2D image ###
        #########################################
        color_img        = color_frame.reshape(((color_height, color_width, 4))).astype(np.uint8)
        depth_img        = depth_frame.reshape(((depth_height, depth_width))).astype(np.uint16) 
        
        # extract depth point
        depth_point = color_point_2_depth_point(kinect, _DepthSpacePoint, kinect._depth_frame_data, color_point)
        #for j in range(0,1080):
        #    color_point = [500,j]

        ###############################################
        ### Useful functions in utils_PyKinectV2.py ###
        ###############################################
        # align_color_img = utils.get_align_color_image(kinect, color_img)
        
        

        ######################################
        ### Display 2D images using OpenCV ###
        ######################################
        color_img_resize = cv2.resize(color_img, (0,0), fx=0.5, fy=0.5) # Resize (1080, 1920, 4) into half (540, 960, 4)
        depth_colormap   = cv2.applyColorMap(cv2.convertScaleAbs(depth_img, alpha=255/2000), cv2.COLORMAP_JET) # Scale to display from 0 mm to 1500 mm
        
        cv2.imshow('color', color_img_resize)                       # (540, 960, 4)
        #cv2.imshow('align color with depth image', align_color_img) # (424, 512)
        cv2.imshow('depth', depth_colormap)                         # (424, 512)
        cv2.imshow('depth original', depth_img)

    key = cv2.waitKey(30)
    if key==27: # Press esc to break the loop
        break

kinect.close()
cv2.destroyAllWindows()