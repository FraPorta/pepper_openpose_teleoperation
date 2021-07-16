import numpy as np
import cv2 as cv
import glob
import pyautogui
import yaml
import os

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)
# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

# Specify resolution
resolution = (760, 435)
  
# create folder to store data
# Create folder to save keypoints if it does not exist 
# now = datetime.now()
# dt_string = now.strftime("%d_%m_%Y_%H-%M-%S")      
if not os.path.exists("video_data"):
    os.mkdir("video_data")
folder = "video_data/" + "calibration/"
if not os.path.exists(folder):
    os.mkdir(folder)

# Specify frames rate. We can choose any 
# value and experiment with it
fps = 15.0
count = 0

# images = glob.glob('*.jpg')
while count < 300:
    count += 1
    
    # Take screenshot using PyAutoGUI
    img = pyautogui.screenshot(region=(100, 20, 760, 435))
    img = np.array(img)
    
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    
    
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (7,6), None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners)
        # Draw and display the corners
        cv.drawChessboardCorners(img, (7,6), corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(1000)
cv.destroyAllWindows()

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# transform the matrix and distortion coefficients to writable lists
data = {'camera_matrix': np.asarray(mtx).tolist(),
        'dist_coeff': np.asarray(dist).tolist()}

# and save it to a file
with open(folder+"calibration_matrix.yaml", "w") as f:
    yaml.dump(data, f)
