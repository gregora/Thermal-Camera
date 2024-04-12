from Fluke import Fluke

import serial
import time


if __name__ == '__main__':
    F = Fluke(9600, 1, serial.PARITY_NONE, serial.STOPBITS_ONE, port = 'COM3')
   
    F.start(39.8) # Set target temp degrees
    stable = 0
    print(F.reached_temp())
    while stable == 0: #Check if the target temp is reached
        print("Waiting for the target temperature to be reached...")
        time.sleep(3)
        stable = F.reached_temp()
        print(stable)

    print("Temperature reached!")
    F.stop() #Stop the program 

    #Dodaj vse parametre iz ekrana da so v UI 
     