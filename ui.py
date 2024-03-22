import sys
import time
from datetime import datetime

import numpy as np

from Minolta.Camera import Camera


from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import PyQt5.QtCore as QtCore

import pyqtgraph as pg
import pyqtgraph.exporters



class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Remote temperature mesurement system'
        self.left = 10
        self.top = 10
        self.width = 1500
        self.height = 1000
        self.initUI()
        self.camera = Camera(simulated = False)

        self.data = []
        self.timestamps = []
  
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        button = QPushButton('Measure', self)
        button.resize(100, 50)
        button.move(700, 925)
        button.clicked.connect(self.on_click)

        self.label = QLabel("/", self)
        self.label.move(700, 860)
        self.label.resize(100, 50)
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
        temp = self.camera.take_measurement()
        
        if(len(self.data) == 0):
            self.initial_timestamp = time.time()
        self.data.append(temp)
        self.timestamps.append(time.time() - self.initial_timestamp)
        
        std = np.std(self.data)

        self.label.setText(str(temp) + " °C")
        self.graph.plot(self.timestamps, self.data, clear = True, pen = 'b')

        self.graph_data.setText("First data point at: " + str(datetime.fromtimestamp(self.initial_timestamp).isoformat(sep=" ", timespec="seconds")) + "\n")
        self.graph_data.setText(self.graph_data.text() + "Standard deviation: " + str(round(std, 2)))

    @pyqtSlot()
    def export_graph(self):
        if len(self.data) > 0: 
            exporter = pg.exporters.CSVExporter(self.graph.plotItem)
            exporter.export('data/' + str(datetime.fromtimestamp(self.initial_timestamp).isoformat(sep=" ", timespec="seconds")) + '.csv')
        else:
            print("No data to export!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())