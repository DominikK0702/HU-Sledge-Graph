from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyLcSnap7.PLC import S7Conn
from PyLcSnap7 import Smarttags
from loguru import logger


class UDT_Trigger:
    def __init__(self, plc, db, start):
        self._plc = plc
        self._db = db
        self._start = start
        self.enabled = Smarttags.Bool(self._plc, self._db, self._start, 0)
        self.name = Smarttags.String(self._plc, self._db, self._start + 2, 16)
        self.time = Smarttags.LTime(self._plc, self._db, self._start + 20)


class GDB_Versuchsdaten:
    def __init__(self, plc, db):
        self.plc = plc.plc
        self.cfg = plc.configmanager
        self.db = db
        self.versuchsnummer = Smarttags.String(self.plc, self.db, 0, 64)
        self.versuchstyp = Smarttags.String(self.plc, self.db, 66, 64)
        self.bediener = Smarttags.String(self.plc, self.db, 132, 64)
        self.kommentar = Smarttags.String(self.plc, self.db, 198, 64)
        self.trigger01 = UDT_Trigger(self.plc, self.db, 264)
        self.trigger02 = UDT_Trigger(self.plc, self.db, 292)
        self.trigger03 = UDT_Trigger(self.plc, self.db, 320)
        self.trigger04 = UDT_Trigger(self.plc, self.db, 348)
        self.trigger05 = UDT_Trigger(self.plc, self.db, 376)
        self.trigger06 = UDT_Trigger(self.plc, self.db, 404)
        self.trigger07 = UDT_Trigger(self.plc, self.db, 432)
        self.trigger08 = UDT_Trigger(self.plc, self.db, 460)
        self.trigger09 = UDT_Trigger(self.plc, self.db, 488)
        self.trigger10 = UDT_Trigger(self.plc, self.db, 516)
        self.trigger11 = UDT_Trigger(self.plc, self.db, 544)
        self.trigger12 = UDT_Trigger(self.plc, self.db, 572)
        self.trigger13 = UDT_Trigger(self.plc, self.db, 600)
        self.trigger14 = UDT_Trigger(self.plc, self.db, 628)
        self.trigger15 = UDT_Trigger(self.plc, self.db, 656)
        self.startpos = Smarttags.Real(self.plc, self.db, 684)
        self.endpos = Smarttags.Real(self.plc, self.db, 688)
        self.zuladung = Smarttags.Real(self.plc, self.db, 692)


class GDB_Graph_In:
    def __init__(self, plc, db):
        self._plc = plc.plc
        self._cfg = plc.configmanager
        self._db = db
        self.keep_alive = Smarttags.Bool(self._plc, self._db, 0, 0)
        self.kurve_soll_geschrieben = Smarttags.Bool(self._plc, self._db, 0, 1)
        self.kurve_kmplt_geschrieben = Smarttags.Bool(self._plc, self._db, 0, 2)
        self.puls_geladen = Smarttags.Bool(self._plc, self._db, 0, 3)
        self.anf_puls_laden = Smarttags.Bool(self._plc, self._db, 0, 4)


class GDB_Graph_Out:
    def __init__(self, plc, db):
        self._plc = plc.plc
        self._cfg = plc.configmanager
        self._db = db
        self.file_plot_01 = Smarttags.String(self._plc, self._db, 0, 64)
        self.file_plot_02 = Smarttags.String(self._plc, self._db, 66, 64)
        self.file_plot_03 = Smarttags.String(self._plc, self._db, 132, 64)
        self.anf_sollkurve = Smarttags.Bool(self._plc, self._db, 198, 0)
        self.anf_kurven_komplett = Smarttags.Bool(self._plc, self._db, 198, 0)
        self.background_color = Smarttags.String(self._plc, self._db, 200)
        self.line_color_soll = Smarttags.String(self._plc, self._db, 208)
        self.line_color_ist = Smarttags.String(self._plc, self._db, 216)
        self.lingwidth_soll = Smarttags.Int(self._plc, self._db, 224)
        self.lingwidth_ist = Smarttags.Int(self._plc, self._db, 226)
        self.label_x_axis = Smarttags.String(self._plc, self._db, 228, 16)
        self.label_y_axis = Smarttags.String(self._plc, self._db, 246, 16)
        self.size_x = Smarttags.Int(self._plc, self._db, 264)
        self.size_y = Smarttags.Int(self._plc, self._db, 266)
        self.file_plot_empty = Smarttags.String(self._plc, self._db, 268, 64)
        self.path_export_csv = Smarttags.String(self._plc, self._db, 334)
        self.language_german = Smarttags.Bool(self._plc, self._db, 590, 0)


class GDB_Daten_soll:
    def __init__(self, plc, db):
        self._plc = plc.plc
        self._cfg = plc.configmanager
        self._db = db
        self.daten = Smarttags.RealArray(self._plc, self._db, 0, 3000)
        self.datenpunkte = Smarttags.Int(self._plc, self._db, 12004)


class PlcEvents(QObject):
    language_changed = pyqtSignal()
    req_pulse_request = pyqtSignal()


class OSGPLC(QThread):
    def __init__(self, parent):
        super(OSGPLC, self).__init__()
        self.parent = parent
        self.configmanager = parent.application.configmanager
        self.delay = self.configmanager._config['PLC'].getint('refresh_delay_ms')
        self.running = True
        self.setConnectionStatus(False)
        self.plc = S7Conn(self.configmanager._config['PLC'].get('ip'))
        self.plc_info = None
        self.gdb_graph_in = GDB_Graph_In(self, 892)
        self.gdb_graph_out = GDB_Graph_Out(self, 893)
        self.gdb_versuchsdaten = GDB_Versuchsdaten(self, 894)
        self.gdb_daten_soll = GDB_Daten_soll(self, 891)
        self.current_language_german = None
        self.events = PlcEvents()
        self.start()

    def setConnectionStatus(self, state):
        self.parent.setPlcConnectionStatus(state)

    def connected(self):
        state = self.plc.connect()
        if state:
            try:
                self.plc_info = self.plc.client.get_cpu_info()
            except Exception as e:
                state = False
        self.setConnectionStatus(state)
        return state

    def keep_alive(self):
        self.gdb_graph_in.keep_alive.write(not self.gdb_graph_in.keep_alive.read())

    def set_language(self):
        if self.current_language_german != self.gdb_graph_out.language_german.read():
            self.current_language_german = self.gdb_graph_out.language_german.read()
            if self.current_language_german:
                self.configmanager._lang_cfg.set_language('DE')
                logger.debug('switched language to german')
            else:
                self.configmanager._lang_cfg.set_language('EN')
                logger.debug('switched language to english')

            self.events.language_changed.emit()

    def get_target_pulse(self):

        return []

    def submit_target_pulse(self):
        logger.warning('Anforderung Soll Kurve laden')

        # get pulse
        pulse_16khz = self.get_target_pulse()

        # Submit Pulse and length to plc
        self.gdb_daten_soll.daten.write(pulse_16khz)
        self.gdb_daten_soll.datenpunkte.write(len(pulse_16khz))

        # Tell plc submit complete
        self.gdb_graph_in.puls_geladen.write(True)

        # Reset Toggle Bit
        self.gdb_graph_out.anf_sollkurve.write(False)
        logger.warning('Anforderung Soll Kurve laden fertig')

    def loop(self):
        self.keep_alive()
        self.set_language()
        if self.gdb_graph_out.anf_sollkurve.read():
            self.submit_target_pulse()

    def run(self):
        logger.info('PLC QThread started')
        while self.running:

            if not self.connected():
                continue

            try:
                self.loop()
            except Exception as e:
                pass
            self.msleep(self.delay)
