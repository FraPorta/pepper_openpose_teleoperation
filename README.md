# Pepper Teleoperation using OpenPose
## Description

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

## Run the system
* To start the openpose 3D keypoints detection:
    * Connect the kinect v2 to a usb 3.0
    * Run `op_depth_keypoints.py`
        ```bash
        cd ~/pepper_openpose_teleoperation/openpose_wrap
        python op_depth_keypoints.py
        ```
* To visualize live 3D human pose:
    * In another terminal  run `get_and_plot_3Dkeypoints.py`
        ```bash
        cd ~/pepper_openpose_teleoperation/openpose_wrap
        python get_and_plot_3Dkeypoints.py
        ```
* Pepper
    * Install naoqi [Python SDK](https://developer.softbankrobotics.com/pepper-2-5/downloads/pepper-naoqi-25-downloads-windows)
   