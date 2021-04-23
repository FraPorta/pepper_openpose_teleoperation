import sys
from socket_receive import SocketReceive 

try:
    wp_dict = {}
    # initialize socket for receiving the 3D keypoints
    sr = SocketReceive()

    print("Start receiving keypoints...")
    while True:
        wp_dict = sr.receive_keypoints()
        print(wp_dict)

except Exception as e:
    print(e)
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(exc_type, exc_tb.tb_lineno)
    sys.exit(-1)
