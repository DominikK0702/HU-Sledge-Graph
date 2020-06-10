import sys
import csv
import numpy as np
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.backend_bases import MouseButton
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
from configparser import ConfigParser
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QGroupBox, QWidget, QVBoxLayout, \
    QFileDialog, QHBoxLayout, QFrame, QSplitter, QStyleFactory
from MainWindow import Ui_MainWindow
from PyLcSnap7 import S7Conn, Smarttags

matplotlib.use('Qt5Agg')

class SnaptoCursor:
    """
    Like Cursor but the crosshair snaps to the nearest x, y point.
    For simplicity, this assumes that *x* is sorted.
    """

    def __init__(self, ax, x, y):
        self.ax = ax
        self.lx = ax.axhline(color='k')  # the horiz line
        self.ly = ax.axvline(color='k')  # the vert line
        self.x = x
        self.y = y
        # text location in axes coords
        self.txt = ax.text(0.7, 0.9, '', transform=ax.transAxes)

    def mouse_move(self, event):
        if not event.inaxes:
            return

        x, y = event.xdata, event.ydata
        indx = min(np.searchsorted(self.x, x), len(self.x) - 1)
        x = self.x[indx]
        y = self.y[indx]
        # update the line positions
        self.lx.set_ydata(y)
        self.ly.set_xdata(x)

        self.txt.set_text('x=%1.2f, y=%1.2f' % (x, y))
        print('x=%1.2f, y=%1.2f' % (x, y))
        self.ax.figure.canvas.draw()


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, config, ):
        self.cfg = config
        fig = Figure(figsize=(5, 4), dpi=self.cfg['GRAPH'].getint('dpi'))
        self.axes = fig.add_subplot(111)
        self.edit_mode = False
        self.cursor_mode = False
        self.current_data = None
        super(MplCanvas, self).__init__(fig)
        fig.subplots_adjust(
            top=0.93,
            bottom=0.065,
            left=0.05,
            right=0.989,
            hspace=0.2,
            wspace=0.2
        )
        self.cursor = SnaptoCursor(self.axes,[i[0] for i in self.curre])


        self.dragging = False
        self.drag_start_pos = None

        self.mpl_connect('motion_notify_event', self.cursor_move)
        self.mpl_connect('button_press_event', self.button_press)
        self.mpl_connect('button_release_event', self.button_release)

    def cursor_move(self, event):
        if self.cursor_mode:
            print('Cursor:',event)

        if self.dragging and self.edit_mode:
            print('Drag From:', self.drag_start_pos, 'To:', (event.xdata, event.ydata))

    def button_press(self, event):
        if event.button.value == MouseButton.LEFT:
            self.drag_start_pos = (event.xdata, event.ydata)
            self.dragging = True

    def button_release(self, event):
        if event.button.value == MouseButton.LEFT:
            self.dragging = False

    def plot_current(self, datax, datay):
        self.axes.clear()
        self.axes.plot(datax, datay)
        self.cursor.ax = self.axes
        self.draw()

    def plot_ist(self, datax, datay):
        self.axes.clear()
        self.axes.plot(datax, datay)
        self.draw()

    def plot_soll(self, datax, datay):
        self.axes.clear()
        self.axes.plot(datax, datay)
        self.draw()


class PLC(QtCore.QThread):
    def __init__(self, parent):
        super(PLC, self).__init__()
        self.parent = parent
        self.cfg = parent.cfg
        self.plc = S7Conn(self.cfg['PLC']['ip'])
        self.keep_alive = Smarttags.Bool(self.plc, self.cfg['PLC'].getint('db_in'), 0, 0)
        self.array_ist = Smarttags.RealArray(self.plc, self.cfg['PLC'].getint('db_ist'), 0, 3000)
        self.array_soll = Smarttags.RealArray(self.plc, self.cfg['PLC'].getint('db_soll'), 0, 3000)

    def submit_data(self, data):
        done = False
        while not done:
            try:
                self.array_soll.write(data)
                done = True
            except Exception as e:
                print(e)



    def run(self):
        self.parent.statusbar.showMessage(self.cfg['STRINGS']['status_plc_connecting'])
        self.sleep(1)
        if self.plc.connect():
            self.parent.statusbar.showMessage(self.cfg['STRINGS']['status_plc_connected'])
        else:
            self.parent.statusbar.showMessage(self.cfg['STRINGS']['status_plc_disconnected'])

        while True:
            try:
                self.keep_alive.write(not self.keep_alive.read())
            except Exception as e:
                pass
            self.msleep(200)


class GraphMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, plc, config, *args, **kwargs):
        super(GraphMainWindow, self).__init__(*args, **kwargs)
        self.cfg = config
        self.plc = PLC(self)
        self.plc.start()

        self.setupUi(self)
        self.setupWindow()
        self.connect_componets()

        self.graph = MplCanvas(self.cfg)

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar2QT(self.graph, self)

        self.mplLayout.addWidget(self.graph)
        self.mplLayout.addWidget(toolbar)

        self.show()

    def setupWindow(self):
        self.setWindowIcon(QtGui.QIcon('./assets/primary-chart-line.png'))
        self.setWindowTitle(self.cfg['GUI']['title'])
        self.logo.setPixmap(QtGui.QPixmap('./assets/logo.png'))

    def connect_componets(self):
        self.btn_load.clicked.connect(self.handle_btn_load)
        self.btn_save.clicked.connect(self.handle_btn_save)
        # self.btn_compare.clicked.connect(self.handle_btn_compare)
        self.btn_tool_cursor.clicked.connect(self.handle_btn_tool_cursor)
        self.btn_tool_edit.clicked.connect(self.handle_btn_tool_edit)
        self.btn_submit_plc.clicked.connect(self.handle_btn_submit_plc)

    def handle_btn_load(self):
        options = QFileDialog.Options()
        if not self.cfg['GUI'].getboolean('use_native_filedialog'):
            options |= QFileDialog.DontUseNativeDialog
        fileName, fileType = QFileDialog.getOpenFileName(self, self.cfg['STRINGS']['csv_load_title'], "", "CSV (*.csv)",
                                                         options=options)
        if fileName:
            with open(fileName, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')
                self.graph.current_data = []
                for row in reader:
                    self.graph.current_data.append([int(row[0]), float(row[1])])
            self.statusbar.showMessage(self.cfg['STRINGS']['status_csv_loaded'])

            self.graph.plot_current([i for i in range(len(self.graph.current_data))], [i[1] for i in self.graph.current_data])

    def handle_btn_save(self):
        options = QFileDialog.Options()
        if not self.cfg['GUI'].getboolean('use_native_filedialog'):
            options |= QFileDialog.DontUseNativeDialog
        fileName, fileType = QFileDialog.getSaveFileName(self, self.cfg['STRINGS']['csv_save_title'], "", "CSV (*.csv)",
                                                         options=options)
        if fileName:
            with open(fileName, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerows(self.graph.current_data)
            self.statusbar.showMessage(self.cfg['STRINGS']['status_csv_saved'])

    def handle_btn_compare(self):
        print('compare')

    def handle_btn_tool_cursor(self):
        if self.btn_tool_cursor.isChecked():
            self.btn_tool_edit.setChecked(False)
            self.graph.cursor_mode = True
            self.graph.edit_mode = False
        else:
            self.graph.cursor_mode = False

    def handle_btn_tool_edit(self):
        if self.btn_tool_edit.isChecked():
            self.btn_tool_cursor.setChecked(False)
            self.graph.edit_mode = True
            self.graph.cursor_mode = False
        else:
            self.graph.edit_mode = False

    def handle_btn_submit_plc(self):
        if self.current_data:
            self.plc.submit_data([i[1] for i in self.current_data])
            self.statusbar.showMessage(self.cfg['STRINGS']['status_plc_data_submit'])
        else:
            self.statusbar.showMessage(self.cfg['STRINGS']['status_plc_data_submit_error'])

if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini', encoding='utf-8')
    app = QApplication(sys.argv)
    plc = S7Conn(config['PLC']['ip'])
    gui = GraphMainWindow(plc, config)
    sys.exit(app.exec())
