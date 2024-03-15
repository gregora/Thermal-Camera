import serial
import time

ser = serial.Serial(
                    port = 'COM3',
                    baudrate = 9600,
                    timeout=1,
                    parity=serial.PARITY_NONE, 
                    stopbits=serial.STOPBITS_ONE)  # open serial port
#print(ser.name)  # check which port was really used
ser.write(b'UNIT:TEMP\n') 
#ser.timeout(10)
time.sleep(2)
s = ser.read(100)
