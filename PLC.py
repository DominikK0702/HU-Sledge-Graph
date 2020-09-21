from PyQt5 import QtCore
import matplotlib.pyplot as plt
from SinamicsExport import get_last_trace
from PyLcSnap7.PLC import S7Conn
from PyLcSnap7 import Smarttags
from TraceHelper import Trace, offset_x_soll
from Protocol.ProtocolGen import ProtocolJson, ProtocolData
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
    def __init__(self, plc, cfg, db):
        self.plc = plc
        self.cfg = cfg
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


class PLC(QtCore.QThread):
    def __init__(self, parent):
        super(PLC, self).__init__()
        self.parent = parent
        self.cfg = parent.cfg
        self.plc = S7Conn(self.cfg['PLC']['ip'])
        self.gdb_versuchsdaten = GDB_Versuchsdaten(self.plc, self.cfg, 894)
        self.keep_alive = Smarttags.Bool(self.plc, self.cfg['PLC'].getint('db_in'), 0, 0)
        self.regler_date_ready = Smarttags.Bool(self.plc, self.cfg['PLC'].getint('db_out'), 0, 0)
        self.array_ist = Smarttags.RealArray(self.plc, self.cfg['PLC'].getint('db_ist'), 0, 3000)
        self.array_soll = Smarttags.RealArray(self.plc, self.cfg['PLC'].getint('db_soll'), 0, 3000)
        self.var_url_01 = Smarttags.String(self.plc, self.cfg['PLC'].getint('db_out'), 0, 64)
        self.var_url_02 = Smarttags.String(self.plc, self.cfg['PLC'].getint('db_out'), 66, 64)
        self.var_url_03 = Smarttags.String(self.plc, self.cfg['PLC'].getint('db_out'), 132, 64)
        self.anf_soll = Smarttags.Bool(self.plc, self.cfg['PLC'].getint('db_out'), 198, 0)
        self.anf_kompl = Smarttags.Bool(self.plc, self.cfg['PLC'].getint('db_out'), 198, 1)
        self.bg_color = Smarttags.String(self.plc, self.cfg['PLC'].getint('db_out'), 200, 8)
        self.soll_color = Smarttags.String(self.plc, self.cfg['PLC'].getint('db_out'), 208, 8)
        self.ist_color = Smarttags.String(self.plc, self.cfg['PLC'].getint('db_out'), 216, 8)
        self.soll_linewidth = Smarttags.Int(self.plc, self.cfg['PLC'].getint('db_out'), 224)
        self.ist_linewidth = Smarttags.Int(self.plc, self.cfg['PLC'].getint('db_out'), 226)
        self.bez_x = Smarttags.String(self.plc, self.cfg['PLC'].getint('db_out'), 228, 16)
        self.bez_y = Smarttags.String(self.plc, self.cfg['PLC'].getint('db_out'), 246, 16)
        self.size_x = Smarttags.Int(self.plc, self.cfg['PLC'].getint('db_out'), 264)
        self.size_y = Smarttags.Int(self.plc, self.cfg['PLC'].getint('db_out'), 266)
        self.plot_done_soll = Smarttags.Bool(self.plc, self.cfg['PLC'].getint('db_in'), 0, 1)
        self.plot_done_kompl = Smarttags.Bool(self.plc, self.cfg['PLC'].getint('db_in'), 0, 2)
        self.soll_len = Smarttags.Int(self.plc, self.cfg['PLC'].getint('db_soll'), 12004)
        self.anf_submit_data = Smarttags.Bool(self.plc, self.cfg['PLC'].getint('db_in'), 0, 4)
        self.path_json_export = Smarttags.String(self.plc, self.cfg['PLC'].getint('db_out'), 334, 255)
        self.language = Smarttags.Bool(self.plc, self.cfg['PLC'].getint('db_out'), 590, 0)
        self.dpi = 100

    def submit_data(self, datay):
        done = False
        logger.debug('Submitting data to plc')
        while not done:
            try:
                self.array_soll.write([i * 9.81 for i in datay])
                self.soll_len.write(len(datay))
                done = True
                logger.debug('Data submitted to plc')
            except Exception as e:
                logger.error(f'Submitting data to plc canceled: {str(e)}')

    def read_soll_ist_data(self):
        done = False
        logger.debug('Reading compare data from plc')
        while not done:
            try:
                soll = self.array_soll.read()
                ist = self.array_ist.read()
                done = True
                logger.debug('Done reading compare data from plc')
            except Exception as e:
                logger.error(f'Reading data from plc canceled: {str(e)}')
        return soll, ist

    def plot_soll(self):
        soll = [i * 9.81 for i in self.parent.current_data_y]
        fig = plt.figure(dpi=self.dpi, figsize=(self.size_x.read() / self.dpi, self.size_y.read() / self.dpi))
        fig.subplots_adjust(top=self.cfg['PLCGRAPH'].getfloat('adjust_top'),
                            bottom=self.cfg['PLCGRAPH'].getfloat('adjust_bottom'),
                            left=self.cfg['PLCGRAPH'].getfloat('ajdust_left'),
                            right=self.cfg['PLCGRAPH'].getfloat('adjust_right'),
                            hspace=self.cfg['PLCGRAPH'].getfloat('adjust_hspace'),
                            wspace=self.cfg['PLCGRAPH'].getfloat('adjust_wspace'))
        plt.grid(color=(0, 0, 0), alpha=0.2, linestyle='-', linewidth=0.2)
        ax = fig.add_subplot()
        ax.set_facecolor('#' + self.bg_color.read())
        ax.set_ylabel(self.bez_y.read())
        ax.set_xlabel(self.bez_x.read())
        done = False
        while not done:
            try:
                ax.plot(
                    [i * 1000 for i in offset_x_soll(soll, 0)],
                    soll,
                    linewidth=self.soll_linewidth.read(),
                    color='#' + self.soll_color.read())
                done = True
            except Exception as e:
                logger.error(str(e))
        fig.savefig(self.var_url_02.read(), dpi=self.dpi)
        fig.savefig(self.var_url_03.read(), dpi=self.dpi)
        logger.debug('Target plot for plc generated.')
        del (fig)

    def store_json(self, trace, soll_x, soll_data):
        store = ProtocolData()
        # Info
        store.data['versuchsnummer'] = self.gdb_versuchsdaten.versuchsnummer.read()
        store.data['versuchstyp'] = self.gdb_versuchsdaten.versuchstyp.read()
        store.data['bediener'] = self.gdb_versuchsdaten.bediener.read()
        store.data['kommentar'] = self.gdb_versuchsdaten.kommentar.read()
        store.data['startpos'] = self.gdb_versuchsdaten.startpos.read()
        store.data['endpos'] = self.gdb_versuchsdaten.endpos.read()
        store.data['zuladung'] = self.gdb_versuchsdaten.zuladung.read()
        # Trigger
        store.data['trigger']['01']['enabled'] = self.gdb_versuchsdaten.trigger01.enabled.read()
        store.data['trigger']['01']['name'] = self.gdb_versuchsdaten.trigger01.name.read()
        store.data['trigger']['01']['zeit'] = self.gdb_versuchsdaten.trigger01.time.read()
        store.data['trigger']['02']['enabled'] = self.gdb_versuchsdaten.trigger02.enabled.read()
        store.data['trigger']['02']['name'] = self.gdb_versuchsdaten.trigger02.name.read()
        store.data['trigger']['02']['zeit'] = self.gdb_versuchsdaten.trigger02.time.read()
        store.data['trigger']['03']['enabled'] = self.gdb_versuchsdaten.trigger03.enabled.read()
        store.data['trigger']['03']['name'] = self.gdb_versuchsdaten.trigger03.name.read()
        store.data['trigger']['03']['zeit'] = self.gdb_versuchsdaten.trigger03.time.read()
        store.data['trigger']['04']['enabled'] = self.gdb_versuchsdaten.trigger04.enabled.read()
        store.data['trigger']['04']['name'] = self.gdb_versuchsdaten.trigger04.name.read()
        store.data['trigger']['04']['zeit'] = self.gdb_versuchsdaten.trigger04.time.read()
        store.data['trigger']['05']['enabled'] = self.gdb_versuchsdaten.trigger05.enabled.read()
        store.data['trigger']['05']['name'] = self.gdb_versuchsdaten.trigger05.name.read()
        store.data['trigger']['05']['zeit'] = self.gdb_versuchsdaten.trigger05.time.read()
        store.data['trigger']['06']['enabled'] = self.gdb_versuchsdaten.trigger06.enabled.read()
        store.data['trigger']['06']['name'] = self.gdb_versuchsdaten.trigger06.name.read()
        store.data['trigger']['06']['zeit'] = self.gdb_versuchsdaten.trigger06.time.read()
        store.data['trigger']['07']['enabled'] = self.gdb_versuchsdaten.trigger07.enabled.read()
        store.data['trigger']['07']['name'] = self.gdb_versuchsdaten.trigger07.name.read()
        store.data['trigger']['07']['zeit'] = self.gdb_versuchsdaten.trigger07.time.read()
        store.data['trigger']['08']['enabled'] = self.gdb_versuchsdaten.trigger08.enabled.read()
        store.data['trigger']['08']['name'] = self.gdb_versuchsdaten.trigger08.name.read()
        store.data['trigger']['08']['zeit'] = self.gdb_versuchsdaten.trigger08.time.read()
        store.data['trigger']['09']['enabled'] = self.gdb_versuchsdaten.trigger09.enabled.read()
        store.data['trigger']['09']['name'] = self.gdb_versuchsdaten.trigger09.name.read()
        store.data['trigger']['09']['zeit'] = self.gdb_versuchsdaten.trigger09.time.read()
        store.data['trigger']['10']['enabled'] = self.gdb_versuchsdaten.trigger10.enabled.read()
        store.data['trigger']['10']['name'] = self.gdb_versuchsdaten.trigger10.name.read()
        store.data['trigger']['10']['zeit'] = self.gdb_versuchsdaten.trigger10.time.read()
        store.data['trigger']['11']['enabled'] = self.gdb_versuchsdaten.trigger11.enabled.read()
        store.data['trigger']['11']['name'] = self.gdb_versuchsdaten.trigger11.name.read()
        store.data['trigger']['11']['zeit'] = self.gdb_versuchsdaten.trigger11.time.read()
        store.data['trigger']['12']['enabled'] = self.gdb_versuchsdaten.trigger12.enabled.read()
        store.data['trigger']['12']['name'] = self.gdb_versuchsdaten.trigger12.name.read()
        store.data['trigger']['12']['zeit'] = self.gdb_versuchsdaten.trigger12.time.read()
        store.data['trigger']['13']['enabled'] = self.gdb_versuchsdaten.trigger13.enabled.read()
        store.data['trigger']['13']['name'] = self.gdb_versuchsdaten.trigger13.name.read()
        store.data['trigger']['13']['zeit'] = self.gdb_versuchsdaten.trigger13.time.read()
        store.data['trigger']['14']['enabled'] = self.gdb_versuchsdaten.trigger14.enabled.read()
        store.data['trigger']['14']['name'] = self.gdb_versuchsdaten.trigger14.name.read()
        store.data['trigger']['14']['zeit'] = self.gdb_versuchsdaten.trigger14.time.read()
        store.data['trigger']['15']['enabled'] = self.gdb_versuchsdaten.trigger15.enabled.read()
        store.data['trigger']['15']['name'] = self.gdb_versuchsdaten.trigger15.name.read()
        store.data['trigger']['15']['zeit'] = self.gdb_versuchsdaten.trigger15.time.read()
        # Puls
        store.data['puls_x'] = soll_x
        store.data['puls_y'] = soll_data
        # Trace
        store.data['trace_vel'] = trace.get_axis_velocity()
        store.data['trace_x'] = trace.get_axis_time()
        store.data['trace_way'] = trace.get_axis_way()
        store.data['trace_acc_way'] = trace.get_axis_acceleration()
        store.data['trace_acc_vel'] = trace.get_axis_acc_from_speed(filtered=False)
        store.data['trace_acc_vel_filt'] = trace.get_axis_acc_from_speed(filtered=True)
        store.data['trace_voltage'] = trace.get_axis_voltage()
        jsonObj = ProtocolJson()
        jsonObj.json.data = store.data
        jsonObj.save(self.path_json_export.read())
        logger.debug('Protocol saved.')

    def plot_kompl(self):
        filename = get_last_trace(self.cfg['PLC']['ip_cu320'], './export/trace.csv')
        trace = Trace()
        trace.load_trace_csv(filename)

        # soll_data = [i * 60 * 0.981 for i in self.array_soll.read()]
        # todo test calc to m/s²
        soll_data = [i * 0.981 for i in self.array_soll.read()]

        offset = 35
        soll_x = [i * 1000 for i in offset_x_soll(soll_data, offset)]
        pulsdauer = soll_x[-1] + 50

        ist_x = [i * 1000 for i in trace.get_axis_time() if i * 1000 <= pulsdauer]
        ist_data = trace.get_axis_acc_from_speed(filtered=True)[:len(ist_x)]
        # todo test calc to m/s²
        ist_data = [i / 60 for i in ist_data]

        fig = plt.figure(dpi=self.dpi, figsize=(self.size_x.read() / self.dpi, self.size_y.read() / self.dpi))
        fig.subplots_adjust(top=self.cfg['PLCGRAPH'].getfloat('adjust_top'),
                            bottom=self.cfg['PLCGRAPH'].getfloat('adjust_bottom'),
                            left=self.cfg['PLCGRAPH'].getfloat('ajdust_left'),
                            right=self.cfg['PLCGRAPH'].getfloat('adjust_right'),
                            hspace=self.cfg['PLCGRAPH'].getfloat('adjust_hspace'),
                            wspace=self.cfg['PLCGRAPH'].getfloat('adjust_wspace'))
        plt.grid(color=(0, 0, 0), alpha=0.2, linestyle='-', linewidth=0.2)
        ax = fig.add_subplot()
        ax.set_facecolor('#' + self.bg_color.read())
        ax.set_ylabel(self.bez_y.read())
        ax.set_xlabel(self.bez_x.read())
        ax.plot(soll_x, soll_data, linewidth=self.soll_linewidth.read(),
                color='#' + self.soll_color.read())

        ax.plot(ist_x, ist_data, linewidth=self.ist_linewidth.read(),
                color='#' + self.ist_color.read())
        fig.savefig(self.var_url_02.read(), dpi=self.dpi)
        fig.savefig(self.var_url_03.read(), dpi=self.dpi)
        logger.debug('Compare plot for plc generated')
        self.store_json(trace, soll_x, soll_data)
        del (ax)
        del (fig)

    def run(self):
        self.parent.statusbar.showMessage(self.cfg['STRINGS']['status_plc_connecting'])
        self.sleep(1)
        if self.plc.connect():
            self.parent.statusbar.showMessage(self.cfg['STRINGS']['status_plc_connected'])
        else:
            self.parent.statusbar.showMessage(self.cfg['STRINGS']['status_plc_disconnected'])

        while True:
            try:
                if not self.plc.connect():
                    self.parent.statusbar.showMessage(self.cfg['STRINGS']['status_plc_disconnected'])
                else:
                    # todo check language string from plc and set langcfg
                    self.keep_alive.write(not self.keep_alive.read())
                    if self.anf_soll.read():
                        if self.parent.current_data_y:
                            done = False
                            while not done:
                                try:
                                    self.submit_data(self.parent.current_data_y)
                                    self.plot_soll()
                                    self.plot_done_soll.write(True)
                                    self.parent.statusbar.showMessage(self.cfg['STRINGS']['status_plc_data_submit'])
                                    self.anf_soll.write(False)
                                    self.plot_done_soll.write(True)
                                    done = True
                                except Exception as e:
                                    logger.error(str(e))
                        else:
                            self.parent.statusbar.showMessage(self.cfg['STRINGS']['status_plc_data_submit_error'])
                            logger.info("Target pulse request active. No pulse data to submit to plc")

                    elif self.anf_kompl.read():
                        self.plot_kompl()
                        self.anf_kompl.write(False)
                        self.plot_done_kompl.write(True)


            except Exception as e:
                print(e)
            self.msleep(self.cfg['PLC'].getint('refresh_delay_ms'))
