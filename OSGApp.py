from PyQt5.QtWidgets import QApplication
from OSGMW import OSGMainWindow
from OSGConfig import OSGConfigManager
import ctypes


class OSledgeGraphApplication(QApplication):
    def __init__(self, *args, **kwargs):
        super(OSledgeGraphApplication, self).__init__(*args, **kwargs)
        self.configmanager = OSGConfigManager('config.ini')
        self.set_app_id()
        self.ui = OSGMainWindow(self)
        self.set_stylesheet()

    def set_stylesheet(self):
        stylesheet = open(self.configmanager._config['APP'].get('stylesheet')).read()
        self.setStyleSheet(stylesheet)

    def set_app_id(self):
        id_company = self.configmanager._config.get('APP', 'id_company')
        id_product = self.configmanager._config.get('APP', 'id_product')
        id_subproduct = self.configmanager._config.get('APP', 'id_subproduct')
        id_version = self.configmanager._config.get('APP', 'id_version')
        app_id = f"{id_company}.{id_product}.{id_subproduct}.{id_version}"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
