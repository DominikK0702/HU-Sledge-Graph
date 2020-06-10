import sys
import matplotlib

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.backend_bases import MouseButton
from matplotlib.figure import Figure
from configparser import ConfigParser
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QGroupBox, QWidget, QVBoxLayout, QFileDialog, QHBoxLayout, QFrame, QSplitter, QStyleFactory
from MainWindow import Ui_MainWindow
from PyLcSnap7 import S7Conn, Smarttags


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
        fig.subplots_adjust(
            top=0.93,
            bottom=0.065,
            left=0.05,
            right=0.989,
            hspace=0.2,
            wspace=0.2
        )

        self.dragging = False
        self.drag_start_pos = None

        self.mpl_connect('motion_notify_event', self.cursor_move)
        self.mpl_connect('button_press_event', self.button_press)
        self.mpl_connect('button_release_event', self.button_release)

    def cursor_move(self, event):
        if self.dragging:
            print('From:', self.drag_start_pos, 'To:', (event.xdata, event.ydata))

    def button_press(self, event):
        if event.button.value == MouseButton.LEFT:
            self.drag_start_pos = (event.xdata, event.ydata)
            self.dragging = True

    def button_release(self, event):
        if event.button.value == MouseButton.LEFT:
            self.dragging = False

    def plot_current(self, datax, datay):
        self.axes.plot(datax, datay)


class PLC(QtCore.QThread):
    def __init__(self, parent):
        super(PLC, self).__init__()
        self.parent = parent
        self.cfg = parent.cfg
        self.plc = S7Conn(self.cfg['PLC']['ip'])
        self.keep_alive = Smarttags.Bool(self.plc, self.cfg['PLC'].getint('db_in'), 0, 0)
        self.array_ist = Smarttags.RealArray(self.plc, self.cfg['PLC'].getint('db_ist'), 0, 3000)
        self.array_soll = Smarttags.RealArray(self.plc, self.cfg['PLC'].getint('db_soll'), 0, 3000)

    def run(self):
        self.parent.statusbar.showMessage(self.cfg['STRINGS']['status_plc_connecting'])
        self.sleep(1)
        if self.plc.connect():
            self.parent.statusbar.showMessage(self.cfg['STRINGS']['status_plc_connected'])
        else:
            self.parent.statusbar.showMessage(self.cfg['STRINGS']['status_plc_disconnected'])

        while True:
            self.keep_alive.write(not self.keep_alive.read())
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




        QApplication.setStyle(QStyleFactory.create('Cleanlooks'))



        self.graph = MplCanvas(self, width=5, height=4, dpi=100)
        self.graph.plot_current([0,1,2,3,4], [10,1,20,3,40])

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
        #self.btn_compare.clicked.connect(self.handle_btn_compare)
        self.btn_tool_cursor.clicked.connect(self.handle_btn_tool_cursor)
        self.btn_tool_edit.clicked.connect(self.handle_btn_tool_edit)

    def handle_btn_load(self):
        options = QFileDialog.Options()
        if not self.cfg['GUI'].getboolean('use_native_filedialog'):
            options |= QFileDialog.DontUseNativeDialog
        fileName, fileType = QFileDialog.getOpenFileName(self,self.cfg['STRINGS']['csv_load_title'],"","CSV (*.csv)", options=options)
        if fileName:
            print(fileName+'.csv')

    def handle_btn_save(self):
        options = QFileDialog.Options()
        if not self.cfg['GUI'].getboolean('use_native_filedialog'):
            options |= QFileDialog.DontUseNativeDialog
        fileName, fileType = QFileDialog.getSaveFileName(self,self.cfg['STRINGS']['csv_save_title'],"","CSV (*.csv)", options=options)
        if fileName:
            print(fileName+'.csv')

    def handle_btn_compare(self):
        print('compare')

    def handle_btn_tool_cursor(self):
        if self.btn_tool_cursor.isChecked():
            self.btn_tool_edit.setChecked(False)
            print('Cursor On')
        else:
            print('Cursor Off')

    def handle_btn_tool_edit(self):
        if self.btn_tool_edit.isChecked():
            self.btn_tool_cursor.setChecked(False)
            print('Edit On')
        else:
            print('Edit Off')


if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini', encoding='utf-8')
    app = QApplication(sys.argv)
    plc = S7Conn(config['PLC']['ip'])
    gui = GraphMainWindow(plc, config)
    sys.exit(app.exec())
