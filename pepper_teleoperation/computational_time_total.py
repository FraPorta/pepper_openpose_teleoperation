import argparse
import numpy as np
import os
import matplotlib.pyplot as plt
import ast
import csv
from os.path import isfile, join

from datetime import datetime

from numpy.lib.function_base import average


## class PlotAngles
#
# loads a list of csv files from the specified folder (path) and plot them using matplotlib
class PlotAngles:
    def __init__(self, path):
        self.folder = 'C:/Users/franc/Downloads/pepper_openpose_teloperation/pepper_teleoperation/angles_data'
        # self.folder = os.curdir
        self.path = path

        
    
    ## method run
    #
    # load and plot data from the specified folder
    def run(self):
        # Loads list of files in the folder
        # keypoints_received = [f for f in os.listdir(self.path) if isfile(join(self.path, f)) and 'keypoints' in f][0]
        # timestamps_start_loop = [f for f in os.listdir(self.path) if isfile(join(self.path, f)) and 'start' in f][0]
        
        # print(keypoints_received)
        # print(timestamps_start_loop)
        
        keypoints_received = 'keypoints_received.txt'
        # timestamps_start_loop = 'timestamps_start_loop.csv'
        
        # times_start_loop = np.loadtxt(self.path + '/' + timestamps_start_loop, delimiter =", ", dtype=np.str)
        
        # with open(self.path + '/' + timestamps_start_loop) as csv_file:
        #     csv_reader = csv.reader(csv_file, delimiter=',')
        #     for row in csv_reader:
        #         timestamp_end = row
                
        timestamp_init = []
        with open(self.path + '/' + keypoints_received, 'r') as f:
            contents = f.read()
            lines = contents.splitlines()
            for line in lines:
                d = ast.literal_eval(line)
                timestamp_init.append(d['timestamp'])
                
            f.close()
        
        
        times_list = []
        for t  in timestamp_init:
            t1 = datetime.strptime(t, '%H:%M:%S.%f')
            times_list.append(t1)   
        
        sum_diff = 0.0
        difference = [j-i for i, j in zip(times_list[:-1], times_list[1:])]
        
        
        for i in difference:
            sum_diff += i.microseconds
            average = (sum_diff/len(difference))/1000

            
        print(str(average) + ' ms')    
        return average 
    
        
        
    def start(self):
        self.list_fold = [f for f in os.listdir(self.folder)]
        av = []
        for fold in self.list_fold:
            self.path =  "angles_data/" +fold
            av.append(self.run())
        
        min_cost = min(av)
        max_cost = max(av)
        final_average = sum(av)/len(av)
        
        print('Average computational time is: ' + str(final_average) + ' ms')
        print('Minimum average computational time is: ' + str(min_cost) + ' ms')
        print('Maximum average computational time is: ' + str(max_cost) + ' ms')
        
        
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, default="23_09_2021_17-04-43_Gera1",
                        help="Insert name of the folder where the angles are stored in a csv file in the 'angles_data' folder")

    args = parser.parse_args()
    path = "angles_data/" + args.path
    
    pa = PlotAngles(path)
    pa.start()