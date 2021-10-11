import argparse
import numpy as np
import os
import matplotlib.pyplot as plt

from os.path import isfile, join

from numpy.lib.function_base import average

## class PlotAngles
#
# loads a list of csv files from the specified folder (path) and plot them using matplotlib
class PlotAngles:
    def __init__(self):
        # self.path = path
        self.folder = 'C:/Users/franc/Downloads/pepper_openpose_teloperation/pepper_teleoperation/angles_data'
        # self.folder = os.curdir
        # self.path = path

    
            
    ## method run
    #
    # load and plot data from the specified folder
    def run(self, files_list):
        av_errors = []
        for i, f in enumerate(files_list):
            data = np.loadtxt(self.path + '/' + f,
                            delimiter =", ")
            
            name = files_list[i]
            data_raw = data[0, :]
            data_filt = data[1, :]
            data_robot = data[2, :]
            time_samples = data[3, :]
            
            # Calculate error
            mean_square_error = np.square(np.subtract(data_raw, data_robot)).mean()
            # error = sum(abs((data_robot-data_raw)^2))/len(data_robot)
            # error = data_robot - data_raw
            # average_error = sum(error)/len(error)
            av_errors.append(mean_square_error)
            # av_errors.append(average_error)
        
        return av_errors 
        
    
    def start(self):
        
        self.list_fold = [f for f in os.listdir(self.folder)]
        av_errors_list = []
        for fold in self.list_fold:
            self.path =  "angles_data/" +fold
            
            # Loads list of files in the folder
            files_list = [f for f in os.listdir(self.path) if isfile(join(self.path, f)) and 'data' in f]
            files_list.reverse()
            
            errors_dict = self.run(files_list)
            av_errors_list.append(errors_dict)

        average_error_dict = {}
        
        for i in range(0, 9):
            temp_list = zip(*av_errors_list)[i]
            average_error_dict[files_list[i]] = sum(temp_list)/len(temp_list)
            
        print(average_error_dict)
             
        
if __name__ == '__main__':
    import argparse
    
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--path", type=str, default="05_07_2021_16-00-53",
    #                     help="Insert name of the folder where the angles are stored in a csv file in the 'angles_data' folder")

    # args = parser.parse_args()
    # path = "angles_data/" + args.path
    
    pa = PlotAngles()
    pa.start()
    
    
    
'''
# POWER SPECTRUM
fourier_transform = np.fft.rfft(data)
abs_fourier_transform = np.abs(fourier_transform)
power_spectrum = np.square(abs_fourier_transform)
frequency = np.linspace(0, sampling_rate/2, len(power_spectrum))
if len(frequency) == len(power_spectrum):
    axs[0].plot(frequency, power_spectrum)
    axs[0].set(xlabel='frequency [1/s]', ylabel='power')
    axs[0].set_title('Power Spectrum')
'''