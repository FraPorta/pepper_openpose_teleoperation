# Pepper Teleoperation using OpenPose
## Description
This repository contains the python code to use the Softbank Robotics Humanoid Robot Pepper to approach a user and then be teleoperated by an operator using Openpose for human pose estimation through the RGB camera of a Kinect v2 and the Kinect Depth Camera to add the third dimension to the estimated skeleton. From the 3D keypoints the joint angles are calculated and used as control input for the robot motors. A real-time butterworth filter is used for smoothing the control signals.
<!-- A video of the framework in action can be found at [this link](https://youtu.be/XeFq2MnqKOw) -->
Here you can find a video showing the framework in action:
<!-- <video src='https://youtu.be/XeFq2MnqKOw' width=180/> -->
[<img src="https://img.youtube.com/vi/XeFq2MnqKOw/maxresdefault.jpg" width="70%">](https://youtu.be/XeFq2MnqKOw)

## Installation guide
* OpenPose [prerequisites](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/installation/1_prerequisites.md):
    * Windows 10 (For this implementation)
    * Cmake-GUI
    * Visual Studio 2019 Enterprise (Version 16.8.6)
    * CUDA 11.1.1
    * Cudnn 8.0.5 (CUDA 11.1 compatible)
    * Python 3.7
* OpenPose [installation](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/installation/0_index.md#compiling-and-running-openpose-from-source)
* Kinect V2
    * [SDK v2.0](https://www.microsoft.com/en-us/download/details.aspx?id=44561)
    * [Pykinect2](https://github.com/Kinect/PyKinect2) python modules installation:
        ```bash
        pip install comtypes==1.1.4
        ```
        ```bash
        pip install numpy
        ```
        ```bash
        pip install pykinect2
        ```
    * Install matplotlib 
        ```bash
        pip install matplotlib
        ```
     * Install pyzmq for inter process communication
        ```bash
        pip install pyzmq
        ```
        
        It is recommended to substitute the `PyKinect2.py` and `PyKinectRuntime.py` files in the pykinect2 libraries inside your python installation with the updated ones form the [github repository](https://github.com/Kinect/PyKinect2) because the pip installer is not updated to the last version 
* Pepper teleoperation
    * Install `Python 2.7 32-bit` (Recommended: [miniconda2](https://repo.anaconda.com/miniconda/Miniconda2-latest-Windows-x86.exe))
    * Install numpy on Python 2.7
        ```bash
        pip install numpy
        ```
    * Install scipy on Python 2.7
        ```bash
        pip install pyzmq
        ```
    * Install matplotlib on Python 2.7
        ```bash
        pip install matplotlib
        ```
    * Install naoqi [Python SDK](https://developer.softbankrobotics.com/pepper-2-5/downloads/pepper-naoqi-25-downloads-windows).\
    Extract and copy the libraries in the folder `libs` of your `Python 2.7 32-bit` installation directory (inside the miniconda2 directory if you use it)

## Run the system
* To start the openpose 3D keypoints detection:
    * Connect the kinect v2 to a USB 3.0 port
    * Run `op_depth_keypoints.py` (in `openpose_wrap` folder)
        ```bash
        cd ~/pepper_openpose_teleoperation/openpose_wrap
        python op_depth_keypoints.py
        ```

* To visualize live 3D human pose with `matplotlib`:
    * In another terminal  run `get_and_plot_3Dkeypoints.py` (in `openpose_wrap` folder)
        ```bash
        cd ~/pepper_openpose_teleoperation/openpose_wrap
        python get_and_plot_3Dkeypoints.py
        ```

* Pepper real-time teleoperation after finding and approaching the user using GUI and voice controls
    * Open another terminal using `Python 2.7 32-bit` (see [miniconda2](https://repo.anaconda.com/miniconda/Miniconda2-latest-Windows-x86.exe))
    * Run `pepper_gui.py` (in `pepper_teleoperation` folder)
    * Insert the IP of your Pepper robot
    * Connect to the robot pressing the button or saying 'Connect'
    * Use the GUI buttons for approaching the user or teleoperate the robot
    * You can press the buttons also by talking (Say what is written on the button)
    * After pressing 'Start talking', the robot will repeat all the things you say, except if it recognize one of the possible commands:
        * 'move forward'
        * 'move backwards'
        * 'move right'
        * 'move left'
        * 'rotate left'
        * 'rotate right'
        * 'stop talking'
        * 'start moving'
        * 'stop moving'
        * 'watch right'
        * 'watch left' 
        * 'watch up'
        * 'watch down'
        * 'watch ahead'
        * 'track arm'
        * 'track user'

## Visualize plots of the angles of a teleoperation session
* Run `plot_angles.py` (in `pepper_teleoperation` folder)
```bash
        cd ~/pepper_openpose_teleoperation/pepper_teleoperation
        python plot_angles.py --path <name of the folder where the angles are stored inside the angles_data folder> 
```
       

<!-- ## Visualize Pepper cameras
[Original guide.](https://groups.google.com/g/ros-sig-aldebaran/c/LhmKTxyTn1Y?pli=1)
* Set Autonomous life to Off on Pepper web page 
* Install [gstreamer](https://gstreamer.freedesktop.org/) on Windows (tested with version 1.10)
* [Connect to Pepper ssh](http://doc.aldebaran.com/2-4/dev/tools/opennao.html) to start the video stream using gstreamer to create an UDP (+RTP) stream of the front (/dev/video0) and bottom (/dev/video1) camera from Pepper, the stream is then retrieved on the PC_HOST. -->

<!-- 
    PEPPER <- (UDP + RTP jpeg payload encoding) -> PC_HOST
    Front camera:
    ```bash
    gst-launch-0.10 -v v4l2src device=/dev/video0 ! 'video/x-raw-yuv,width=640, height=480,framerate=30/1' ! ffmpegcolorspace ! jpegenc, quality=10 ! rtpjpegpay ! udpsink host=PC_HOST port=3000
    ```
    Bottom camera:
    ```bash
     gst-launch-0.10 -v v4l2src device=/dev/video1 ! 'video/x-raw-yuv,width=640, height=480,framerate=5/1' ! ffmpegcolorspace ! jpegenc, quality=10 ! rtpjpegpay ! udpsink host=PC_HOST port=3001
    ```
* On Windows PowerShell run:
    To visualize the front camera:
    ```bash
    .\gst-launch-1.0 -v udpsrc port=3000 caps="application/x-rtp, encoding-name=(string)JPEG, payload=26" ! rtpjpegdepay ! jpegdec ! autovideosink sync=f
    ```
    Bottom camera:
    ```bash
    .\gst-launch-1.0 -v udpsrc port=3001 caps="application/x-rtp, encoding-name=(string)JPEG, payload=26" ! rtpjpegdepay ! jpegdec ! autovideosink sync=f
    ```
-->


## Stream mini IP camera
Pepper cameras are low resolution and streaming video while teleoperating its motors is a challenging task for its hardware, so we decided to install external battery-powered wireless IP cameras to get the live video streaming from Pepper while teleoperating it from another room.
Another IP camera will be installed on Pepper arm to visualize a more specific part of the scenary  
* Download [ONFIV Device Manager](https://sourceforge.net/projects/onvifdm/) 
* Get the rtsp stream URL of your IP camera (rtsp://...) (if it's connected to the same Wi-Fi network of your PC)
* Download [PMPlayer](https://www.picomixer.com/PMPlayer.html)
* Click on 'Open URL'
* Insert video stream URL and play
    
   
