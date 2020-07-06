import sys
import csv
from PIL import ImageColor
from scipy.signal import savgol_filter
from SinamicsExport import get_last_trace
from configparser import ConfigParser
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QDesktopWidget
from MainWindow import Ui_MainWindow
from PLC import PLC
from Graph import Graph, TracePlot
import pyqtgraph as pg
import TraceHelper


class GraphMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, config, *args, **kwargs):
        super(GraphMainWindow, self).__init__(*args, **kwargs)
        self.current_data_x = []
        self.current_data_y = []
        self.compare_data_x = []
        self.soll_data_y = []
        self.ist_data_y = []
        self.edit_mode = False
        self.current_trace = TraceHelper.Trace()
        self.cfg = config

        self.setupUi(self)
        self.setupWindow()

        self.plc = PLC(self)
        self.plc.start()

        self.trace_plot = TracePlot(self.cfg, self)
        self.graph = Graph(self.cfg, self)

        self.tab_layout_pulse.addWidget(self.graph)
        self.tab_layout_trace.addWidget(self.trace_plot)

        self.connect_componets()

        self.pen_zero = pg.mkPen(color=(255, 255, 0), width=1)
        self.pen_current = pg.mkPen(color=ImageColor.getrgb('#' + self.cfg['GRAPH']['color_current']),
                                    width=self.cfg['GRAPH'].getint('width_current'))
        self.pen_soll = pg.mkPen(color=ImageColor.getrgb('#' + self.cfg['GRAPH']['color_compare_soll']),
                                 width=self.cfg['GRAPH'].getint('width_compare_soll'))
        self.pen_ist = pg.mkPen(color=ImageColor.getrgb('#' + self.cfg['GRAPH']['color_compare_ist']),
                                width=self.cfg['GRAPH'].getint('width_compare_ist'))

        self.show()

    def setupWindow(self):
        self.setWindowIcon(QtGui.QIcon(self.cfg['GUI']['window_icon']))
        self.setWindowTitle(self.cfg['GUI']['title'])
        self.logo.setPixmap(QtGui.QPixmap(self.cfg['GUI']['logo']))

        self.monitor = QDesktopWidget().screenGeometry(self.cfg['GUI'].getint('monitor_nr'))
        self.move(self.monitor.left(), self.monitor.top())

        if self.cfg['GUI'].getboolean('always_top'): self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        if self.cfg['GUI'].getboolean('maximized'): self.showMaximized()
        if self.cfg['GUI'].getboolean('fullscreen'): self.showFullScreen()

    def connect_componets(self):
        # Buttons
        self.btn_load.clicked.connect(self.handle_btn_load)
        self.btn_save.clicked.connect(self.handle_btn_save)
        self.btn_compare.clicked.connect(self.handle_btn_compare)
        self.btn_tool_cursor.clicked.connect(self.handle_btn_tool_cursor)
        self.btn_tool_edit.clicked.connect(self.handle_btn_tool_edit)
        self.btn_submit_plc.clicked.connect(self.handle_btn_submit_plc)
        self.btn_trace_loadfile.clicked.connect(self.handle_btn_trace_loadfile)
        self.btn_trace_loadlast.clicked.connect(self.handle_btn_trace_loadlast)
        self.btn_trace_save.clicked.connect(self.handle_btn_trace_save)
        self.btn_trace_clear.clicked.connect(self.handle_btn_trace_clear)
        self.btn_autorange.clicked.connect(self.trace_plot.autoRange)
        # Tabs
        self.tabWidget.currentChanged.connect(self.sync_tabs)

    def sync_tabs(self):
        self.tabWidgetTools.setCurrentIndex(self.tabWidget.currentIndex())

    def handle_btn_load(self):
        options = QFileDialog.Options()
        if not self.cfg['GUI'].getboolean('use_native_filedialog'):
            options |= QFileDialog.DontUseNativeDialog
        fileName, fileType = QFileDialog.getOpenFileName(self, self.cfg['STRINGS']['csv_load_title'], "", "CSV (*.csv)",
                                                         options=options)
        self.current_data_x = []
        self.current_data_y = []
        if fileName:
            with open(fileName, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')
                for row in reader:
                    self.current_data_x.append(float(row[0].replace(',', '.')))
                    self.current_data_y.append(float(row[1].replace(',', '.')))

            self.statusbar.showMessage(self.cfg['STRINGS']['status_csv_loaded'])
            self.btn_tool_edit.setChecked(False)
            self.btn_tool_cursor.setChecked(False)
            self.graph.cursor.enabled(False)
            self.graph.clear()
            self.graph.plot(self.current_data_x, self.current_data_y, pen=self.pen_current,
                            name=self.cfg['STRINGS']['graph_current_label'])
            self.graph.getPlotItem().legend.setPen(self.graph.pen_legend)
            self.graph.enableAutoRange(x=True, y=True)
            self.tabWidget.setCurrentIndex(0)
            self.graph.setTitle(self.cfg['STRINGS']['graph_title_current'])

    def handle_btn_save(self):
        options = QFileDialog.Options()
        if not self.cfg['GUI'].getboolean('use_native_filedialog'):
            options |= QFileDialog.DontUseNativeDialog
        fileName, fileType = QFileDialog.getSaveFileName(self, self.cfg['STRINGS']['csv_save_title'], "", "CSV (*.csv)",
                                                         options=options)
        if fileName:
            khz = self.cfg['GRAPH'].getint('resolution_khz')
            with open(fileName, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file, delimiter=';')
                for count, i in enumerate(self.current_data_y):
                    writer.writerow(
                        [format((count + 1) / (khz * 1000), f'.{self.cfg["GRAPH"]["csv_export_float_precision_x"]}f'),
                         format(i, f'.{self.cfg["GRAPH"]["csv_export_float_precision_y"]}f')])

            self.statusbar.showMessage(self.cfg['STRINGS']['status_csv_saved'])

    def handle_btn_compare(self):
        self.soll_data_y, self.ist_data_y = self.plc.read_soll_ist_data()
        self.ist_data_y = []
        filename = get_last_trace(self.cfg['PLC']['ip_cu320'], './export/trace.csv')
        if not filename:
            return self.statusbar.showMessage(self.cfg['STRINGS']['status_trace_connnection_error'])
        header = None
        data = []
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for i, row in enumerate(reader):
                if i == 0:
                    header = row
                else:
                    data.append(row)

        self.btn_tool_edit.setChecked(False)
        self.btn_tool_cursor.setChecked(False)
        self.graph.cursor.enabled(False)

        self.graph.clear()
        self.current_data_x = []
        self.current_data_y = []
        khz = self.cfg['GRAPH'].getint('resolution_khz')

        self.graph.setTitle(self.cfg['STRINGS']['graph_title_compare'])
        # self.graph.plot([float(i[0].replace(',','.'))/1000 for i in data], [float(i[4].replace(',','.')) for i in data],
        #                pen=self.pen_ist, name=self.cfg['STRINGS']['graph_ist_label'])
        self.graph.plot([float(i[0].replace(',', '.')) / 1000 for i in data],
                        savgol_filter([float(i[4].replace(',', '.')) for i in data], 51, 3),
                        pen=self.pen_ist, name=self.cfg['STRINGS']['graph_ist_label'])
        self.graph.plot([(count + 1) / (khz * 1000) for count in range(len(self.soll_data_y))],
                        [i * 60 for i in self.soll_data_y],
                        pen=self.pen_soll, name=self.cfg['STRINGS']['graph_soll_label'])
        self.graph.getPlotItem().legend.setPen(self.graph.pen_legend)
        self.statusbar.showMessage(self.cfg['STRINGS']['status_plc_data_loaded'])

    def handle_btn_tool_cursor(self):
        if self.btn_tool_cursor.isChecked():
            self.btn_tool_edit.setChecked(False)
            self.graph.cursor.enabled(True)
        else:
            self.graph.cursor.enabled(False)

    def handle_btn_tool_edit(self):
        if self.btn_tool_edit.isChecked():
            self.btn_tool_cursor.setChecked(False)
            self.graph.toggle_edit_mode(True)
            self.graph.cursor.enabled(False)
        else:
            self.graph.toggle_edit_mode(False)

    def handle_btn_submit_plc(self):
        done = False
        while not done:
            try:
                self.plc.anf_submit_data.write(True)
                done = True
            except Exception as e:
                print(e)

    def handle_btn_trace_loadfile(self):
        options = QFileDialog.Options()
        if not self.cfg['GUI'].getboolean('use_native_filedialog'):
            options |= QFileDialog.DontUseNativeDialog
        fileName, fileType = QFileDialog.getOpenFileName(self, self.cfg['STRINGS']['trace_load_title'], "",
                                                         "Trace ACX (*.ACX.GZ);;Trace CSV (*.csv)",
                                                         options=options)
        if fileName and fileType == 'Trace ACX (*.ACX.GZ)':
            self.trace_plot.load_trace_acx(fileName)
        elif fileName and fileType == 'Trace CSV (*.csv)':
            self.trace_plot.load_trace_csv(fileName)
        if fileName:
            self.statusbar.showMessage(self.cfg['STRINGS']['status_trace_file_loaded'])

    def handle_btn_trace_loadlast(self):
        try:
            self.trace_plot.load_trace_csv('./export/trace.csv')
            self.statusbar.showMessage(self.cfg['STRINGS']['status_trace_last_loaded'])
        except Exception as e:
            self.statusbar.showMessage(str(e))

    def handle_btn_trace_clear(self):
        self.current_trace.clear()
        self.graph.clear()
        self.graph.setXLabel('')
        self.graph.setYLabel('')
        self.statusbar.showMessage(self.cfg['STRINGS']['status_trace_cleared'])

    def handle_btn_trace_save(self):
        if self.current_trace.datapoints <= 0:
            return
        self.mainwindow.tabWidget.setCurrentIndex(0)
        options = QFileDialog.Options()
        if not self.cfg['GUI'].getboolean('use_native_filedialog'):
            options |= QFileDialog.DontUseNativeDialog
        fileName, fileType = QFileDialog.getSaveFileName(self, self.cfg['STRINGS']['trace_save_title'], "",
                                                         "CSV (*.csv)",
                                                         options=options)
        if fileName:
            try:
                self.current_trace.save_to_csv(fileName)
                self.statusbar.showMessage(self.cfg['STRINGS']['status_trace_saved'])
            except Exception as e:
                self.statusbar.showMessage(str(e))


if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini', encoding='utf-8')
    app = QApplication(sys.argv)
    gui = GraphMainWindow(config)
    sys.exit(app.exec())
