from Minolta.Camera import Camera
from Fluke.Fluke import Fluke

import numpy as np
import serial
import time
import sys
import json

from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

SIMULATE = False

# load parameters from json
parameters = json.load(open('calibration_parameters.json'))

temperatures = parameters["temperatures"]
N = parameters["N"]
sleep_time = parameters["sleep_time"]
N_r = parameters["N_r"]
std_treshold = parameters["std_treshold"]
err_treshold = parameters["err_treshold"]

camera_emissivity = parameters["camera_emissivity"]

def measure():

    camera = Camera(port = '/dev/ttyUSB1', simulated = SIMULATE)
    fluke = Fluke(9600, 1, serial.PARITY_NONE, serial.STOPBITS_ONE, port='/dev/ttyUSB0', simulated = SIMULATE)

    camera.set_emissivity(camera_emissivity)


    camera_measurements = np.zeros((len(temperatures), N))
    fluke_measurements = np.zeros((len(temperatures), N))


    for t in temperatures:

        fluke.start(t)

        rolling_t = [] # buffer for rolling temperature measurements to determine stability

        while len(rolling_t) < N_r or np.std(rolling_t) > std_treshold or np.abs(np.mean(rolling_t) - t) > err_treshold:

            rolling_t.append(fluke.get_temp())
            time.sleep(sleep_time)

            if len(rolling_t) > N_r:
                print(f'Current standard deviation {np.std(rolling_t):,.2f}, current error {np.abs(np.mean(rolling_t) - t):,.2f}')
                rolling_t.pop(0)

        # Temperature is now stable
        print("Temperature reached: ", t)

        for i in range(N):
            temp_fluke = fluke.get_temp()
            temp_camera = camera.take_measurement()

            camera_measurements[temperatures.index(t), i] = temp_camera
            fluke_measurements[temperatures.index(t), i] = temp_fluke

            print("Camera: ", temp_camera, "Fluke: ", temp_fluke)

            time.sleep(sleep_time)

    #save data to ./calibration as txt
    np.savetxt('calibration/camera_measurements.txt', camera_measurements)
    np.savetxt('calibration/fluke_measurements.txt', fluke_measurements)

def calculate_calibration():
    
    camera_measurements = np.loadtxt('calibration/camera_measurements.txt')
    fluke_measurements = np.loadtxt('calibration/fluke_measurements.txt')

    # average
    camera_avg = np.mean(camera_measurements, axis=1)
    fluke_avg = np.mean(fluke_measurements, axis=1)

    # linear regression
    reg = LinearRegression().fit(fluke_avg.reshape(-1, 1), camera_avg)

    # visualize camera_avg vs fluke_avg and regression line
    plt.subplot(1, 2, 1)
    plt.plot(fluke_avg, reg.predict(fluke_avg.reshape(-1, 1)), c = 'b', linestyle = '--', linewidth = 1)
    plt.scatter(fluke_avg, camera_avg, c = 'r', s = 10)
    plt.text(fluke_avg[0] + 20, camera_avg[0], f'y = {reg.coef_[0]:,.2f}x + {reg.intercept_:,.2f}', fontsize="large", fontstyle="oblique")
    plt.xlabel('Fluke temperature [°C]')
    plt.ylabel('Camera temperature [°C]')
    plt.title('Calibration')

    # visualize errors
    plt.subplot(1, 2, 2)
    plt.axhline(0, color='black', linewidth=1)
    plt.plot(temperatures, camera_avg - fluke_avg, c = 'r')
    plt.xlabel('Reference temperature [°C]')
    plt.ylabel('Error [°C]')
    plt.title('Error vs Temperature')


    plt.show()


    # save calibration coefficients to ./calibration as txt
    np.savetxt('calibration/regression_coefficients.txt', [reg.coef_[0], reg.intercept_])





if len(sys.argv) > 1:
    if sys.argv[1] == 'measure':
        measure()
        print("MEASURING COMPLETE!")
        print()

calculate_calibration()

