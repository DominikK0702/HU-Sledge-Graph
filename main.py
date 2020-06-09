import sys
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.backend_bases import MouseButton
from matplotlib.figure import Figure
from configparser import ConfigParser
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QGroupBox, QWidget, QVBoxLayout


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

        self.dragging = False
        self.drag_start_pos = None

        self.mpl_connect('motion_notify_event', self.cursor_move)
        self.mpl_connect('button_press_event', self.button_press)
        self.mpl_connect('button_release_event', self.button_release)

    def cursor_move(self, event):
        if self.dragging:
            print('From:',self.drag_start_pos,'To:', (event.xdata, event.ydata))

    def button_press(self, event):
        if event.button.value == MouseButton.LEFT:
            self.drag_start_pos = (event.xdata, event.ydata)
            self.dragging = True

    def button_release(self, event):
        if event.button.value == MouseButton.LEFT:
            self.dragging = False

    def plot_current(self, datax, datay):
        self.axes.plot(datax,datay)

class HeadWidget(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(HeadWidget, self).__init__(self.parent)

class GraphMainWindow(QMainWindow):
    def __init__(self,cfg):
        self.cfg = cfg
        super(GraphMainWindow, self).__init__()
        self.initUI()

    def configUI(self):
        self.setWindowTitle(self.cfg['GUI']['title'])
        if self.cfg['GUI'].getboolean('always_on_top'):
            self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setGeometry(self.cfg['GUI'].getint('offset_x'),self.cfg['GUI'].getint('offset_y'), self.cfg['GUI'].getint('width'),self.cfg['GUI'].getint('heigth'))
        if self.cfg['GUI'].getboolean('fullscreen'):
            self.showFullScreen()

    def initUI(self):
        self.configUI()

        self.graph = MplCanvas(self, width=5, height=4, dpi=100)
        self.graph.plot_current([0,1,2,3,4], [10,1,20,3,40])

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar2QT(self.graph, self)

        head = HeadWidget(self)

        layout = QVBoxLayout()

        layout.addWidget(head)
        layout.addWidget(self.graph)
        layout.addWidget(toolbar)


        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.show()




if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini',encoding='utf-8')
    app = QApplication(sys.argv)
    gui = GraphMainWindow(config)
    sys.exit(app.exec_())
