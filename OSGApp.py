from PyQt5.QtWidgets import QApplication
from OSGMW import OSGMainWindow
from OSGConfig import OSGConfigManager

import ctypes
myappid = u'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class OSledgeGraphApplication(QApplication):
    def __init__(self, *args, **kwargs):
        super(OSledgeGraphApplication, self).__init__(*args, **kwargs)
        self.configmanager = OSGConfigManager('new_config.ini')
        self.ui = OSGMainWindow(self)


    def set_app_id(self):
        id_company = self.configmanager._config.get('id_company')
        id_product = self.configmanager._config.get('id_product')
        id_subproduct = self.configmanager._config.get('id_subproduct')
        id_version = self.configmanager._config.get('id_version')
        app_id = f"{id_company}.{id_product}.{id_subproduct}.{id_version}"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)