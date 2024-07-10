import sys
import serial
import time
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

class DistanceGraph(QMainWindow):
    def __init__(self, serial_port):
        super().__init__()
        try:
            self.serial_port = serial.Serial(serial_port, 9600, timeout=1)
        except serial.SerialException as e:
            QMessageBox.critical(self, "Serial Port Error", str(e))
            sys.exit()

        self.data = []

        self.initUI()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_graph)
        self.timer.start(1)

    def initUI(self):
        self.setWindowTitle('Distance Graph')

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.show()

    def update_graph(self):
        line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
        if line.startswith('Distance: '):
            try:
                distance = float(line.split(': ')[1])
                self.data.append(-distance)
                if len(self.data) > 1000:
                    self.data.pop(0)

                self.ax.clear()
                self.ax.plot(self.data)
                self.ax.set_ylim(min(self.data) - 10, 0)
                self.canvas.draw()
            except ValueError:
                pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    available_ports = list_serial_ports()
    if not available_ports:
        print("No available serial ports found.")
        sys.exit()

    print("Available serial ports:", available_ports)
    serial_port = 'COM6'

    if serial_port not in available_ports:
        print(f"Specified port {serial_port} is not available.")
        sys.exit()

    main_window = DistanceGraph(serial_port)
    sys.exit(app.exec_())
