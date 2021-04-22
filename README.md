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
        *  ```bash
            pip install comtypes==1.1.4
            ```
        *   ```bash
            pip install numpy
            ```
        *   ```bash
            pip install pykinect2
            ```
            You should substitute the PyKinect2.py and PyKinectRuntime.py files with the updated ones form the [github repository](https://github.com/Kinect/PyKinect2)

