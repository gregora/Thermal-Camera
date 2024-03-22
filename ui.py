import sys
import time
from datetime import datetime
import serial

import numpy as np

from Minolta.Camera import Camera
from Fluke.Fluke import Fluke


from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel
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
        self.initUI()
        self.camera = Camera(port = '/dev/ttyUSB0', simulated = simulate)
        self.fluke = Fluke(9600, 1, serial.PARITY_NONE, serial.STOPBITS_ONE, port='/dev/ttyUSB1', simulated = simulate)

        self.data_camera = []
        self.data_fluke = []
        self.timestamps = []
  
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        button = QPushButton('Measure', self)
        button.resize(100, 50)
        button.move(700, 925)
        button.clicked.connect(self.on_click)

        self.label = QLabel("/", self)
        self.label.move(500, 860)
        self.label.resize(500, 50)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        font = self.label.font()
        font.setPointSize(25)
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

        self.show()

    @pyqtSlot()
    def on_click(self):
        temp_camera = self.camera.take_measurement()
        temp_fluke = float(self.fluke.send_command('SOUR:SENS:DATA?'))
        
        if(len(self.data_camera) == 0):
            self.initial_timestamp = time.time()

        self.data_camera.append(temp_camera)
        self.data_fluke.append(temp_fluke)
        self.timestamps.append(time.time() - self.initial_timestamp)
        
        std_camera = np.std(self.data_camera)
        std_fluke = np.std(self.data_fluke)

        self.label.setText("Camera: " + str(temp_camera) + " °C    -    Fluke: " + str(temp_fluke) + " °C")
        self.graph.plot(self.timestamps, self.data_camera, clear = True, pen = 'r')
        self.graph.plot(self.timestamps, self.data_fluke, clear = False, pen = 'b')

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App(simulate=True)
    sys.exit(app.exec_())

