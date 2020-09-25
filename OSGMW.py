from PyQt5.QtWidgets import QMainWindow, QDesktopWidget
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from MainWindow import Ui_MainWindow


class OSGMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, app, *args, **kwargs):
        super(OSGMainWindow, self).__init__(*args, **kwargs)
        self.application = app
        self.setupUi(self)
        self.setupWindow()
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
        self.menuFile.setTitle(self.application.configmanager.lang_get_string('gui_menubar_file'))
        self.actionExit.setText(self.application.configmanager.lang_get_string('gui_menubar_file_exit'))
        self.menuInfo.setTitle(self.application.configmanager.lang_get_string('gui_menubar_info'))
        self.actionInfo.setText(self.application.configmanager.lang_get_string('gui_menubar_info_info'))
        self.actionAbout_Qt.setText(self.application.configmanager.lang_get_string('gui_menubar_info_aboutqt'))

    def connectComponents(self):
        self.btn_load.clicked.connect(lambda: print(1))


        self.setPlcConnectionStatus(False)

    def setPlcConnectionStatus(self, state):
        if state:
            self.label_plc_status_value.setText('connected')
            self.label_plc_status_value.setStyleSheet('color: #00FF00')
        else:
            self.label_plc_status_value.setText('disconnected')
            self.label_plc_status_value.setStyleSheet('color: #FF0000')
