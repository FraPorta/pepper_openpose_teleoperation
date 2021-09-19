import argparse
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy import signal

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
    def plot_data(self, axs, raw_data, name, sampling_rate):
        # Plot time signals (Raw and filtered)
        data = np.array(raw_data)
        # sampling_rate = len(time_samples)/time_samples[-1]
        fourier_transform = np.fft.rfft(data)
        abs_fourier_transform = np.abs(fourier_transform)
        power_spectrum = np.square(abs_fourier_transform)
        frequency = np.linspace(0, sampling_rate/2, len(power_spectrum))
        
        if len(frequency) == len(power_spectrum):
            axs.plot(frequency, power_spectrum)
            axs.set(xlabel='frequency [1/s]', ylabel='power')
            axs.set_title('Power Spectrum '+ name)
            
            
    ## method run
    #
    # load and plot data from the specified folder
    def run(self):
        # Loads list of files in the folder
        files_list = [f for f in os.listdir(self.path) if isfile(join(self.path, f)) and 'data' in f]
        
        files_list.reverse()
        
        # Create figure with 12 subplots
        fig, axs = plt.subplots(1,1)
        # fig.suptitle('Power spectrum of Butterworth filter')
        
         # Filter parameters 
        fs = 5.3            # sample rate, Hz
        nyq = 0.5 * fs      # Nyquist Frequency
        
        cutoff = 0.7        # desired cutoff frequency of the filter, Hz 
        order = 1           # filter order
        normal_cutoff = cutoff / nyq    # Cutoff freq for lowpass filter

        # Filter poles
        b, a = signal.butter(order, normal_cutoff, btype='low', analog=False, output='ba') 

        w, h = signal.freqs(b, a)
        plt.semilogx(w, 20 * np.log10(abs(h)))
        plt.title('Butterworth filter frequency response')
        plt.xlabel('Frequency [radians / second]')
        plt.ylabel('Amplitude [dB]')
        plt.margins(0, 0.1)
        plt.grid(which='both', axis='both')
        plt.axvline(normal_cutoff, color='green') # cutoff frequency
        plt.show()
        
        
        print("Showing angles plots, close to terminate the program.")
        # plt.xlim([-0.01, 0.8])
        # plt.subplots_adjust(hspace=0.36)
        # plt.show()
            
        
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, default="17_09_2021_15-28-18__Mario3",
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