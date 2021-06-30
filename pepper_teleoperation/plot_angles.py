import argparse
import numpy as np
import os
import matplotlib.pyplot as plt

from os.path import isfile, join

## class PlotAngles
#
# loads a list of csv files from the specified folder (path) and plot them using matplotlib
class PlotAngles:
    def __init__(self, path):
        self.path = path
        self.pos = {0: (0,0),
                    1: (0,1),
                    2: (0,2),
                    3: (1,0),
                    4: (1,1),
                    5: (1,2),
                    6: (2,0),
                    7: (2,1),
                    8: (2,2)}
    
        
    ##  function plot_data
    #
    #   Plot raw and filtered angles at the end of the session
    def plot_data(self, axs, raw_data, filt_data, robot_data, name, time_samples, pos):
        # Plot time signals (Raw and filtered)
        data = np.array(raw_data)
        
        if len(raw_data) > len(filt_data):
            filt_data.append(0.0)
        data_filt = np.array(filt_data)
        
        if len(raw_data) > len(robot_data):
            robot_data.append(0.0)
        data_robot = np.array(robot_data)
        
        if len(time_samples) == len(data):
            axs[pos[0], pos[1]].plot(time_samples, data)
            axs[pos[0], pos[1]].set(xlabel='time [s]', ylabel='Angle [rad]')
            axs[pos[0], pos[1]].set_title(name)
            
        if len(time_samples) == len(data_filt):
            axs[pos[0], pos[1]].plot(time_samples, data_filt)
            # axs[pos_x, pos_y].legend(['signal', 'filtered'])
        
        if len(time_samples) == len(data_robot):
            axs[pos[0], pos[1]].plot(time_samples, data_robot)
            axs[pos[0], pos[1]].legend(['signal', 'filtered', 'robot'])
            
    ## method run
    #
    # load and plot data from the specified folder
    def run(self):
        # Loads list of files in the folder
        files_list = [f for f in os.listdir(self.path) if isfile(join(self.path, f))]
        files_list.reverse()
        
        # Create figure with 12 subplots
        fig, axs = plt.subplots(3,3)
        fig.suptitle('Joints angles')

        for i, f in enumerate(files_list):
            data = np.loadtxt(self.path + '/' + f,
                            delimiter =", ")
            
            name = files_list[i]
            data_raw = data[0, :]
            data_filt = data[1, :]
            data_robot = data[2, :]
            time_samples = data[3, :]
            
            # Plot i-th joint angles
            self.plot_data(axs, data_raw, data_filt, data_robot, name, time_samples, self.pos.get(i))
        
        print("Showing angles plots, close to terminate the program.")
        plt.subplots_adjust(hspace=0.36)
        plt.show()
            
        
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, default="23_06_2021_17-30-45",
                        help="Insert name of the folder where the angles are stored in a csv file in the 'angles_data' folder")

    args = parser.parse_args()
    path = "angles_data/" + args.path
    
    pa = PlotAngles(path)
    pa.run()
    
    
    
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