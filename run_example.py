import random
import sys

import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from pyqt_graph_widgets.simple_widget import GraphWidget


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        
        central = QWidget()
        self.setCentralWidget(central)
        
        graph_widget = GraphWidget(self, data)
        graph_widget.set_data(data)
        
        vbox = QVBoxLayout(central)
        vbox.addWidget(graph_widget)
        
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(lambda: graph_widget.set_data(
            np.array(graph_widget._source_data.tolist() + [[random.randint(20, 50), 
                                                            len(graph_widget._source_data) * 2]])))
        self.timer.start()
        
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        return super().keyPressEvent(event)
    
    
if __name__ == '__main__':
    app = QApplication([])
    
    # data = np.array([[x ** 2, x] for x in np.arange(-10, 10.1, 0.1)])
    # data = np.array([[y, x] for x in np.arange()])
    data = np.array([[random.randint(20, 50), x] for x in range(0, 100, 2)])
    # data = np.array([[(x ** 2) * ((x - 2) ** 2), x] for x in np.arange(-1, 3, 0.1)])
    print(data)
    window = Window()
    window.resize(1280, 720)
    window.move(window.rect().center() / 2)
    window.show()
    
    sys.exit(app.exec())