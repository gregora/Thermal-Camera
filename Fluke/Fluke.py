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
    
    def start(self,temp):
        set_PT = self.send_command('SOUR:SPO ' + str(temp)) #Nastavitev main set pointa !
        start = self.send_command('OUTP:STAT 1') # 0 - OFF, 1 - ON

        print("Set point temperature: ",temp)
    
    def stop(self):
        stop = self.send_command('OUTP:STAT 0')
        print("Stoping...")

    def get_temp(self):
        temp_app = float(self.send_command('SOUR:SENS:DATA?')) #display temperature
        return temp_app
    
    def get_set_point_temp(self):
        try:
            temp_set = float(self.send_command('SOUR:SPO?'))
        except:
            temp_set = 0
        return temp_set
    
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

    def get_data(self):
        out_stat = self.send_command('OUTP:STAT?') # Output stat 0 - OFF, 1 - ON
        irt = self.send_command('SOUR:EMIS?') #IRT stat
        cal = self.send_command('SOUR:CAL:WAV?') #Cal stat
        
        return out_stat,irt,cal

    
    