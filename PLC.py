from PyQt5 import QtCore
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from SinamicsExport import get_last_trace
from PyLcSnap7.PLC import S7Conn
from PyLcSnap7 import Smarttags
from TraceHelper import Trace, offset_x_soll


class UDT_Trigger:
    def __init__(self, plc, db, start):
        self._plc = plc
        self._db = db
        self._start = start
        self.enabled = Smarttags.Bool(self._plc, self._db, self._start, 0)
        self.name = Smarttags.String(self._plc, self._db, self._start + 2, 16)
        self.time = Smarttags.Int(self._plc, self._db, self._start + 20)


class GDB_Versuchsdaten:
    def __init__(self, plc, cfg):
        self.plc = plc
        self.cfg = cfg
        self.versuchsnummer = Smarttags.String(self.plc, 894, 0, 64)
        self.versuchstyp = Smarttags.String(self.plc, 894, 66, 64)
        self.bediener = Smarttags.String(self.plc, 894, 132, 64)
        self.kommentar = Smarttags.String(self.plc, 894, 198, 64)
        self.trigger01 = UDT_Trigger(self.plc, 894, 264)


class PLC(QtCore.QThread):
    def __init__(self, parent):
        super(PLC, self).__init__()
        self.parent = parent
        self.cfg = parent.cfg
        self.plc = S7Conn(self.cfg['PLC']['ip'])
        x = self.plc.readLTime(894,284)
        self.plc.writeLTime(894,284,x.microseconds)
        self.gdb_versuchsdaten = GDB_Versuchsdaten(self.plc, self.cfg)
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
        self.dpi = 100

    def submit_data(self, datay):
        done = False
        while not done:
            try:
                self.array_soll.write([i * 9.81 for i in datay])
                self.soll_len.write(len(datay))
                done = True
            except Exception as e:
                print(e)

    def read_soll_ist_data(self):
        done = False
        while not done:
            try:
                soll = self.array_soll.read()
                ist = self.array_ist.read()
                done = True
            except Exception as e:
                print(e)
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
        ax = fig.add_subplot()
        ax.set_facecolor('#' + self.bg_color.read())
        ax.set_ylabel(self.bez_y.read())
        ax.set_xlabel(self.bez_x.read())
        done = False
        while not done:
            try:
                ax.plot(
                    [(i + 1) / (self.cfg['GRAPH'].getint('resolution_khz')) for i in range(len(soll))],
                    soll,
                    linewidth=self.soll_linewidth.read(),
                    color='#' + self.soll_color.read())
                done = True
            except Exception as e:
                print(e)
        fig.savefig(self.var_url_02.read(), dpi=self.dpi)
        fig.savefig(self.var_url_03.read(), dpi=self.dpi)
        del (fig)

    def plot_kompl(self):
        filename = get_last_trace(self.cfg['PLC']['ip_cu320'], './export/trace.csv')
        trace = Trace()
        trace.load_trace_csv(filename)
        khz = self.cfg['GRAPH'].getint('resolution_khz')

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
                                    print(e)
                        else:
                            self.parent.statusbar.showMessage(self.cfg['STRINGS']['status_plc_data_submit_error'])

                    elif self.anf_kompl.read():
                        self.plot_kompl()
                        self.anf_kompl.write(False)
                        self.plot_done_kompl.write(True)


            except Exception as e:
                print(e)
            self.msleep(self.cfg['PLC'].getint('refresh_delay_ms'))
