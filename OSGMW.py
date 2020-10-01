from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QFileDialog
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from ui.OSGMainWindow import Ui_OSGMainWindow
from OSGConverter import OSGConverter
from OSGPLC import OSGPLC
from OSGDataContainer import OSGDataContainer
from loguru import logger


class OSGMWPulseToolTab:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.cfgmanager = mainwindow.application.configmanager
        self.connect_components()

    def connect_components(self):
        self.mainwindow.pushButtonImportPulse.clicked.connect(self.import_pulse)

    def import_pulse(self):
        logger.info('Import Pulse')
        options = QFileDialog.Options()
        fileName, fileType = QFileDialog.getOpenFileName(self.mainwindow,
                                                         self.cfgmanager.lang_get_string('filedialog_pulse_import_title'),
                                                         self.cfgmanager._config['PULSE'].get('import_file_dir'),
                                                         f"{self.cfgmanager.lang_get_string('filedialog_pulse_import_ext_title')} ({self.cfgmanager._config['PULSE'].get('import_file_ext')})",
                                                         options=options)
        if fileName:
            logger.info(f"Pulse selected: {fileName}")
            if self.mainwindow.data_container.import_pulse(fileName):
                logger.info('Pulse imported: ' + str(self.mainwindow.data_container.pulse_data))
                self.mainwindow.set_current_pulseinfo(self.mainwindow.data_container.pulse_data.get_name(),
                                                      self.mainwindow.data_container.pulse_data.get_max(),
                                                      self.mainwindow.data_container.pulse_data.get_min(),
                                                      self.mainwindow.data_container.pulse_data.get_durationms())
            else:
                logger.error('Importing Pulse failed.')
        else:
            logger.info('Import pulse canceled by user.')


class OSGMainWindow(QMainWindow, Ui_OSGMainWindow):
    def __init__(self, app, *args, **kwargs):
        super(OSGMainWindow, self).__init__(*args, **kwargs)
        self.application = app
        self.setupUi(self)
        self.setupWindow()
        self.tool_tab_pulse = OSGMWPulseToolTab(self)
        self.data_container = OSGDataContainer()

        self.plc = OSGPLC(self)
        self.setupPlcEvents()

        self.converter = OSGConverter(self)
        self.show()

    def setupWindow(self):
        self.setWindowMonitor()
        self.setWindowIcon(QIcon(self.application.configmanager._config['APP'].get('window_icon')))
        self.logo.setPixmap(QPixmap(self.application.configmanager._config['APP'].get('logo')))
        if self.application.configmanager._config['APP'].getboolean('always_top'): self.setWindowFlag(
            Qt.WindowStaysOnTopHint)
        if self.application.configmanager._config['APP'].getboolean('maximized'): self.showMaximized()
        if self.application.configmanager._config['APP'].getboolean('fullscreen'): self.showFullScreen()
        self.setupStrings()

        self.connectComponents()

    def setupPlcEvents(self):
        self.plc.events.language_changed.connect(self.setupStrings)

    def showMessage(self, message, duration=0):
        self.statusbar.showMessage(message, duration)

    def setWindowMonitor(self):
        display_id = self.application.configmanager._config['APP'].getint('monitor_nr')
        monitor = QDesktopWidget().screenGeometry(display_id)
        self.move(monitor.left(), monitor.top())

    def setupStrings(self):
        # Main Window Title
        self.setWindowTitle(self.application.configmanager.lang_get_string('title'))
        # Main Window Menu bar

    def set_current_pulseinfo(self,name, max, min,durationms):
        self.labelCurrentPulseNameValue.setText(name)
        self.labelCurrentPulseMaxValue.setText(str(max)+' G')
        self.labelCurrentPulseMinValue.setText(str(min)+' G')
        self.labelCurrentPulseDurationValue.setText(str(round(durationms,2)) + ' ms')

    def connectComponents(self):
        pass

    def setPlcConnectionStatus(self, state):
        if state:
            self.labelPlcStatusValue.setText('connected')
            self.labelPlcStatusValue.setStyleSheet(
                f"color: #{self.application.configmanager._config['PLC'].get('color_connected')}")
        else:
            self.labelPlcStatusValue.setText('disconnected')
            self.labelPlcStatusValue.setStyleSheet(
                f"color: #{self.application.configmanager._config['PLC'].get('color_disconnected')}")

    def setConverterConnectionStatus(self, state):
        if state:
            self.labelConverterStatusValue.setText('connected')
            self.labelConverterStatusValue.setStyleSheet(
                f"color: #{self.application.configmanager._config['CONVERTER'].get('color_connected')}")
        else:
            self.labelConverterStatusValue.setText('disconnected')
            self.labelConverterStatusValue.setStyleSheet(
                f"color: #{self.application.configmanager._config['CONVERTER'].get('color_disconnected')}")

