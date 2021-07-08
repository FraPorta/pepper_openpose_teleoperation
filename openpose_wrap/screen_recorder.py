# importing the required packages
import pyautogui
import cv2
import numpy as np
from datetime import datetime
  
# Specify resolution
resolution = (760, 435)
  
# Specify video codec
codec = cv2.VideoWriter_fourcc(*"XVID")
  
# Specify name of Output file
now = datetime.now()
# dd/mm/YY H:M:S
dt_string = now.strftime("%d_%m_%Y_%H-%M-%S")
filename = dt_string +"_rec.avi"
  
# Specify frames rate. We can choose any 
# value and experiment with it
fps = 30.0
  
# Creating a VideoWriter object
# out = cv2.VideoWriter(filename, codec, fps, resolution)
  
# Create an Empty window
cv2.namedWindow("Live")
  
# Resize this window
# cv2.resizeWindow("Live", 480, 270)
  
while True:
    # Take screenshot using PyAutoGUI
    img = pyautogui.screenshot(region=(100, 20, 760, 435))

    # Convert the screenshot to a numpy array
    frame = np.array(img)
  
    # Convert it from BGR(Blue, Green, Red) to
    # RGB(Red, Green, Blue)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    #### Elaborate frame ####
    
    
    
    
    # Write it to the output file
    # out.write(frame)
      
    # Optional: Display the recording screen
    cv2.imshow('Live', frame)
      
    # Stop recording when we press 'q'
    if cv2.waitKey(1) == ord('q'):
        break
  
# Release the Video writer
# out.release()
  
# Destroy all windows
cv2.destroyAllWindows()