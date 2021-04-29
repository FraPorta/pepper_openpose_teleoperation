import sys

from socket_receive import SocketReceive

import numpy as np

# Body parts associated to their index
body_mapping = {
    '0':  "Nose", 
    '1':  "Neck", 
    '2':  "RShoulder",
    '3':  "RElbow",
    '4':  "RWrist",
    '5':  "LShoulder",
    '6':  "LElbow",
    '7':  "LWrist",
    '8':  "MidHip"
    }
## function vector_from_points
#
# calculate 3D vector from two points (vector = P2 - P1)
def vector_from_points(P1, P2):
    vector = [P2[0] - P1[0], P2[1] - P1[1], P2[2] - P1[2]]
    return vector

def obtain_LShoulderPitchRoll_angles(P1, P5, P6, P8):
    # Construct 3D vectors (bones) from points
    v_1_5 = vector_from_points(P1, P5)
    v_5_1 = vector_from_points(P5, P1)
    v_6_5 = vector_from_points(P6, P5)
    v_5_6 = vector_from_points(P5, P6)

    

    # Left torso X axis 
    n_1_5_6 = np.cross(v_1_5, v_6_5)

    # Left torso Z axis
    v_8_1 = vector_from_points(P8, P1)

    # Calculate normal of the 8_1_5 plane
    n_8_1_5 = np.cross(v_8_1, v_5_1)

    # Left torso Y axis
    R_left_torso = np.cross(v_8_1, n_8_1_5)

    

    # Intermediate angle to calculate positive or negative final Pitch angle
    intermediate_angle = np.arccos(np.dot(v_5_6, v_8_1) / (np.linalg.norm(v_5_6))*(np.linalg.norm(v_8_1)))
    
    # Module of the LShoulderPitch angle
    theta_LSP_module = np.arccos(np.dot(v_8_1, np.cross(R_left_torso, v_5_6))/(np.linalg.norm(v_8_1) * np.linalg.norm(np.cross(R_left_torso, v_5_6))))

    # Positive or negative LShoulderPitch
    if intermediate_angle <= np.pi/2 :
        LShoulderPitch = -theta_LSP_module
    else:
        LShoulderPitch = theta_LSP_module

    print("Pitch:")
    print((LShoulderPitch * 180 )/ np.pi)

    # Formula for LShoulderRoll
    LShoulderRoll = (np.pi/2) - np.arccos((np.dot(v_5_6, R_left_torso)) / (np.linalg.norm(v_5_6) * np.linalg.norm(R_left_torso)))

    print("Roll:")
    print((LShoulderRoll * 180)/ np.pi)

    return LShoulderPitch, LShoulderRoll

def obtain_LShoulderRoll_angle():
    LShoulderRoll = 0
    return LShoulderRoll

def obtain_LElbowYaw_angle():
    LElbowYaw = 0
    return LElbowYaw

def obtain_LElbowRoll_angle():
    LElbowRoll = 0
    return LElbowRoll

def obtain_RShoulderPitch_angle():
    RShoulderPitch = 0
    return RShoulderPitch

def obtain_RShoulderRoll_angle():
    RShoulderRoll = 0
    return RShoulderRoll

def obtain_RElbowYaw_angle():
    RElbowYaw = 0
    return RElbowYaw

def obtain_RElbowRoll_angle():
    RElbowRoll = 0
    return RElbowRoll

try:
    # Init dictionary
    wp_dict = {}

    # initialize socket for receiving the 3D keypoints
    sr = SocketReceive()

    # LShoulderPitch and LShoulderRoll needed keypoints
    LS = ['1','5','6','8']

    # LElbowYaw and LElbowRoll needed keypoints
    LE = ['1','5','6','7']

    # RShoulderPitch and RShoulderRoll needed keypoints
    RS = ['1','2','3','8']

    # RElbowYaw and RElbowRoll needed keypoints
    RE = ['1','2','3','4']   

    print("Start receiving keypoints...")
    while True:
        # Receive keypoints from socket
        wp_dict = sr.receive_keypoints()
        # print(wp_dict)

        # LShoulder angles
        if all (body_part in wp_dict for body_part in LS):        
            LShoulderPitch, LShoulderRoll = obtain_LShoulderPitchRoll_angles(wp_dict.get(LS[0]), wp_dict.get(LS[1]), wp_dict.get(LS[2]), wp_dict.get(LS[3]))
            # LShoulderRoll = obtain_LShoulderRoll_angle(wp_dict.get(LS[0]), wp_dict.get(LS[1]), wp_dict.get(LS[2]), wp_dict.get(LS[3]))

        # # LElbow angles
        # if all (body_part in wp_dict for body_part in LE):
        #     LElbowYaw = obtain_LElbowYaw_angle()
        #     LElbowRoll = obtain_LElbowRoll_angle()
        
        # # RShoulder angles
        # if all (body_part in wp_dict for body_part in RS):        
        #     RShoulderPitch = obtain_RShoulderPitch_angle()
        #     RShoulderRoll = obtain_RShoulderRoll_angle()

        # # RElbow angles
        # if all (body_part in wp_dict for body_part in RE):
        #     RElbowYaw = obtain_RElbowYaw_angle()
        #     RElbowRoll = obtain_RElbowRoll_angle()
                

except Exception as e:
    print(e)
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(exc_type, exc_tb.tb_lineno)
    sys.exit(-1)
