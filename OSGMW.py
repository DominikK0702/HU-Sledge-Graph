from PyQt5.QtWidgets import QMainWindow, QDesktopWidget
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from ui.OSGMainWindow import Ui_OSGMainWindow
from OSGConverter import OSGConverter
from OSGPLC import OSGPLC
from OSGDataContainer import OSGDataContainer


class OSGMainWindow(QMainWindow, Ui_OSGMainWindow):
    def __init__(self, app, *args, **kwargs):
        super(OSGMainWindow, self).__init__(*args, **kwargs)
        self.application = app
        self.setupUi(self)
        self.setupWindow()
        self.plc = OSGPLC(self)
        self.converter = OSGConverter(self)
        self.data_container = OSGDataContainer()
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
