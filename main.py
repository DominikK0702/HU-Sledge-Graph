import sys
import csv
import matplotlib.pyplot as plt
from PIL import ImageColor

from configparser import ConfigParser
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QDesktopWidget
from MainWindow import Ui_MainWindow
from PyLcSnap7 import S7Conn, Smarttags
from SinamicsExport import get_last_trace
import pyqtgraph as pg


class PLC(QtCore.QThread):
    def __init__(self, parent):
        super(PLC, self).__init__()
        self.parent = parent
        self.cfg = parent.cfg
        self.plc = S7Conn(self.cfg['PLC']['ip'])
        self.keep_alive = Smarttags.Bool(self.plc, self.cfg['PLC'].getint('db_in'), 0, 0)
        self.regler_date_ready = Smarttags.Bool(self.plc, self.cfg['PLC'].getint('db_out'), 0, 0)
        self.array_ist = Smarttags.RealArray(self.plc, self.cfg['PLC'].getint('db_ist'), 0, 3000)
        self.array_soll = Smarttags.RealArray(self.plc, self.cfg['PLC'].getint('db_soll'), 0, 3000)
        self.var_url_01 = Smarttags.String(self.plc, self.cfg['PLC'].getint('db_out'), 0, 64)
        self.var_url_02 = Smarttags.String(self.plc, self.cfg['PLC'].getint('db_out'), 66, 64)
        self.var_url_03 = Smarttags.String(self.plc, self.cfg['PLC'].getint('db_out'), 132, 64)
        self.anf_soll = Smarttags.Bool(self.plc, self.cfg['PLC'].getint('db_out'), 198, 0)
        self.anf_kompl = Smarttags.Bool(self.plc, self.cfg['PLC'].getint('db_out'), 198, 1)
        self.bg_color = Smarttags.String(self.plc, self.cfg['PLC'].getint('db_out'), 200, 8)
        self.soll_color = Smarttags.String(self.plc, self.cfg['PLC'].getint('db_out'), 208, 8)
        self.ist_color = Smarttags.String(self.plc, self.cfg['PLC'].getint('db_out'), 216, 8)
        self.soll_linewidth = Smarttags.Int(self.plc, self.cfg['PLC'].getint('db_out'), 224)
        self.ist_linewidth = Smarttags.Int(self.plc, self.cfg['PLC'].getint('db_out'), 226)
        self.bez_x = Smarttags.String(self.plc, self.cfg['PLC'].getint('db_out'), 228, 16)
        self.bez_y = Smarttags.String(self.plc, self.cfg['PLC'].getint('db_out'), 246, 16)
        self.size_x = Smarttags.Int(self.plc, self.cfg['PLC'].getint('db_out'), 264)
        self.size_y = Smarttags.Int(self.plc, self.cfg['PLC'].getint('db_out'), 266)
        self.plot_done_soll = Smarttags.Bool(self.plc, self.cfg['PLC'].getint('db_in'), 0, 1)
        self.plot_done_kompl = Smarttags.Bool(self.plc, self.cfg['PLC'].getint('db_in'), 0, 2)
        self.dpi = 100

    def submit_data(self, datay):
        done = False
        while not done:
            try:
                self.array_soll.write(datay)
                done = True
            except Exception as e:
                print(e)

    def read_soll_ist_data(self):
        done = False
        while not done:
            try:
                soll = self.array_soll.read()
                ist = self.array_ist.read()
                done = True
            except Exception as e:
                print(e)
        return soll, ist

    def plot_soll(self):
        soll = self.array_soll.read()
        fig = plt.figure(dpi=self.dpi, figsize=(self.size_x.read() / self.dpi, self.size_y.read() / self.dpi))
        fig.subplots_adjust(top=self.cfg['PLCGRAPH'].getfloat('adjust_top'),
                            bottom=self.cfg['PLCGRAPH'].getfloat('adjust_bottom'),
                            left=self.cfg['PLCGRAPH'].getfloat('ajdust_left'),
                            right=self.cfg['PLCGRAPH'].getfloat('adjust_right'),
                            hspace=self.cfg['PLCGRAPH'].getfloat('adjust_hspace'),
                            wspace=self.cfg['PLCGRAPH'].getfloat('adjust_wspace'))
        ax = fig.add_subplot()
        ax.set_facecolor('#' + self.bg_color.read())
        ax.set_ylabel(self.bez_y.read())
        ax.set_xlabel(self.bez_x.read())
        ax.plot([i for i in range(len(soll))], soll, linewidth=self.soll_linewidth.read(),
                color='#' + self.soll_color.read())
        fig.savefig(self.var_url_02.read(), dpi=self.dpi)
        fig.savefig(self.var_url_03.read(), dpi=self.dpi)

    def plot_kompl(self):
        filename = get_last_trace(self.cfg['PLC']['ip_cu320'], './export/trace.csv')
        header = None
        data = []
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for i, row in enumerate(reader):
                if i == 0:
                    header = row
                else:
                    data.append(row)

        khz = self.cfg['GRAPH'].getint('resolution_khz')
        soll_data = self.array_soll.read()
        soll_x = [(count + 1) / (khz * 1000) for count in range(len(soll_data))]

        ist_x = [float(i[self.cfg['GRAPH'].getint('trace_x_index')].replace(',', '.')) for i in data]
        ist_data = [float(i[self.cfg['GRAPH'].getint('trace_y_index')].replace(',', '.')) for i in data]

        fig = plt.figure(dpi=self.dpi, figsize=(self.size_x.read() / self.dpi, self.size_y.read() / self.dpi))
        fig.subplots_adjust(top=self.cfg['PLCGRAPH'].getfloat('adjust_top'),
                            bottom=self.cfg['PLCGRAPH'].getfloat('adjust_bottom'),
                            left=self.cfg['PLCGRAPH'].getfloat('ajdust_left'),
                            right=self.cfg['PLCGRAPH'].getfloat('adjust_right'),
                            hspace=self.cfg['PLCGRAPH'].getfloat('adjust_hspace'),
                            wspace=self.cfg['PLCGRAPH'].getfloat('adjust_wspace'))
        ax = fig.add_subplot()
        ax.set_facecolor('#' + self.bg_color.read())
        ax.set_ylabel(self.bez_y.read())
        ax.set_xlabel(self.bez_x.read())
        ax.plot(x, soll_data, linewidth=self.soll_linewidth.read(),
                color='#' + self.soll_color.read())

        ax.plot(x, ist_data, linewidth=self.ist_linewidth.read(),
                color='#' + self.ist_color.read())
        fig.savefig(self.var_url_02.read(), dpi=self.dpi)
        fig.savefig(self.var_url_03.read(), dpi=self.dpi)

    def run(self):
        self.parent.statusbar.showMessage(self.cfg['STRINGS']['status_plc_connecting'])
        self.sleep(1)
        if self.plc.connect():
            self.parent.statusbar.showMessage(self.cfg['STRINGS']['status_plc_connected'])
        else:
            self.parent.statusbar.showMessage(self.cfg['STRINGS']['status_plc_disconnected'])

        while True:
            try:
                if not self.plc.connect():
                    self.parent.statusbar.showMessage(self.cfg['STRINGS']['status_plc_disconnected'])
                else:
                    self.keep_alive.write(not self.keep_alive.read())
                    if self.anf_soll.read():
                        self.plot_soll()
                        self.anf_soll.write(False)
                        self.plot_done_soll.write(True)
                    elif self.anf_kompl.read():
                        self.plot_kompl()
                        self.anf_kompl.write(False)
                        self.plot_done_kompl.write(True)


            except Exception as e:
                print(e)
            self.msleep(200)


class Graph(pg.PlotWidget):
    def __init__(self, cfg):
        self.cfg = cfg
        super(Graph, self).__init__(enableMenu=self.cfg['GRAPH'].getboolean('enable_menu'))
        self.setMouseEnabled(x=self.cfg['GRAPH'].getboolean('mouseenable_x'),
                             y=self.cfg['GRAPH'].getboolean('mouseenable_x'))
        self.enableAutoRange(x=self.cfg['GRAPH'].getboolean('autorange_x'),
                             y=self.cfg['GRAPH'].getboolean('autorange_x'))
        self.showGrid(x=self.cfg['GRAPH'].getboolean('grid_x'), y=self.cfg['GRAPH'].getboolean('grid_y'))
        self.setXLabel(self.cfg['GRAPH']['name_ax_x'])
        self.setYLabel(self.cfg['GRAPH']['name_ax_y'])
        self.addLegend()
        self.pen_legend = pg.mkPen(color=ImageColor.getrgb('#' + self.cfg['GRAPH']['color_legend']),
                                   width=self.cfg['GRAPH'].getint('width_legend'))
        self.setBackground(self.cfg['GRAPH']['background_color'])

    def setXLabel(self, text):
        self.setLabel('bottom', text, color=self.cfg['GRAPH']['color_xlabel'])

    def setYLabel(self, text):
        self.setLabel('left', text, color=self.cfg['GRAPH']['color_ylabel'])


class GraphMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, plc, config, *args, **kwargs):
        super(GraphMainWindow, self).__init__(*args, **kwargs)
        self.current_data_x = []
        self.current_data_y = []
        self.compare_data_x = []
        self.soll_data_y = []
        self.ist_data_y = []
        self.cfg = config
        self.plc = PLC(self)
        self.plc.start()

        self.setupUi(self)
        self.setupWindow()
        self.connect_componets()

        self.graph = Graph(self.cfg)

        self.graphLayout.addWidget(self.graph)

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
        self.btn_load.clicked.connect(self.handle_btn_load)
        self.btn_save.clicked.connect(self.handle_btn_save)
        self.btn_compare.clicked.connect(self.handle_btn_compare)
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
                    self.current_data_x.append(float(row[0].replace(',', '.')))
                    self.current_data_y.append(float(row[1].replace(',', '.')))

            self.statusbar.showMessage(self.cfg['STRINGS']['status_csv_loaded'])
            self.graph.clear()
            self.graph.plot(self.current_data_x, self.current_data_y, pen=self.pen_current,
                            name=self.cfg['STRINGS']['graph_current_label'])
            self.graph.getPlotItem().legend.setPen(self.graph.pen_legend)
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
        self.graph.clear()
        self.current_data_x = []
        self.current_data_y = []
        khz = self.cfg['GRAPH'].getint('resolution_khz')
        self.soll_data_y, self.ist_data_y = self.plc.read_soll_ist_data()
        self.graph.setTitle(self.cfg['STRINGS']['graph_title_compare'])
        self.graph.plot([(count + 1) / (khz * 1000) for count in range(len(self.ist_data_y))], self.ist_data_y,
                        pen=self.pen_ist, name=self.cfg['STRINGS']['graph_ist_label'])
        self.graph.plot([(count + 1) / (khz * 1000) for count in range(len(self.soll_data_y))], self.soll_data_y,
                        pen=self.pen_soll, name=self.cfg['STRINGS']['graph_soll_label'])
        self.graph.getPlotItem().legend.setPen(self.graph.pen_legend)
        self.statusbar.showMessage(self.cfg['STRINGS']['status_plc_data_loaded'])

    def handle_btn_tool_cursor(self):
        if self.btn_tool_cursor.isChecked():
            self.btn_tool_edit.setChecked(False)
            self.graph.cursor_mode = True
            self.graph.edit_mode = False
        else:
            self.graph.cursor_mode = False
            self.graph.cursor.clear()

    def handle_btn_tool_edit(self):
        if self.btn_tool_edit.isChecked():
            self.btn_tool_cursor.setChecked(False)
            self.graph.edit_mode = True
            self.graph.cursor_mode = False
        else:
            self.graph.edit_mode = False

    def handle_btn_submit_plc(self):
        if self.current_data_y:
            self.plc.submit_data(self.current_data_y)
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
