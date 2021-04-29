import sys

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from socket_receive import SocketReceive

import numpy as np


try:
    # Init dictionary
    wp_dict = {}

    # initialize socket for receiving the 3D keypoints
    sr = SocketReceive()

    # Create matplotlib figure
    fig = plt.figure(figsize=(10,8))
    ax = fig.add_subplot(111, projection='3d')

    # to run GUI event loop
    plt.ion()
    
    print("Start receiving keypoints...")
    while True:
        # Receive keypoints from socket
        wp_dict = sr.receive_keypoints()
        # print(wp_dict)
        if bool(wp_dict):
            # Extract keypoints from dictionary
            wp_list = list(wp_dict.values())
            wp_keys = list(wp_dict.keys())
            
            wp_arr = np.array(wp_list)
            #wp_keys = np.array(wp_keys)

            xs = wp_arr[:,0]
            zs = wp_arr[:,1]
            ys = wp_arr[:,2]
            c = 'r'
            m = 'o'
            
            # Clear current figure 
            plt.cla()
            
            # Plot 3D keypoints
            ax.scatter(xs, ys, zs, c=c, marker=m)
            
            # Set labels
            ax.set_xlabel('X Label')
            ax.set_ylabel('Z Label')
            ax.set_zlabel('Y Label')
            
            # Set axes limits
            ax.set_xlim(-1,1)
            ax.set_ylim(0.5,2)
            ax.set_zlim(-1,1)

            # Set point names
            for label, x, y, z in zip(wp_keys, xs, ys, zs):
                ax.text(x+0.02, y+0.02, z+0.02, label, fontsize='medium', color='black')

            # Update 3D plot
            plt.show()
            fig.canvas.draw()
            fig.canvas.flush_events()

except Exception as e:
    print(e)
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(exc_type, exc_tb.tb_lineno)
    sys.exit(-1)
