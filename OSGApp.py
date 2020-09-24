from PyQt5.QtWidgets import QApplication
from OSGMW import OSGMainWindow
from OSGConfig import OSGConfigManager

class OSledgeGraphApplication(QApplication):
    def __init__(self, *args, **kwargs):
        super(OSledgeGraphApplication, self).__init__(*args, **kwargs)
        self.configmanager = OSGConfigManager('new_config.ini')
        self.ui = OSGMainWindow(self)
        print(1)