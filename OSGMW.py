from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QPixmap, QIcon
from MainWindow import Ui_MainWindow

class OSGMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, app, *args, **kwargs):
        super(OSGMainWindow, self).__init__(*args, **kwargs)
        self.application = app
        self.setupUi(self)
        self.setupStrings()
        self.setupWindow()
        self.show()

    def setupWindow(self):
        self.setWindowIcon(QIcon(self.application.configmanager._config['APP'].get('window_icon')))
        self.showMaximized()

    def setupStrings(self):
        self.setWindowTitle(self.application.configmanager.lang_get_string('title'))