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
* Pepper teleoperation
    * Install `Python 2.7 32-bit` (Recommended: [miniconda2](https://repo.anaconda.com/miniconda/Miniconda2-latest-Windows-x86.exe)
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
* Pepper real-time teloperation
    * Open another terminal using `Python 2.7 32-bit` (see [miniconda2](https://repo.anaconda.com/miniconda/Miniconda2-latest-Windows-x86.exe)
    * Run `pepper_armsReactiveControl_butter.py` (in `pepper_teleoperation` folder)
        ```bash
        cd ~/pepper_openpose_teleoperation/pepper_teleoperation
        python pepper_armsReactiveControl_butter.py --ip [your_Pepper_ip]
        ```
    * Set the flag --show_plots to true if you want to visualize the plots for the controlled joints angles when you stop the script
    
   