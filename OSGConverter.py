from PyQt5.QtCore import QThread


class OSGConverter(QThread):
    def __init__(self, parent=None):
        super(OSGConverter, self).__init__()
        self.parent = parent
        self.delay = self.parent.application.configmanager._config['CONVERTER'].getint('refresh_delay_ms')
        self.running = True
        self.setConnectionStatus(False)
        self.start()

    def setConnectionStatus(self, state):
        self.parent.setConverterConnectionStatus(state)

    def connected(self):
        return False

    def run(self):

        while self.connected():
            print(self.delay)
            self.msleep(self.delay)
