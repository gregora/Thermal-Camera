import serial
import time
import random
import math
import numpy as np

class Camera:
    def __init__(self, port = '/dev/ttyUSB0', simulated = False):
        self.simulated = simulated
        if simulated:
            return
        
        # CAMERA SPECIFICATIONS
        # Baudrate: 4800
        # Parity: Even
        # Data bits: 7
        # Stop bits: 2
        # Start bit: 1

        self.ser = serial.Serial(port, baudrate=4800, stopbits=serial.STOPBITS_TWO, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, timeout=1.0)

    def clear_buffer(self):
        if self.simulated:
            return
        
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

    def send_command(self, command):
        result = b''
        self.ser.setRTS(True)

        command_binary = command.encode('utf-8') + b'\r'
        
        while result == b'':
            self.ser.write(command_binary)
            result = self.ser.readline()
            time.sleep(1)

        return result


    def take_measurement(self):
        
        if self.simulated:
            return round(23.0 + 3*random.random(), 1)
        
        response = self.send_command('MS')
        response = response.decode('utf-8')

        if response[0] == 'E':
            return 'Error'
        else:
            temperature = float(response[3:9])

        return temperature

    
    def close(self):
        if self.simulated:
            return

        self.ser.close()


def test_camera():

    camera = Camera(simulated=False)

    temp = camera.take_measurement()
    print(temp, time.time())

    camera.clear_buffer()
    camera.close()

test_camera()