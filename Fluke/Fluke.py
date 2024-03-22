import serial
import time
import random




class Fluke:
    def __init__(self, baudrate, timeout, parity, stopbits, port = 'COM3', simulated = False):

        self.simulated = simulated
        if simulated:
            return

        self.ser = serial.Serial(
            port = port,
            baudrate = baudrate,
            timeout=timeout,
            parity=parity, 
            stopbits=stopbits,
            bytesize=serial.EIGHTBITS)
        #VIDIS KO SI IDIOT PA NEZNAS BRAT 
            # Commands consist of a command header and, if necessary, parameter data. All com-
            # mands must be terminated with either a carriage return (ASCII 0D hex or 13 decimal)
            # or new line character (ASCII 0A hex or 10 decimal).


    def send_command(self, command):

        if self.simulated:
            return round(23.0 + 3*random.random(), 1)

        result = b''
        self.ser.setRTS(True)

        command_binary = command.encode('utf-8') + b'\r'
        
        while result == b'':
            self.ser.write(command_binary)
            result = self.ser.readline()
            result = result.decode('utf-8')
            time.sleep(1)

        return result
    