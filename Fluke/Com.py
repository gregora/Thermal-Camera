import serial
import time
import PySimpleGUI as psg

parity_mapping = {
    'NONE': serial.PARITY_NONE,
    'EVEN': serial.PARITY_EVEN,
    'ODD': serial.PARITY_ODD,
    'MARK': serial.PARITY_MARK,
    'SPACE': serial.PARITY_SPACE
}

stopbits_mapping = {
    'ONE': serial.STOPBITS_ONE,
    'ONE_POINT_FIVE': serial.STOPBITS_ONE_POINT_FIVE,
    'TWO': serial.STOPBITS_TWO
}


class UI:
    def Setup():
        timeout_list = [0.1,0.3,0.5,1,2,3,4]
        parity_list = ["serial.PARITY_NONE", "serial.PARITY_EVEN", "serial.PARITY_ODD","serial.PARITY_MARK","serial.PARITY_SPACE"]
        stopbit_list = ["serial.STOPBITS_ONE", "serial.STOPBITS_ONE_POINT_FIVE", "serial.STOPBITS_TWO"]
        baud_input = psg.Input('', enable_events=True, key='-INPUT-', font=('Arial Bold', 14), justification='left')
        lst2 = psg.Combo(timeout_list, font=('Arial Bold', 14),  expand_x=True, enable_events=True,  readonly=False, key='-COMBO2-')
        lst3 = psg.Combo(parity_list, font=('Arial Bold', 14),  expand_x=True, enable_events=True,  readonly=False, key='-COMBO3-')
        lst4 = psg.Combo(stopbit_list, font=('Arial Bold', 14),  expand_x=True, enable_events=True,  readonly=False, key='-COMBO4-')
        text1 = psg.Text("Določi serijsko povezavo", font=('Arial Bold', 14), justification='center')
        text2 = psg.Text("Baud rate", font=('Arial Bold', 14), justification='center')
        text3 = psg.Text("Timeout [s]", font=('Arial Bold', 14), justification='center')
        text4 = psg.Text("Pariteta", font=('Arial Bold', 14), justification='center')
        text5 = psg.Text("Število stop bitov", font=('Arial Bold', 14), justification='center')

        layout = [[text1], [baud_input,text2], [lst2,text3], [lst3,text4], [lst4,text5],[psg.Button('Add'), psg.Button('Exit')]]
            
        window = psg.Window('RS232 - Fluke', layout, size=(715, 400))
        while True:
            event, values = window.read()
            # End program if user closes window or
            # presses the OK button
            if event == 'Add':
                print('You entered ', values['-INPUT-'])
                print('You entered ', values['-COMBO2-'])
                print('You entered ', values['-COMBO3-'])
                print('You entered ', values['-COMBO4-'])
                parity = parity_mapping[values['-COMBO3-'].replace('serial.PARITY_', '').replace('"','')] #just straight fun :)
                stopbits = stopbits_mapping[values['-COMBO4-'].replace('serial.STOPBITS_', '').replace('"','')]
                SerialCommunication(values['-INPUT-'], values['-COMBO2-'], parity, stopbits)
                UI.Comanding()
            if event == "Exit" or event == psg.WIN_CLOSED:
                break

        window.close()
    
    def Comanding():
        command_input = psg.Input('', enable_events=True, key='-INPUT-', font=('Arial Bold', 14), justification='left')
        text1 = psg.Text("Vnesi ukaz", font=('Arial Bold', 14), justification='center')
        layout = [[text1], [command_input],[psg.Button('Send'), psg.Button('Exit')]]
        window = psg.Window('RS232 - Fluke', layout, size=(715, 200))
        while True:
            event, values = window.read()
            # End program if user closes window or
            # presses the OK button
            if event == 'Send':
                print('You entered ', values['-INPUT-'])
                SerialCommunication.send_command(values['-INPUT-'])
            if event == "Exit" or event == psg.WIN_CLOSED:
                break
        window.close()



class SerialCommunication:
    def __init__(self, baudrate, timeout, parity, stopbits):
        self.ser = serial.Serial(
            port = 'COM3',
            baudrate = baudrate,
            timeout=timeout,
            parity=parity, 
            stopbits=stopbits)
    
    def send_command(self, command):
        self.ser.write(command)
        time.sleep(0.1)
        return self.ser.readline()
    
    
if __name__ == '__main__':
    UI.Setup()
    