# importing the required packages
import pyautogui
import cv2
import os
import numpy as np
from datetime import datetime
  
# Specify resolution
resolution = (760, 435)
  
# Specify video codec
codec = cv2.VideoWriter_fourcc(*"XVID")
  
# create folder to store data
# Create folder to save keypoints if it does not exist 
now = datetime.now()
dt_string = now.strftime("%d_%m_%Y_%H-%M-%S")      
if not os.path.exists("video_data"):
    os.mkdir("video_data")
folder = "video_data/" + dt_string + "/"
os.mkdir(folder)

# Specify name of Output file
videoname = folder + "arm_rec.avi"
  
# Specify frames rate. We can choose any 
# value and experiment with it
fps = 15.0
  
# Creating a VideoWriter object
out = cv2.VideoWriter(videoname, codec, fps, resolution)
  
# Create an Empty window
cv2.namedWindow("Pepper Arm Camera")
  
# Resize this window
# cv2.resizeWindow("Live", 480, 270)

arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_100)
arucoParams = cv2.aruco.DetectorParameters_create()

# list to store the already found ids
found_ids = []

# dict to store the single marker info when found for the first time
marker_info = {}
# list to store the already found markers info
markers_list = []

highlight = {}
count = {}

while True:

    # Take screenshot using PyAutoGUI
    img = pyautogui.screenshot(region=(100, 20, 760, 435))

    # Convert the screenshot to a numpy array
    frame = np.array(img)
  
    # Convert it from BGR(Blue, Green, Red) to
    # RGB(Red, Green, Blue)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    #### Elaborate frame ####
    # detect ArUco markers in the input frame
    corners, ids, rejected = cv2.aruco.detectMarkers(frame, arucoDict, parameters = arucoParams)
    
    # verify *at least* one ArUco marker was detected
    if len(corners) > 0:
		# flatten the ArUco IDs list
        ids = ids.flatten()
        
		# loop over the detected ArUCo corners
        for (markerCorner, markerID) in zip(corners, ids):
            # extract the marker corners (which are always returned
            # in top-left, top-right, bottom-right, and bottom-left
            # order)
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners
            
            # convert each of the (x, y)-coordinate pairs to integers
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))

            # Update the list of already found marker IDs
            if not markerID in found_ids:
                found_ids.append(markerID)
                corn = [topRight, bottomRight, bottomLeft, topLeft]
                timestamp = datetime.now().strftime('%H:%M:%S.%f')
                
                marker_info['id']           = markerID
                marker_info['timestamp']    = timestamp
                marker_info['topRight']     = topRight
                marker_info['bottomRight']  = bottomRight
                marker_info['bottomLeft']   = bottomLeft
                marker_info['topLeft']      = topLeft
                
                markers_list.append(marker_info)
                marker_info = {} 
                
                highlight[markerID] = True
                count[markerID] = 0
            
            # if highlight:
            #     highlight_markers = [k for k,v in highlight.items() if v == True]
            
            if count[markerID] > 10:
                highlight[markerID] = False
                count[markerID] = 0
                
            if highlight[markerID]: 
                c = count[markerID]
                count[markerID] = c + 1  
                
                # draw the bounding box of the ArUCo detection
                cv2.line(frame, topLeft, topRight, (0, 255, 0), 4)
                cv2.line(frame, topRight, bottomRight, (0, 255, 0), 4)
                cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 4)
                cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 4)
            else:    
                # draw the bounding box of the ArUCo detection
                cv2.line(frame, topLeft, topRight, (255, 0, 0), 2)
                cv2.line(frame, topRight, bottomRight, (255, 0, 0), 2)
                cv2.line(frame, bottomRight, bottomLeft, (255, 0, 0), 2)
                cv2.line(frame, bottomLeft, topLeft, (255, 0, 0), 2)
            
            # compute and draw the center (x, y)-coordinates of the
            # ArUco marker
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)
            
            # draw the ArUco marker ID on the frame
            cv2.putText(frame, str(markerID),
                        (topLeft[0], topLeft[1] - 15),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)

    # Write it to the output file
    out.write(frame)
      
    # Optional: Display the recording screen
    cv2.imshow('Pepper Arm Camera', frame)
    
    # Stop recording when we press 'q'
    if cv2.waitKey(1) == ord('q'):
        break

# Release the Video writer
out.release()
  
# Destroy all windows
cv2.destroyAllWindows()

# Save data in a file
with open(folder + "markers.txt", "w") as textfile:
    textfile.write("Found markers:\n")
    # If markers were found save info in a file
    if markers_list:  
        for line in markers_list:
            textfile.write(str(line) + "\n")
    textfile.close()
  
