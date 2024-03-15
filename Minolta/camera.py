import serial
import time


class Camera:
    def __init__(self, port = '/dev/ttyUSB0'):
        self.ser = serial.Serial(port, baudrate=4800, stopbits=serial.STOPBITS_TWO, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, timeout=1.0)

    def clear_buffer(self):
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
        response = self.send_command('MS')
        response = response.decode('utf-8')

        if response[0] == 'E':
            return 'Error'
        else:
            temperature = float(response[3:9])

        return temperature

    
    def close(self):
        self.ser.close()

camera = Camera()

temp = camera.take_measurement()
print(temp)

camera.clear_buffer()
camera.close()

