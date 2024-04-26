import sys
import time
from datetime import datetime
import serial
import threading

import numpy as np

from Minolta.Camera import Camera
from Fluke.Fluke import Fluke


from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import PyQt5.QtCore as QtCore

import pyqtgraph as pg
import pyqtgraph.exporters



class App(QWidget):
    def __init__(self, simulate = False):
        super().__init__()
        self.title = 'Remote temperature mesurement system'
        self.left = 10
        self.top = 10
        self.width = 1500
        self.height = 1000
        self.camera = Camera(port = '/dev/ttyUSB0', simulated = simulate)
        self.fluke = Fluke(9600, 1, serial.PARITY_NONE, serial.STOPBITS_ONE, port='/dev/ttyUSB1', simulated = simulate)

        self.initUI()

        self.data_camera = []
        self.data_fluke = []
        self.timestamps = []

        self.update_interval = threading.Thread(target = self.update_fluke_info)
        self.update_interval.start()

    def initUI(self):
    
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        button = QPushButton('Measure', self)
        button.resize(100, 50)
        button.move(700, 925)
        font = button.font()
        font.setPointSize(50)
        button.clicked.connect(self.on_click)

        self.label = QLabel("/", self)
        self.label.move(350, 860)
        self.label.resize(800, 50)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        font = self.label.font()
        font.setPointSize(20)
        self.label.setFont(font)

        self.graph = pg.PlotWidget(self)
        self.graph.move(250, 50)
        self.graph.resize(1000, 400)
        self.graph.showGrid(x = True, y = True)
        self.graph.setLabel("left", "Temperature (°C)")
        self.graph.setLabel("bottom", "Time (s)")

        self.export_button = QPushButton('Export CSV', self)
        self.export_button.resize(100, 50)
        self.export_button.move(1150, 50)
        self.export_button.clicked.connect(self.export_graph)

        self.graph_data = QLabel("", self)
        self.graph_data.move(250, 470)
        self.graph_data.resize(500, 200)
        font = self.graph_data.font()
        font.setPointSize(15)
        self.graph_data.setFont(font)

        self.input_label = QLabel("Set temperature: ", self)
        self.input_label.move(850, 925)
        self.input_label.resize(150, 50)

        self.input = QLineEdit(self)
        self.input.move(975, 925)
        self.input.resize(100, 50) 
        self.input.returnPressed.connect(self.on_text_edited)
        self.input.setText(str(self.fluke.get_set_point_temp()))

        #Fluke infomation
        self.status = QPushButton(self)
        self.status.move(1400, 750)  
        self.status.resize(30, 30)  
        self.status.setStyleSheet("background-color: green; border-radius: 15px;") #Green on / Red off ?
   
        self.fluke_info = QLabel("Podatki fluke:", self)
        self.fluke_info.move(1350, 700)  
        self.fluke_info.resize(150, 50)  

        self.on_off = QLabel("On/Off", self)
        self.on_off.move(1340, 740)  
        self.on_off.resize(150, 50) 

        self.irt = QLabel("", self)
        self.irt.setGeometry(1370, 790, 60, 40)  
        self.irt.setStyleSheet("border: 1px solid black;")  

        self.irt_label = QLabel("IRT ε", self)
        self.irt_label.move(1300, 785)  
        self.irt_label.resize(150, 50) 
         
        self.cal = QLabel("", self)
        self.cal.setGeometry(1370, 850, 60, 40) 
        self.cal.setStyleSheet("border: 1px solid black;")  

        self.cal_label = QLabel("CAL λ", self)
        self.cal_label.move(1300, 845)  
        self.cal_label.resize(150, 50) 

        #test
        self.irt.setText("")
        self.cal.setText("")
        #TODO logiko spisati za spreminjanje barve in dodajanje podatkov

        self.update_fluke_info()

        self.show()

    def update_fluke_info(self):

        temp, out_stat, set_p, irt, cal = self.fluke.get_data()


        if int(out_stat) == 1:
            self.status.setStyleSheet("background-color: green; border-radius: 15px;")
        else:
            self.status.setStyleSheet("background-color: red; border-radius: 15px;")

        self.irt.setText(str(irt))

        if int(cal) == 0:
            self.cal.setText("8-14 μm")
        else:
            self.cal.setText("undefined!")


    @pyqtSlot()
    def on_click(self):
        temp_camera = self.camera.take_measurement()
        temp_fluke = self.fluke.get_temp()
        
        if(len(self.data_camera) == 0):
            self.initial_timestamp = time.time()

        self.data_camera.append(temp_camera)
        self.data_fluke.append(temp_fluke)
        self.timestamps.append(time.time() - self.initial_timestamp)
        
        std_camera = np.std(self.data_camera)
        std_fluke = np.std(self.data_fluke)

        self.label.setText("Camera: " + str(temp_camera) + " °C         Fluke: " + str(temp_fluke) + " °C")
        self.graph.plot(self.timestamps, self.data_camera,
                        name = "Camera Temp",
                        clear = True,
                        pen = 'r',
                        symbol = 'o',
                        symbolBrush = 'r',
                        symbolSize = 5
                        )
        
        self.graph.plot(self.timestamps, self.data_fluke,
                        name = "Fluke Temp",
                        clear = False,
                        pen = 'b',
                        symbol = 'o',
                        symbolBrush = 'b',
                        symbolSize = 5
                        )

        self.graph_data.setText("First data point at: " + str(datetime.fromtimestamp(self.initial_timestamp).isoformat(sep=" ", timespec="seconds")) + "\n")
        self.graph_data.setText(self.graph_data.text() + "Standard deviation of camera: " + str(round(std_camera, 2)))
        self.graph_data.setText(self.graph_data.text() + "\nStandard deviation of Fluke: " + str(round(std_fluke, 2)))

    @pyqtSlot()
    def export_graph(self):
        if len(self.data_camera) > 0: 
            exporter = pg.exporters.CSVExporter(self.graph.plotItem)
            exporter.export('data/' + str(datetime.fromtimestamp(self.initial_timestamp).isoformat(sep=" ", timespec="seconds")) + '.csv')
        else:
            print("No data to export!")

    @pyqtSlot()
    def on_text_edited(self):
        if self.input.text() == "":
            return
        temp = float(self.input.text())
        self.fluke.start(temp)
        self.input.setText(str(self.fluke.get_set_point_temp()))

        self.update_fluke_info()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = App(simulate=False)

    sys.exit(app.exec_())


