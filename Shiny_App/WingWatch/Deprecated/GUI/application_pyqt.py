import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QLineEdit, QLabel
import pandas as pd

class PlottingWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt6 Plotting Example")
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # File input components
        self.file_label = QLabel("No file selected")
        self.layout.addWidget(self.file_label)

        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Path to the file")
        self.layout.addWidget(self.file_input)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.open_file_dialog)
        self.layout.addWidget(self.browse_button)

        # Plot area
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        # Initialize plot
        self.data = None
        self.update_plot()

    def open_file_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "CSV Files (*.csv);;All Files (*)")
        if file_name:
            self.file_input.setText(file_name)
            self.file_label.setText(file_name)
            self.load_data(file_name)


    def load_data(self, file_name):
        try:
            # Assuming the file contains two columns of numeric data (e.g., x and y values)
            data = pd.read_csv(file_name, delimiter=',')
            self.data = data
            self.update_plot()
        except Exception as e:
            print(f"Error loading file: {e}")

    def update_plot(self):
        self.ax.clear()
        if self.data is not None:
            x, y = self.data.X, self.data.Y
            self.ax.scatter(x, y)
            self.ax.set_xlabel('X-axis')
            self.ax.set_ylabel('Y-axis')
            self.ax.set_title('Plot')
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlottingWindow()
    window.show()
    sys.exit(app.exec())
