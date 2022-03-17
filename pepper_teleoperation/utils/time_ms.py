import time
from keypoints_to_angles import KeypointsToAngles

def main():
    time_arr = []
    KtA = KeypointsToAngles()

    wp_dict = {'0': [0.14026252925395966, 0.4979947507381439, 1.5790001153945923], 
            '1': [0.11283310502767563, 0.30691930651664734, 1.6740000247955322],
            '2': [-0.03261782228946686, 0.310418963432312, 1.6680001020431519],
            '3': [-0.1515801101922989, 0.08435355871915817, 1.6770000457763672], 
            '4': [-0.19893579185009003, -0.026394914835691452, 1.4860000610351562], 
            '5': [0.2714358866214752, 0.3160605728626251, 1.7010000944137573],
            '6': [0.34075403213500977, 0.08414772897958755, 1.6770000457763672], 
            '7': [0.3948674499988556, -0.05517739802598953, 1.5040000677108765], 
            '8': [0.10609894245862961, -0.13485142588615417, 1.571000099182129]
            }
    
    for i in range(1000):
        start = time.time_ns() 
        # print(start)
        # Get angles from keypoints
        LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll,\
        RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll,\
        HipPitch = KtA.get_angles(wp_dict)
        
        end = time.time_ns()  
        print(f"Time: {(end - start)} ns")
        time_arr.append((end - start))

    average = sum(time_arr) / len(time_arr)
    
    print(f"Time taken is {average} ns")



if __name__ == '__main__':
    main()
    