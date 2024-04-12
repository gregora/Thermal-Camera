import serial
import time




class Fluke:
    def __init__(self, baudrate, timeout, parity, stopbits, port = 'COM3'):
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
        result = b''
        self.ser.setRTS(True)

        command_binary = command.encode('utf-8') + b'\r'
        
        while result == b'':
            self.ser.write(command_binary)
            result = self.ser.readline()
            result = result.decode('utf-8')
            time.sleep(1)

        return result
    
    def start(self,temp):
        set_PT = self.send_command('SOUR:SPO ' + str(temp)) #Nastavitev main set pointa !
        start = self.send_command('OUTP:STAT 1') # 0 - OFF, 1 - ON

        print("Set point temperature: ",temp)
    
    def stop(self):
        stop = self.send_command('OUTP:STAT 0')
        print("Stoping...")

    def reached_temp(self):
        set_p = self.send_command('SOUR:SPO?') #SOUR:STAB:TEST? SOUR:STAB:LIM?
        set_p = float(set_p)
        print("Set temp",set_p)
        temp = self.send_command('SOUR:SENS:DATA?')
        temp = float(temp)
        print("Actual Temp",temp)
        f = temp - set_p
        while f > 0.01 or f < -0.01:
            return 0
        return 1
    
    