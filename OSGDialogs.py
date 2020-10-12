from ui.QtInfo import Ui_QtInfo
from ui.InfoDialog import Ui_InfoDialog
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow


def show_qtinfo(parent):
    qtinfo = QMainWindow(parent)
    qtinfo_ui = Ui_QtInfo()
    qtinfo_ui.setupUi(qtinfo)
    qtinfo_ui.label.setPixmap(QtGui.QPixmap('./assets/qt.png'))
    qtinfo.show()

def show_info(parent):
    info = QMainWindow(parent)
    info_ui = Ui_InfoDialog()
    info_ui.setupUi(info)
    info.show()