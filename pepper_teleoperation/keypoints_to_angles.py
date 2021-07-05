import sys

from socket_receive import SocketReceive

import numpy as np
import math

## class KeypointsToAngles
#
# This class contains methods to receive 3D keypoints and calculate skeleton joint angles  
class KeypointsToAngles:
    '''
    # Body parts associated to their index
    body_mapping = {'0':  "Nose", 
                    '1':  "Neck", 
                    '2':  "RShoulder",
                    '3':  "RElbow",
                    '4':  "RWrist",
                    '5':  "LShoulder",
                    '6':  "LElbow",
                    '7':  "LWrist",
                    '8':  "MidHip"}
    '''

    ##  method __init__
    #
    #   Initialization method 
    def __init__(self):
        # init start flag
        self.start_flag = True

        # initialize socket for receiving the 3D keypoints
        self.sr = SocketReceive()

        print("Start receiving keypoints...")
    
    ##  method __del__
    #
    #   delete class
    def __del__(self):
        self.stop_receiving()
        del self.sr

    ##  method stop_receiving
    #
    #   stop the receive keypoints loop
    def stop_receiving(self):
        self.start_flag = False

    ##  function vector_from_points
    #
    #   calculate 3D vector from two points ( vector = P2 - P1 )
    def vector_from_points(self, P1, P2):
        vector = [P2[0] - P1[0], P2[1] - P1[1], P2[2] - P1[2]]
        return vector

    ##  function obtain_LShoulderPitchRoll_angles
    # 
    #   Calculate left shoulder pitch and roll angles
    def obtain_LShoulderPitchRoll_angles(self, P1, P5, P6, P8):
        # Construct 3D vectors (bones) from points
        v_1_5 = self.vector_from_points(P1, P5)
        v_5_1 = self.vector_from_points(P5, P1)
        v_6_5 = self.vector_from_points(P6, P5)
        v_5_6 = self.vector_from_points(P5, P6)

        # # Calculate normal of the 1_5_6 plane
        # n_1_5_6 = np.cross(v_1_5, v_6_5)

        # Left torso Z axis
        v_8_1 = self.vector_from_points(P8, P1)

        # Left torso X axis 
        n_8_1_5 = np.cross(v_8_1, v_5_1)
        # n_8_1_5 = np.cross(v_5_1, v_8_1)

        # Left torso Y axis
        # R_left_torso = np.cross(v_8_1, n_8_1_5)
        R_left_torso = np.cross(n_8_1_5, v_8_1) # Left-right arm inverted

        x = np.dot(v_5_6, v_8_1) / (np.linalg.norm(v_5_6))*(np.linalg.norm(v_8_1))
        # Intermediate angle to calculate positive or negative final Pitch angle
        try:
            intermediate_angle = math.acos(x)
        except ValueError:
            intermediate_angle = np.pi/2
        # intermediate_angle = np.arccos(x, where=(abs(x)<1), out=np.full_like(x, np.pi/2))
        
        # Module of the LShoulderPitch angle
        x = np.dot(v_8_1, np.cross(R_left_torso, v_5_6))/(np.linalg.norm(v_8_1) * np.linalg.norm(np.cross(R_left_torso, v_5_6))) 
        try:
            theta_LSP_module = math.acos(x)
        except ValueError:
            theta_LSP_module = 0
        # theta_LSP_module = np.arccos(x, where=(abs(x)<1), out=np.full_like(x, 0))

        # Positive or negative LShoulderPitch
        if intermediate_angle <= np.pi/2 :
            LShoulderPitch = -theta_LSP_module
        else:
            LShoulderPitch = theta_LSP_module
    
        # Formula for LShoulderRoll
        # LShoulderRoll = (np.pi/2) - np.arccos((np.dot(v_5_6, R_left_torso)) / (np.linalg.norm(v_5_6) * np.linalg.norm(R_left_torso)))
        x = (np.dot(v_5_6, R_left_torso)) / (np.linalg.norm(v_5_6) * np.linalg.norm(R_left_torso))
        try:
            LShoulderRoll = math.acos(x) - (np.pi/2)
        except ValueError:
            LShoulderRoll = 0
        # LShoulderRoll =  np.arccos(x, where=(abs(x)<1), out=np.full_like(x, 0)) - (np.pi/2) # Left-right arm inverted
        
        # Return LShoulder angles
        return LShoulderPitch, LShoulderRoll
    
    ##  function obtain_RShoulderPitchRoll_angles
    # 
    #   Calculate right shoulder pitch and roll angles
    def obtain_RShoulderPitchRoll_angle(self, P1, P2, P3, P8):
        # Construct 3D vectors (bones) from points
        v_2_3 = self.vector_from_points(P2, P3)
        v_1_2 = self.vector_from_points(P1, P2)
        v_2_1 = self.vector_from_points(P2, P1)

        # Right torso Z axis
        v_8_1 = self.vector_from_points(P8, P1)
        # Right torso X axis
        n_8_1_2 = np.cross(v_8_1, v_1_2)
        # Right torso Y axis
        # R_right_torso = np.cross(v_8_1, n_8_1_2) 
        R_right_torso = np.cross(n_8_1_2,v_8_1) # Left-right arm inverted

        # # Normal to plane 1_2_3
        # n_1_2_3 = np.cross(v_2_3, v_2_1)

        # Module of the RShoulderPitch angle
        x = np.dot(v_8_1, np.cross(R_right_torso, v_2_3))/(np.linalg.norm(v_8_1) * np.linalg.norm(np.cross(R_right_torso, v_2_3)))
        try:
            theta_RSP_module = math.acos(x)
        except ValueError:
            theta_RSP_module = 0
        # theta_RSP_module = np.arccos(x, where=(abs(x)<1), out=np.full_like(x, 0))
        
        # Intermediate angle to calculate positive or negative final Pitch angle
        x = np.dot(v_2_3, v_8_1) / (np.linalg.norm(v_2_3))*(np.linalg.norm(v_8_1))
        try:
            intermediate_angle = math.acos(x)
        except ValueError:
            intermediate_angle = np.pi/2
        # intermediate_angle = np.arccos(x, where=(abs(x)<1), out=np.full_like(x, np.pi/2))

        # Positive or negative RShoulderPitch
        if intermediate_angle <= np.pi/2 :
            RShoulderPitch = - theta_RSP_module
        else:
            RShoulderPitch = theta_RSP_module

        # Formula for RShoulderRoll
        # RShoulderRoll =  (np.pi/2) - np.arccos((np.dot(v_2_3, R_right_torso)) / (np.linalg.norm(v_2_3) * np.linalg.norm(R_right_torso))) 
        x = (np.dot(v_2_3, R_right_torso)) / (np.linalg.norm(v_2_3) * np.linalg.norm(R_right_torso))
        try:
            RShoulderRoll = math.acos(x) - (np.pi/2)
        except ValueError:
            RShoulderRoll = np.pi/2
        # RShoulderRoll =  np.arccos(x, where=(abs(x)<1), out=np.full_like(x, 0)) - (np.pi/2) # Left-right arm inverted

        # Return RShoulder angles
        return RShoulderPitch, RShoulderRoll

    ##  function obtain_LElbowYawRoll_angle
    #   
    #   Calculate left elbow yaw and roll angles
    def obtain_LElbowYawRoll_angle(self, P1, P5, P6, P7):
        # Construct 3D vectors (bones) from points
        v_6_7 = self.vector_from_points(P6, P7)
        v_1_5 = self.vector_from_points(P1, P5)

        # Left arm Z axis
        v_6_5 = self.vector_from_points(P6, P5)
        # Left arm X axis
        # n_1_5_6 = np.cross(v_6_5, v_1_5) 
        n_1_5_6 = np.cross(v_1_5, v_6_5) # Right-Left arms inverted
        # Left arm Y axis
        R_left_arm = np.cross(v_6_5, n_1_5_6)

        # Normal of 5_6_7 plane
        n_5_6_7 = np.cross(v_6_5, v_6_7) 

        # Formula to calculate the module of LElbowYaw angle
        x = np.dot(n_1_5_6, n_5_6_7) / (np.linalg.norm(n_1_5_6) * np.linalg.norm(n_5_6_7))
        try:
            theta_LEY_module = math.acos(x)
        except ValueError:
            theta_LEY_module = 0
        # theta_LEY_module = np.arccos(x, where=(abs(x)<1), out=np.full_like(x, 0)) 

        # Intermediate angles to choose the right LElbowYaw angle
        x = np.dot(v_6_7, n_1_5_6) / (np.linalg.norm(v_6_7) * np.linalg.norm(n_1_5_6))
        try:
            intermediate_angle_1 = math.acos(x)
        except ValueError:
            intermediate_angle_1 = np.pi/2
        # intermediate_angle_1 = np.arccos(x, where=(abs(x)<1), out=np.full_like(x, np.pi/2))

        x = np.dot(v_6_7, R_left_arm) / (np.linalg.norm(v_6_7) * np.linalg.norm(R_left_arm))
        try:
            intermediate_angle_2 = math.acos(x)
        except ValueError:
            intermediate_angle_2 = np.pi/2
        # intermediate_angle_2 = np.arccos(x, where=(abs(x)<1), out=np.full_like(x, np.pi/2))

        # Choice of the correct LElbowYaw angle using intermediate angles values
        if intermediate_angle_1 <= np.pi/2:
            LElbowYaw = -theta_LEY_module 
        else:
            if intermediate_angle_2 > np.pi/2:
                LElbowYaw = theta_LEY_module 
            elif intermediate_angle_2 <= np.pi/2:
                LElbowYaw = theta_LEY_module - (2 * np.pi)

        # Formula for LElbowRoll angle
        x = np.dot(v_6_7, v_6_5) / (np.linalg.norm(v_6_7) * np.linalg.norm(v_6_5))
        try:
            LElbowRoll = math.acos(x) - np.pi
        except ValueError:
            LElbowRoll = 0
        # LElbowRoll = np.arccos(x, where=(abs(x)<1), out=np.full_like(x, 0)) - np.pi
        # print('Before', LElbowYaw*180/np.pi, LElbowRoll*180/np.pi)
        # Return LElbow angles
        return LElbowYaw, LElbowRoll

 
    ##  function obtain_RElbowYawRoll_angle
    # 
    #   Calculate right elbow yaw and roll angles
    def obtain_RElbowYawRoll_angle(self, P1, P2, P3, P4):
        # Construct 3D vectors (bones) from points
        v_3_4 = self.vector_from_points(P3, P4)
        v_1_2 = self.vector_from_points(P1, P2)

        # Left arm Z axis
        v_3_2 = self.vector_from_points(P3, P2)
        # Left arm X axis
        # n_1_2_3 = np.cross(v_3_2, v_1_2)  # -- OUT --
        n_1_2_3 = np.cross(v_1_2, v_3_2)    # -- IN --  Right-left arms inverted
        # Left arm Y axis
        R_right_arm = np.cross(v_3_2, n_1_2_3)

        # normal to the 2_3_4 plane
        n_2_3_4 = np.cross(v_3_2, v_3_4)
        # n_2_3_4 = np.cross(v_3_4, v_3_2)


        # Formula to calculate the module of RElbowYaw angle
        x = np.dot(n_1_2_3, n_2_3_4) / (np.linalg.norm(n_1_2_3) * np.linalg.norm(n_2_3_4))
        try:
            theta_REY_module = math.acos(x)
        except ValueError:
            theta_REY_module = 0
        # theta_REY_module = np.arccos(x, where=(abs(x)<1), out=np.full_like(x, 0))

        # Intermediate angles to choose the right RElbowYaw angle
        x = np.dot(v_3_4, n_1_2_3) / (np.linalg.norm(v_3_4) * np.linalg.norm(n_1_2_3))
        try:
            intermediate_angle_1 = math.acos(x)
        except ValueError:
            intermediate_angle_1 =  np.pi/2
        # intermediate_angle_1 = np.arccos(x, where=(abs(x)<1), out=np.full_like(x, np.pi/2))

        x = np.dot(v_3_4, R_right_arm) / (np.linalg.norm(v_3_4) * np.linalg.norm(R_right_arm))
        try:
            intermediate_angle_2 = math.acos(x)
        except ValueError:
            intermediate_angle_2 =  np.pi/2
        # intermediate_angle_2 = np.arccos(x, where=(abs(x)<1), out=np.full_like(x, np.pi/2))

        # Choice of the correct RElbowYaw angle using intermediate angles values
        if intermediate_angle_1 <= np.pi/2:
            RElbowYaw = -theta_REY_module
        else:
            if intermediate_angle_2 > np.pi/2:
                RElbowYaw = theta_REY_module
            elif intermediate_angle_2 <= np.pi/2:
                # RElbowYaw = -theta_REY_module + (2 * np.pi)
                RElbowYaw = theta_REY_module 
        
        # Formula for RElbowRoll angle
        x = np.dot(v_3_4, v_3_2) / (np.linalg.norm(v_3_4) * np.linalg.norm(v_3_2))
        try:
            RElbowRoll =  np.pi - math.acos(x)
        except ValueError:
            RElbowRoll =  0
        # RElbowRoll = np.pi - np.arccos(x, where=(abs(x)<1), out=np.full_like(x, 0))

        # print('Before', RElbowYaw*180/np.pi, RElbowRoll*180/np.pi)
        # Return RElbow angles
        return RElbowYaw, RElbowRoll
    
    ##  function obtain_HipPitch_angles
    # 
    #   Calculate right hip pitch angle
    def obtain_HipPitch_angles(self, P0_curr, P8_curr):
        # Calculate vector
        v_0_8_curr = self.vector_from_points(P0_curr, P8_curr)

        # Normals to axis planes
        n_YZ = [1, 0, 0]
        n_XZ = [0, 1, 0]
        n_XY = [0, 0, 1]

        # Project vectors on YZ plane
        v_0_8_curr_proj = v_0_8_curr - np.dot(v_0_8_curr, n_YZ)

        # Calculate HipPitch module
        # omega_HP_module = np.arccos((np.dot(v_0_8_prev_proj, v_0_8_curr_proj))/(np.linalg.norm(v_0_8_prev_proj) * np.linalg.norm(v_0_8_curr_proj)))
        x = (np.dot(n_XZ, v_0_8_curr_proj))/(np.linalg.norm(n_XZ) * np.linalg.norm(v_0_8_curr_proj))
        try:
            omega_HP_module =  math.acos(x)
        except ValueError:
            omega_HP_module =  0
        # omega_HP_module = np.arccos(x, where=(abs(x)<1), out=np.full_like(x, 0))

        # Intermediate vector and angle to calculate positive or negative pich
        x = np.dot(v_0_8_curr_proj, n_XY) / (np.linalg.norm(v_0_8_curr_proj) * np.linalg.norm(n_XY))
        try:
            intermediate_angle =  math.acos(x)
        except ValueError:
            intermediate_angle =  0
        # intermediate_angle = np.arccos(x, where=(abs(x)<1), out=np.full_like(x, 0))

        # Choose positive or negative pitch angle
        correction = 0.15
        if intermediate_angle > np.pi/2:
            HipPitch = np.pi - omega_HP_module - correction
        else:
            HipPitch = omega_HP_module - np.pi - correction
        
        return HipPitch
    
    
    ##  function invert_right_left
    #
    #   Invert left and right arm
    def invert_right_left(self, wp_dict):
        temp_dict = {}

        if '0' in wp_dict:
            temp_dict['0'] = wp_dict['0']
        if '1' in wp_dict:
            temp_dict['1'] = wp_dict['1']
        if '2' in wp_dict:
            temp_dict['5'] = wp_dict['2']
        if '3' in wp_dict:
            temp_dict['6'] = wp_dict['3']
        if '4' in wp_dict:
            temp_dict['7'] = wp_dict['4']

        if '5' in wp_dict:
            temp_dict['2'] = wp_dict['5']
        if '6' in wp_dict:
            temp_dict['3'] = wp_dict['6']
        if '7' in wp_dict:
            temp_dict['4'] = wp_dict['7']
        if '8' in wp_dict:
            temp_dict['8'] = wp_dict['8']
        
        # print(temp_dict)
        return temp_dict

    ##  method get_keypoints
    #
    #  retrieve keypoints from socket
    def get_keypoints(self):
        # Receive keypoints from socket
        wp_dict = self.sr.receive_keypoints()
        return wp_dict

    ##  method get_angles
    #
    #   Get angles from socket and calculate joint angles
    def get_angles(self, wp_dict):
        try:

            # LShoulderPitch and LShoulderRoll needed keypoints
            LS = ['1','5','6','8']

            # LElbowYaw and LElbowRoll needed keypoints
            LE = ['1','5','6','7']

            # RShoulderPitch and RShoulderRoll needed keypoints
            RS = ['1','2','3','8']

            # RElbowYaw and RElbowRoll needed keypoints
            RE = ['1','2','3','4']   

            # HipPitch needed keypoints
            HP = ['1', '8']    

            # Init angles
            LShoulderPitch = LShoulderRoll = LElbowYaw = LElbowRoll = RShoulderPitch = RShoulderRoll = RElbowYaw = RElbowRoll = HipPitch = None

            # Invert right arm with left arm
            wp_dict = self.invert_right_left(wp_dict) 

            # HipPitch angles 
            if all (body_part in wp_dict for body_part in HP):
                HipPitch = self.obtain_HipPitch_angles(wp_dict.get(HP[0]), wp_dict.get(HP[1]))

            # LShoulder angles 
            if all (body_part in wp_dict for body_part in LS):        
                LShoulderPitch, LShoulderRoll = self.obtain_LShoulderPitchRoll_angles(wp_dict.get(LS[0]), wp_dict.get(LS[1]), wp_dict.get(LS[2]), wp_dict.get(LS[3]))

            # LElbow angles
            if all (body_part in wp_dict for body_part in LE):
                LElbowYaw, LElbowRoll = self.obtain_LElbowYawRoll_angle(wp_dict.get(LE[0]), wp_dict.get(LE[1]), wp_dict.get(LE[2]), wp_dict.get(LE[3]))

            # RShoulder angles
            if all (body_part in wp_dict for body_part in RS):        
                RShoulderPitch, RShoulderRoll = self.obtain_RShoulderPitchRoll_angle(wp_dict.get(RS[0]), wp_dict.get(RS[1]), wp_dict.get(RS[2]), wp_dict.get(RS[3]))

            # RElbow angles
            if all (body_part in wp_dict for body_part in RE):
                RElbowYaw, RElbowRoll = self.obtain_RElbowYawRoll_angle(wp_dict.get(RE[0]), wp_dict.get(RE[1]), wp_dict.get(RE[2]), wp_dict.get(RE[3]))
            
            return LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, HipPitch
                
        # Catch exceptions
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            sys.exit(-1)
