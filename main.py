import sys
from configparser import ConfigParser
from PyQt5 import QtCore
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout


class GraphMainWindow(QMainWindow):
    def __init__(self,cfg):
        self.cfg = cfg
        super(GraphMainWindow, self).__init__()
        self.initUI()

    def configUI(self):
        self.setWindowTitle(self.cfg['GUI']['title'])
        self.resize(self.cfg['GUI'].getint('width'),self.cfg['GUI'].getint('heigth'))

    def initUI(self):
        self.configUI()
        layout = QGridLayout()
        layout
        self.btn_save = QPushButton(self.cfg['STRINGS']['btn_save'], self)
        self.btn_save.show()
        self.btn_load = QPushButton(self.cfg['STRINGS']['btn_load'], self)
        self.btn_load.show()
        self.btn_submit = QPushButton(self.cfg['STRINGS']['btn_submit'], self)
        self.btn_submit.show()
        self.btn_compare = QPushButton(self.cfg['STRINGS']['btn_compare'], self)
        self.btn_compare.show()

        self.show()




if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')
    app = QApplication(sys.argv)
    gui = GraphMainWindow(config)
    sys.exit(app.exec_())
