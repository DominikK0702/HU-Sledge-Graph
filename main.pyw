import glob
import sys
import csv
import os
from PIL import ImageColor
from SinamicsExport import get_last_trace
from configparser import ConfigParser
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QDesktopWidget, QTableWidgetItem, QDialog, QDialogButtonBox, QShortcut
from MainWindow import Ui_MainWindow
from InfoDialog import Ui_InfoDialog
from QtInfo import Ui_QtInfo
from CSVExportDialog import Ui_Dialog
from PLC import PLC
from GraphWidget import Graph
from TraceWidget import TracePlot
import pyqtgraph as pg
import TraceHelper
from Protocol import ProtocolGen
from LangConfig import LanguageConfig
from loguru import logger

# Single Instance
from tendo import singleton
# Raises Exception if theres already another Instance
me = singleton.SingleInstance()


# todo Pulse Evaluate switch viewmode


class GraphMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, config, *args, **kwargs):
        super(GraphMainWindow, self).__init__(*args, **kwargs)
        self.cfg = config
        self.current_data_x = []
        self.current_data_y = []
        self.compare_soll_data_y = []
        self.current_file_name = ''
        self.compare_trace = TraceHelper.Trace()
        self.current_protocol = None
        # Set Gui Language from Plc
        self.languageCfg = LanguageConfig(self.cfg['GUI'].get('language_file'),
                                          default_language='DE' if PLC(self).language.read() else 'EN')

        self.setupUi(self)
        self.setupWindow()

        self.plc = PLC(self)
        self.plc.start()

        self.trace_plot = TracePlot(self.cfg, self)
        self.graph = Graph(self.cfg, self)

        self.tab_layout_pulse.addWidget(self.graph)
        self.tab_layout_trace.addWidget(self.trace_plot)

        self.connect_componets()

        self.pen_current = pg.mkPen(color=ImageColor.getrgb('#' + self.cfg['GRAPH']['color_current']),
                                    width=self.cfg['GRAPH'].getint('width_current'))
        self.undo_shortcut = QShortcut(QtGui.QKeySequence("Ctrl+Z"), self)
        self.undo_shortcut.activated.connect(self.handle_undo_shortcut)
        self.show()

    def handle_undo_shortcut(self):
        if self.tabWidget.currentIndex() == 0 and self.graph.edit_mode:
            # Pulse Tab and edit mode active
            if self.graph.bez is not None:
                self.graph.bez.undo()

    def setupStrings(self):
        # Window Title
        self.setWindowTitle(self.languageCfg.get('title'))

        # Menu bar
        self.menuFile.setTitle(self.languageCfg.get('gui_menubar_file'))
        self.actionExit.setText(self.languageCfg.get('gui_menubar_file_exit'))
        self.menuInfo.setTitle(self.languageCfg.get('gui_menubar_info'))
        self.actionInfo.setText(self.languageCfg.get('gui_menubar_info_info'))
        self.actionAbout_Qt.setText(self.languageCfg.get('gui_menubar_info_aboutqt'))

        # Tab Widget View
        self.tabWidget.setTabText(0, self.languageCfg.get('gui_tab_pulse_title'))
        self.tabWidget.setTabText(1, self.languageCfg.get('gui_tab_trace_title'))
        self.tabWidget.setTabText(2, self.languageCfg.get('gui_tab_protocol_title'))
        # Tab Widget Tools
        self.tabWidgetTools.setTabText(0, self.languageCfg.get('gui_tab_pulse_title'))
        self.tabWidgetTools.setTabText(1, self.languageCfg.get('gui_tab_trace_title'))
        self.tabWidgetTools.setTabText(2, self.languageCfg.get('gui_tab_protocol_title'))
        # Pulse
        self.groupBox_imexport.setTitle(self.languageCfg.get('gui_box_pulse_imexport'))
        self.groupBox_Evaluate.setTitle(self.languageCfg.get('gui_box_pulse_evaluate'))
        self.groupBox_Tools.setTitle(self.languageCfg.get('gui_box_pulse_tools'))
        self.groupBox_PulsSettings.setTitle(self.languageCfg.get('gui_box_pulse_settings'))
        self.groupBox_PLC.setTitle(self.languageCfg.get('gui_box_pulse_plc'))

        self.btn_load.setText(self.languageCfg.get('gui_btn_pulse_import'))
        self.btn_save.setText(self.languageCfg.get('gui_btn_pulse_export'))
        self.btn_compare.setText(self.languageCfg.get('gui_btn_pulse_compare'))
        self.btn_tool_cursor.setText(self.languageCfg.get('gui_btn_pulse_cursor'))
        self.btn_tool_edit.setText(self.languageCfg.get('gui_btn_pulse_edit'))
        self.btn_tool_scale.setText(self.languageCfg.get('gui_btn_pulse_scale'))
        self.radioButton_standard.setText(self.languageCfg.get('gui_rb_pulse_setting_default'))
        self.radioButton_y_linked.setText(self.languageCfg.get('gui_rb_pulse_setting_y_linked'))
        self.radioButton_interpolate.setText(self.languageCfg.get('gui_rb_pulse_setting_interpolate'))
        self.spinBox_PulseEditPointCount.setSuffix(
            ' ' + self.languageCfg.get('gui_spinbox_pulse_editpointcount_suffix'))
        self.btn_submit_plc.setText(self.languageCfg.get('gui_btn_pulse_submit_plc'))
        self.btn_autorange.setText(self.languageCfg.get('gui_btn_pulse_autorange'))
        self.cb_pulse_view.setItemText(0, self.languageCfg.get('gui_select_pulse_view_single'))
        self.cb_pulse_view.setItemText(1, self.languageCfg.get('gui_select_pulse_view_multi'))
        # Trace
        self.groupBox_trace_imexport.setTitle(self.languageCfg.get('gui_box_trace_imexport'))
        self.groupBox_trace_view.setTitle(self.languageCfg.get('gui_box_trace_view'))
        self.groupBox_trace_axis.setTitle(self.languageCfg.get('gui_box_trace_axis'))

        self.btn_trace_loadfile.setText(self.languageCfg.get('gui_btn_trace_load'))
        self.btn_trace_loadlast.setText(self.languageCfg.get('gui_btn_trace_loadlast'))
        self.btn_trace_save.setText(self.languageCfg.get('gui_btn_trace_save'))
        self.btn_trace_autorange.setText(self.languageCfg.get('gui_btn_trace_autorange'))
        self.cb_pulse_view.setItemText(0, self.languageCfg.get('gui_cb_trace_view_multi'))
        self.cb_pulse_view.setItemText(1, self.languageCfg.get('gui_cb_trace_view_single'))

        self.cb_trace_ax_way.setText(self.languageCfg.get('gui_cb_trace_ax_way'))
        self.cb_trace_ax_vel.setText(self.languageCfg.get('gui_cb_trace_ax_velocity'))
        self.cb_trace_ax_voltage.setText(self.languageCfg.get('gui_cb_trace_ax_voltage'))
        self.cb_trace_ax_acc_way.setText(self.languageCfg.get('gui_cb_trace_ax_acc_way'))
        self.cb_trace_ax_acc_vel.setText(self.languageCfg.get('gui_cb_trace_ax_acc_vel'))
        self.cb_trace_ax_acc_vel_filtered.setText(self.languageCfg.get('gui_cb_trace_ax_acc_vel_filtered'))
        # Protocol
        self.groupBox_protocol_import.setTitle(self.languageCfg.get('gui_box_protocol_import'))
        self.groupBox_protocol_pdf.setTitle(self.languageCfg.get('gui_box_protocol_pdf'))

        self.btn_protocol_import.setText(self.languageCfg.get('gui_btn_protocol_import'))
        self.btn_protocol_last.setText(self.languageCfg.get('gui_btn_protocol_import_last'))
        self.btn_protocol_pdfgen.setText(self.languageCfg.get('gui_btn_protocol_generate_pdf'))
        self.label_protocol_trigger.setText(self.languageCfg.get('gui_title_protocol_trigger'))
        self.label_protocol_general.setText(self.languageCfg.get('gui_title_protocol_general'))
        self.tableWidget_general.verticalHeaderItem(0).setText(self.languageCfg.get('gui_protocol_type') + ':')
        self.tableWidget_general.verticalHeaderItem(1).setText(self.languageCfg.get('gui_protocol_nr') + ':')
        self.tableWidget_general.verticalHeaderItem(2).setText(self.languageCfg.get('gui_protocol_comment') + ':')
        self.tableWidget_general.verticalHeaderItem(3).setText(self.languageCfg.get('gui_protocol_operator') + ':')
        self.tableWidget_general.verticalHeaderItem(4).setText(self.languageCfg.get('gui_protocol_start_pos') + ':')
        self.tableWidget_general.verticalHeaderItem(5).setText(self.languageCfg.get('gui_protocol_end_pos') + ':')
        self.tableWidget_general.verticalHeaderItem(6).setText(self.languageCfg.get('gui_protocol_load') + ':')
        self.tableWidget_general.verticalHeaderItem(7).setText(self.languageCfg.get('gui_protocol_timestamp') + ':')

    def setupWindow(self):
        self.setupStrings()
        self.setWindowIcon(QtGui.QIcon(self.cfg['GUI']['window_icon']))
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
        self.btn_protocol_last.clicked.connect(self.handle_load_last_protocol)
        self.btn_protocol_import.clicked.connect(self.handle_load_protocol)
        self.btn_protocol_pdfgen.clicked.connect(self.handle_generate_pdf_protocol)

        self.btn_tool_scale.clicked.connect(self.handle_scale)

        self.btn_protocol_export_csv.clicked.connect(self.handle_export_csv)

        self.actionInfo.triggered.connect(self.show_dialoginfo)
        self.actionAbout_Qt.triggered.connect(self.show_qtinfo)

    def export_csv(self, protocol=None):
        options = QFileDialog.Options()
        if not self.cfg['GUI'].getboolean('use_native_filedialog'):
            options |= QFileDialog.DontUseNativeDialog
        fileName, fileType = QFileDialog.getSaveFileName(self, "Save CSV Export", "",
                                                         "CSV Export (*.csv)",
                                                         options=options)
        if fileName:
            if protocol is None:
                protocol = self.current_protocol.json.data
            csv_data = []
            if self.export_ui.checkBox_axis_01.isChecked():
                # Soll Kurve
                csv_data.append(protocol.get('puls_x'))
                csv_data.append(protocol.get('puls_y'))
            if self.export_ui.checkBox_axis_02.isChecked():
                # Geschwindigkeit
                csv_data.append([i * 1000 for i in protocol.get('trace_x')])
                csv_data.append([i / 60 for i in protocol.get('trace_vel')])
            if self.export_ui.checkBox_axis_03.isChecked():
                # Weg
                csv_data.append([i * 1000 for i in protocol.get('trace_x')])
                csv_data.append(protocol.get('trace_way'))
            if self.export_ui.checkBox_axis_04.isChecked():
                # Beschl. Weg
                csv_data.append([i * 1000 for i in protocol.get('trace_x')])
                csv_data.append([(i / 60) * 0.981 for i in protocol.get('trace_acc_way')])
            if self.export_ui.checkBox_axis_05.isChecked():
                # Beschl. Geschw.
                csv_data.append([i * 1000 for i in protocol.get('trace_x')])
                csv_data.append([(i / 60) * 0.981 for i in protocol.get('trace_acc_vel')])
            if self.export_ui.checkBox_axis_06.isChecked():
                # Beschl. Geschw. Filtered
                csv_data.append([i * 1000 for i in protocol.get('trace_x')])
                csv_data.append([(i / 60) * 0.981 for i in protocol.get('trace_acc_vel_filt')])
            if self.export_ui.checkBox_axis_07.isChecked():
                # Voltage
                csv_data.append(protocol.get('trace_x'))
                csv_data.append(protocol.get('trace_voltage'))

            delimiter = ';'
            if self.export_ui.comboBox_csv_sep.currentIndex() == 0:
                # Semicolon ; Seperator
                delimiter = ';'
            elif self.export_ui.comboBox_csv_sep.currentIndex() == 1:
                # Comma , Seperator
                delimiter = ','
            elif self.export_ui.comboBox_csv_sep.currentIndex() == 2:
                # Tab \t Seperator
                delimiter = '\t'

            float_point = '.'
            if self.export_ui.comboBox_float_point.currentIndex() == 0:
                float_point = '.'
            elif self.export_ui.comboBox_float_point.currentIndex() == 1:
                float_point = ','


            empty = ''
            if self.export_ui.comboBox_no_value_placeholder.currentIndex() == 0:
                empty = ''
            elif self.export_ui.comboBox_no_value_placeholder.currentIndex() == 1:
                empty = '{:.10f}'.format(0.0).replace('.',float_point)

            with open(fileName, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=delimiter)
                for c in range(len(csv_data[-1])):
                    row = []
                    for i in csv_data:
                        try:
                            row.append('{:.10f}'.format(i[c]).replace('.',float_point))
                        except Exception as e:
                            row.append(empty)
                    writer.writerow(row)

            logger.debug("CSV Exported.")
        else:
            logger.debug("CSV Export aborted.")

    def handle_export_csv(self):
        # check if there is any protocol
        if self.current_protocol:
            self.export_dialog = QDialog(self)
            self.export_ui = Ui_Dialog()
            self.export_ui.setupUi(self.export_dialog)
            self.export_ui.groupBox.setTitle(self.languageCfg.get('gui_csvexport_dialog_group_title'))
            self.export_ui.buttonBox.button(QDialogButtonBox.Ok).setText(self.languageCfg.get('gui_csvexport_dialog_group_ok'))
            self.export_ui.buttonBox.button(QDialogButtonBox.Cancel).setText(self.languageCfg.get('gui_csvexport_dialog_group_cancel'))

            self.export_ui.label_csv_sep.setText(self.languageCfg.get('gui_csvexport_dialog_label_csv_sep'))
            self.export_ui.label_float_point.setText(self.languageCfg.get('gui_csvexport_dialog_label_csv_float_point'))
            self.export_ui.label_no_value_placeholder.setText(self.languageCfg.get('gui_csvexport_dialog_label_csv_placeholder'))
            self.export_ui.label_warning.setText(self.languageCfg.get('gui_csvexport_dialog_csv_warning'))
            self.export_ui.textBrowser_disclaimer.setText(self.languageCfg.get('gui_csvexport_dialog_csv_disclaimer'))

            self.export_ui.checkBox_axis_01.setText(self.languageCfg.get('gui_csvexport_dialog_axis01'))
            self.export_ui.checkBox_axis_02.setText(self.languageCfg.get('gui_csvexport_dialog_axis02'))
            self.export_ui.checkBox_axis_03.setText(self.languageCfg.get('gui_csvexport_dialog_axis03'))
            self.export_ui.checkBox_axis_04.setText(self.languageCfg.get('gui_csvexport_dialog_axis04'))
            self.export_ui.checkBox_axis_05.setText(self.languageCfg.get('gui_csvexport_dialog_axis05'))
            self.export_ui.checkBox_axis_06.setText(self.languageCfg.get('gui_csvexport_dialog_axis06'))
            self.export_ui.checkBox_axis_07.setText(self.languageCfg.get('gui_csvexport_dialog_axis07'))
            self.export_dialog.show()
            self.export_ui.buttonBox.accepted.connect(self.export_csv)
            logger.debug("CSV Exportdialog displayed.")
        else:
            options = QFileDialog.Options()
            if not self.cfg['GUI'].getboolean('use_native_filedialog'):
                options |= QFileDialog.DontUseNativeDialog
            fileName, fileType = QFileDialog.getOpenFileName(self, "Open PJson", "",
                                                             "PJSON Protocol (*.pjson)",
                                                             options=options)
            if fileName:
                prot = ProtocolGen.ProtocolJson()
                prot.load(fileName)
                self.export_dialog = QDialog(self)
                self.export_ui = Ui_Dialog()
                self.export_ui.setupUi(self.export_dialog)
                self.export_ui.groupBox.setTitle(self.languageCfg.get('gui_csvexport_dialog_group_title'))
                self.export_ui.buttonBox.button(QDialogButtonBox.Ok).setText(
                    self.languageCfg.get('gui_csvexport_dialog_group_ok'))
                self.export_ui.buttonBox.button(QDialogButtonBox.Cancel).setText(
                    self.languageCfg.get('gui_csvexport_dialog_group_cancel'))
                self.export_ui.label_csv_sep.setText(self.languageCfg.get('gui_csvexport_dialog_label_csv_sep'))
                self.export_ui.label_float_point.setText(
                    self.languageCfg.get('gui_csvexport_dialog_label_csv_float_point'))
                self.export_ui.label_no_value_placeholder.setText(
                    self.languageCfg.get('gui_csvexport_dialog_label_csv_placeholder'))
                self.export_ui.checkBox_axis_01.setText(self.languageCfg.get('gui_csvexport_dialog_axis01'))
                self.export_ui.checkBox_axis_02.setText(self.languageCfg.get('gui_csvexport_dialog_axis02'))
                self.export_ui.checkBox_axis_03.setText(self.languageCfg.get('gui_csvexport_dialog_axis03'))
                self.export_ui.checkBox_axis_04.setText(self.languageCfg.get('gui_csvexport_dialog_axis04'))
                self.export_ui.checkBox_axis_05.setText(self.languageCfg.get('gui_csvexport_dialog_axis05'))
                self.export_ui.checkBox_axis_06.setText(self.languageCfg.get('gui_csvexport_dialog_axis06'))
                self.export_ui.checkBox_axis_07.setText(self.languageCfg.get('gui_csvexport_dialog_axis07'))
                self.export_dialog.show()
                self.export_ui.buttonBox.accepted.connect(lambda: self.export_csv(prot.json.data))
                logger.debug("CSV Exportdialog displayed.")
            else:
                logger.debug("CSV Exportdialog canceled due no Trace loaded")

    def handle_scale(self):
        factor = self.doubleSpinBox_scale_factor.value()
        if factor == 1.0:
            logger.debug("Scale Pulse canceled because x1.0 doesnt do anything")
            return
        else:
            if len(self.current_data_y) <= 0:
                logger.debug("Scale Pulse canceled because no data to scale")
                return
            for index, i in enumerate(self.current_data_y):
                self.current_data_y[index] = i * factor

            self.reset_tools()
            self.graph.clear()

            self.graph.plot(self.current_data_x, self.current_data_y, pen=self.pen_current,
                            name=self.languageCfg.get('graph_current_label'))
            self.graph.getPlotItem().legend.setPen(self.graph.pen_legend)

            self.graph.enableAutoRange(x=True, y=True)
            logger.debug(f"Scaled Pulse to x{factor}")

    def draw_protocol(self, protocol):
        # general
        self.tableWidget_general.setItem(0, 0, QTableWidgetItem(protocol.json.data['versuchstyp']))
        self.tableWidget_general.setItem(1, 0, QTableWidgetItem(protocol.json.data['versuchsnummer']))
        self.tableWidget_general.setItem(2, 0, QTableWidgetItem(protocol.json.data['kommentar']))
        self.tableWidget_general.setItem(3, 0, QTableWidgetItem(protocol.json.data['bediener']))
        self.tableWidget_general.setItem(4, 0, QTableWidgetItem(str(protocol.json.data['startpos']) + ' mm'))
        self.tableWidget_general.setItem(5, 0, QTableWidgetItem(str(protocol.json.data['endpos']) + ' mm'))
        self.tableWidget_general.setItem(6, 0, QTableWidgetItem(str(protocol.json.data['zuladung']) + ' kg'))

        try:
            timestamp = str(protocol.json.data['timestamp'])
        except Exception as e:
            logger.debug("Protocol: using outdated file version (still supported but timestamp is missing)")
            timestamp = "Outdated File Version"
        self.tableWidget_general.setItem(7, 0, QTableWidgetItem(timestamp))

        # triggers
        for index, trig in enumerate(protocol.json.data['trigger'].items()):
            self.tableWidget_trigger.setItem(index, 0, QTableWidgetItem(trig[1]['name']))
            self.tableWidget_trigger.setItem(index, 1, QTableWidgetItem(str(trig[1]['zeit'] / 1e6) + ' ms'))
            self.tableWidget_trigger.setItem(index, 2, QTableWidgetItem(self.languageCfg.get('gui_true') if trig[1]['enabled'] else self.languageCfg.get('gui_false')))

        self.trace_plot.load_trace_protocol(protocol)

        self.reset_tools()
        self.graph.clear()
        self.graph.setTitle(self.languageCfg.get('prototcol_pulse_title'))

        # Plot Soll
        offset_soll = 50
        scaled_soll_data = protocol.json.data['puls_y']
        soll_x = [i * 1000 for i in TraceHelper.offset_x_soll(scaled_soll_data, offset_soll)]
        self.graph.plot(soll_x,
                        scaled_soll_data,
                        pen=self.graph.pen_soll, name=self.cfg['STRINGS']['graph_soll_label'])
        pulsdauer = soll_x[-1] + 50

        ist_x = [i * 1000 for i in self.trace_plot.trace.get_axis_time() if i * 1000 <= pulsdauer]
        ist_y = [i / 60 for i in self.trace_plot.trace.get_axis_acc_from_speed(filtered=True)[:len(ist_x)]]

        # Plot Ist
        self.graph.plot(ist_x, ist_y,
                        pen=self.graph.pen_ist, name=self.cfg['STRINGS']['graph_ist_label'])

        self.graph.auto_range()
        self.graph.setXLabel(self.cfg['GRAPH']['name_ax_compare_x'])
        self.graph.setYLabel(self.cfg['GRAPH']['name_ax_compare_y'])
        self.graph.getPlotItem().legend.setPen(self.graph.pen_legend)
        self.tabWidget.setCurrentIndex(2)
        logger.debug("Protocoll loaded.")

    def handle_generate_pdf_protocol(self):
        if self.current_protocol:
            options = QFileDialog.Options()
            if not self.cfg['GUI'].getboolean('use_native_filedialog'):
                options |= QFileDialog.DontUseNativeDialog
            fileName, fileType = QFileDialog.getSaveFileName(self, "Protokoll PDF speichern", "",
                                                             "Protokoll PDF (*.pdf)",
                                                             options=options)
            if fileName:
                pdf = ProtocolGen.ProtocolPDF(fileName, self.current_protocol.json)
                logger.debug(f"Protocol pdf generated: {fileName}")
                self.statusbar.showMessage('Protokoll PDF erstellt.')
        else:
            logger.debug("No protocol to generate pdf.")
            self.statusbar.showMessage('Kein Protokoll geladen um PDF zu erstellen.')

    def handle_load_last_protocol(self):
        done = False
        while not done:
            path = self.plc.path_json_export.read()
            done = True
        # path = ''
        if path == '':
            path = "./export/protocols"
            logger.debug(f"'No path for protocol load from plc. Falling back to default: {path}")

        filename = max(glob.glob(path + '/*'), key=os.path.getmtime)
        if filename:
            protocol = ProtocolGen.ProtocolJson()
            protocol.load(filename)
            self.current_protocol = protocol
            self.draw_protocol(self.current_protocol)
            self.graph.compare_mode = True
            self.graph.pulse_mode = False
            logger.debug("Latest protocol loaded.")
            self.statusbar.showMessage('Protokoll des letzten Versuchs geladen.')
        else:
            logger.error("Loading latest protocol failed.")
            self.statusbar.showMessage('Protokoll des letzten Versuchs laden gescheitert.')

    def handle_load_protocol(self):
        options = QFileDialog.Options()
        if not self.cfg['GUI'].getboolean('use_native_filedialog'):
            options |= QFileDialog.DontUseNativeDialog
        fileName, fileType = QFileDialog.getOpenFileName(self, self.cfg['STRINGS']['csv_load_title'], "",
                                                         "Protokoll JSON (*.pjson)",
                                                         options=options)
        if fileName:
            protocol = ProtocolGen.ProtocolJson()
            protocol.load(fileName)
            self.current_protocol = protocol
            self.draw_protocol(self.current_protocol)
            self.graph.compare_mode = True
            self.graph.pulse_mode = False
            logger.debug(f"Protocol loaded from file: {fileName}")
        else:
            logger.debug("Load protocol: no filename defined")

    def show_dialoginfo(self):
        self.info_dialog = QMainWindow(self)
        self.info_ui = Ui_InfoDialog()
        self.info_ui.setupUi(self.info_dialog)
        self.info_ui.label.setPixmap(QtGui.QPixmap('./assets/logo.png'))
        self.info_dialog.show()
        logger.debug("Infodialog displayed.")

    def show_qtinfo(self):
        self.qtinfo = QMainWindow(self)
        self.qtinfo_ui = Ui_QtInfo()
        self.qtinfo_ui.setupUi(self.qtinfo)
        self.qtinfo_ui.label.setPixmap(QtGui.QPixmap('./assets/qt.png'))
        self.qtinfo.show()

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
                self.reset_tools()
                self.graph.clear()

                self.graph.plot(self.current_data_x, self.current_data_y, pen=self.pen_current,
                                name=self.cfg['STRINGS']['graph_current_label'])
                self.graph.getPlotItem().legend.setPen(self.graph.pen_legend)
                self.graph.setXLabel(self.cfg['GRAPH']['name_ax_x'])
                self.graph.setYLabel(self.cfg['GRAPH']['name_ax_y'])

                self.graph.enableAutoRange(x=True, y=True)
                self.graph.setTitle(fileName.split('/')[-1])
                self.graph.compare_mode = False
                self.graph.pulse_mode = True
                self.current_file_name = fileName.split('/')[-1]
                logger.debug(f"Pulse file loaded: {self.current_file_name}")
            except Exception as e:
                logger.error(f"Loading pulse failed: {str(e)}")
                self.statusbar.showMessage(str(e))
        else:
            logger.debug("Pulse load: no filename defined")

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
                x = TraceHelper.offset_x_soll(self.current_data_y, 0)
                for count, i in enumerate(self.current_data_y):
                    writer.writerow(
                        [format(x[count], f'.{self.cfg["GRAPH"]["csv_export_float_precision_x"]}f'),
                         format(i, f'.{self.cfg["GRAPH"]["csv_export_float_precision_y"]}f')])
            logger.debug(f"Pulse saved: {fileName}")
            self.statusbar.showMessage(self.cfg['STRINGS']['status_csv_saved'])

        else:
            logger.info("Save pulse: no filename defined")

    def handle_btn_compare(self):
        filename = get_last_trace(self.cfg['PLC']['ip_cu320'], './export/trace.csv')
        if not filename:
            logger.error("Connection to sinamics controller failed.")
            return self.statusbar.showMessage(self.cfg['STRINGS']['status_trace_connnection_error'])
        self.compare_trace.load_trace_csv(filename)
        done = False
        while not done:
            try:
                self.compare_soll_data_y = self.plc.array_soll.read()
                done = True
            except Exception as e:
                logger.error(f"Handle btn compare {str(e)}")

        self.reset_tools()
        self.graph.clear()
        self.graph.setTitle(self.cfg['STRINGS']['graph_title_compare'])
        self.current_data_x = []
        self.current_data_y = []
        self.graph.plot_compare(self.compare_trace, self.compare_soll_data_y)
        logger.debug("Compare target-actual success.")
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
                logger.info(f"Request to submit pulse to plc: {str(e)}")

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
            self.statusbar.showMessage(self.languageCfg.get('status_trace_last_loaded'))
            logger.debug("Latest Tracefile loaded.")
        except Exception as e:
            logger.debug("Loading latest Tracefile failed.")
            self.statusbar.showMessage(self.languageCfg.get('status_trace_last_load_error'), str(e))

    def handle_btn_trace_save(self):
        if self.trace_plot.trace.datapoints <= 0:
            logger.debug(f"Trace not Saved. No datapoints aviable: {self.trace_plot.trace.datapoints}")
            return
        options = QFileDialog.Options()
        if not self.cfg['GUI'].getboolean('use_native_filedialog'):
            options |= QFileDialog.DontUseNativeDialog
        fileName, fileType = QFileDialog.getSaveFileName(self,
                                                         self.languageCfg.get('trace_save_title'),
                                                         self.cfg['GUI']['dir_save_trace'],
                                                         "Trace CSV (*.tcsv)",
                                                         options=options)
        if fileName:
            try:
                self.trace_plot.trace.save_to_csv(fileName, withaccfromspeed=True)
                self.statusbar.showMessage(self.languageCfg.get('status_trace_saved'))
                logger.debug(f"Trace file saved: {fileName}")
            except Exception as e:
                logger.error(f"Failed to save trace file: {fileName}")
                self.statusbar.showMessage(self.languageCfg.get('status_trace_save_error'), str(e))


def main():
    logger.debug('Programm started')
    config = ConfigParser()
    config.read('config.ini', encoding='utf-8')
    logger.debug('Config loaded')
    app = QApplication(sys.argv)
    gui = GraphMainWindow(config)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
