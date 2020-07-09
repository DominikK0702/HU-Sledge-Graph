import sys
import csv
from PIL import ImageColor
from SinamicsExport import get_last_trace
from configparser import ConfigParser
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QDesktopWidget
from MainWindow import Ui_MainWindow
from InfoDialog import Ui_InfoDialog
from PLC import PLC
from GraphWidget import Graph
from TraceWidget import TracePlot
import pyqtgraph as pg
import TraceHelper


class GraphMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, config, *args, **kwargs):
        super(GraphMainWindow, self).__init__(*args, **kwargs)
        self.current_data_x = []
        self.current_data_y = []
        self.compare_data_x = []
        self.compare_soll_data_y = []
        self.ist_data_y = []
        self.edit_mode = False
        self.current_file_name = ''
        self.current_trace = TraceHelper.Trace()

        self.compare_trace = TraceHelper.Trace()
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


    def reset_tools(self):
        self.btn_tool_edit.setChecked(False)
        self.btn_tool_cursor.setChecked(False)
        self.graph.cursor.enabled(False)


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
        self.btn_autorange.clicked.connect(self.graph.auto_range)

        self.actionInfo.triggered.connect(self.show_dialoginfo)

    def show_dialoginfo(self):
        self.info_dialog = QMainWindow(self)
        self.info_ui = Ui_InfoDialog()
        self.info_ui.setupUi(self.info_dialog)
        self.info_dialog.show()

    def handle_btn_load(self):
        options = QFileDialog.Options()
        if not self.cfg['GUI'].getboolean('use_native_filedialog'):
            options |= QFileDialog.DontUseNativeDialog
        fileName, fileType = QFileDialog.getOpenFileName(self, self.cfg['STRINGS']['csv_load_title'], "",
                                                         "Puls CSV (*.pcsv)",
                                                         options=options)
        self.current_data_x = []
        self.current_data_y = []
        if fileName:
            try:
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
                self.graph.setTitle(fileName.split('/')[-1])
                self.current_file_name = fileName.split('/')[-1]
            except Exception as e:
                self.statusbar.showMessage(str(e))

    def handle_btn_save(self):
        options = QFileDialog.Options()
        if not self.cfg['GUI'].getboolean('use_native_filedialog'):
            options |= QFileDialog.DontUseNativeDialog
        fileName, fileType = QFileDialog.getSaveFileName(self, self.cfg['STRINGS']['csv_save_title'], "",
                                                         "Puls CSV (*.pcsv)",
                                                         options=options)
        if fileName:
            with open(fileName, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file, delimiter=';')
                x = TraceHelper.offset_x_soll(self.current_data_y,0)
                for count, i in enumerate(self.current_data_y):
                    writer.writerow(
                        [format(x[count], f'.{self.cfg["GRAPH"]["csv_export_float_precision_x"]}f'),
                         format(i, f'.{self.cfg["GRAPH"]["csv_export_float_precision_y"]}f')])

            self.statusbar.showMessage(self.cfg['STRINGS']['status_csv_saved'])

    def handle_btn_compare(self):
        filename = get_last_trace(self.cfg['PLC']['ip_cu320'], './export/trace.csv')
        if not filename:
            return self.statusbar.showMessage(self.cfg['STRINGS']['status_trace_connnection_error'])
        self.compare_trace.load_trace_csv(filename)
        self.compare_soll_data_y = self.plc.array_soll.read()
        self.reset_tools()
        self.graph.clear()
        self.graph.setTitle(self.cfg['STRINGS']['graph_title_compare'])
        self.current_data_x = []
        self.current_data_y = []
        self.graph.plot_compare(self.compare_trace, self.compare_soll_data_y)
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
                                                         "Trace CSV (*.tcsv);;Trace ACX (*.ACX.GZ)",
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

    def handle_btn_trace_save(self):
        if self.trace_plot.trace.datapoints <= 0:
            return
        options = QFileDialog.Options()
        if not self.cfg['GUI'].getboolean('use_native_filedialog'):
            options |= QFileDialog.DontUseNativeDialog
        fileName, fileType = QFileDialog.getSaveFileName(self, self.cfg['STRINGS']['trace_save_title'], "",
                                                         "Trace CSV (*.tcsv)",
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
