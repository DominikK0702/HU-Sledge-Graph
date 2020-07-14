import json

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Image, Table, TableStyle, Paragraph, Frame, Spacer
from reportlab.lib import colors, styles

import datetime
import io
import matplotlib.pyplot as plt


class ProtocolData:
    def __init__(self):
        self.data = {
            'versuchsnummer'    : '',
            'versuchstyp'       : '',
            'bediener'          : '',
            'kommentar'         : '',
            'startpos'          : '',
            'endpos'            : '',
            'zuladung'          : '',
            'timestamp'         : datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            'trigger'           : {
                '01': {'enabled': False, 'name': '', 'zeit': 0},
                '02': {'enabled': False, 'name': '', 'zeit': 0},
                '03': {'enabled': False, 'name': '', 'zeit': 0},
                '04': {'enabled': False, 'name': '', 'zeit': 0},
                '05': {'enabled': False, 'name': '', 'zeit': 0},
                '06': {'enabled': False, 'name': '', 'zeit': 0},
                '07': {'enabled': False, 'name': '', 'zeit': 0},
                '08': {'enabled': False, 'name': '', 'zeit': 0},
                '09': {'enabled': False, 'name': '', 'zeit': 0},
                '10': {'enabled': False, 'name': '', 'zeit': 0},
                '11': {'enabled': False, 'name': '', 'zeit': 0},
                '12': {'enabled': False, 'name': '', 'zeit': 0},
                '13': {'enabled': False, 'name': '', 'zeit': 0},
                '14': {'enabled': False, 'name': '', 'zeit': 0},
                '15': {'enabled': False, 'name': '', 'zeit': 0}
            },
            'puls_x'            : [],
            'puls_y'            : [],
            'trace_vel'         : [],
            'trace_x'           : [],
            'trace_way'         : [],
            'trace_acc_way'     : [],
            'trace_acc_vel'     : [],
            'trace_acc_vel_filt': [],
            'trace_voltage'     : []
        }


class ProtocolJson:
    def __init__(self):
        self.json = ProtocolData()

    def load(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            self.json.data = json.loads(f.read())

    def gen_filename(self, path):
        extension = '.pjson'
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        return f'{path}\\{self.json.data["versuchstyp"]}_{timestamp}{extension}'

    def save(self, filepath):
        if filepath == '':
            # Fallback to Default Path if string is empty
            filepath = "./export/protocols"
        with open(self.gen_filename(filepath), 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.json.data))


class ProtocolPDF:
    def __init__(self, filename, data: ProtocolData):
        self.data = data.data
        self.__canv = canvas.Canvas(filename, pagesize=A4)
        self.__canv.setTitle('Versuchsprotokoll')
        self.__canv.setAuthor('Autor')
        self.__canv.setSubject('Subject')
        self.__elements = []
        self.__frame = Frame(0, 0, A4[0], A4[1])
        # Page 1
        self._space(20)
        self._logo()
        self._space(20)
        self._heading('Versuchsprotokoll', 22)
        self._space(20)
        self._sub_heading('Allgemein:', 12)
        self._space(10)
        self._table_general()
        self._space(20)
        self._sub_heading('Trigger-Konfiguration:', 12)
        self._space(30)
        self._table_trigger()
        self._space(20)
        self._sub_heading('Puls Vergleich Soll - Ist:', 12)
        self._space(8)
        self._puls_plot()
        self.__frame.addFromList(self.__elements, self.__canv)
        self.__canv.showPage()
        # Page 3
        self.__elements = []
        self.__frame_trace = Frame(0, 0, A4[0], A4[1])
        self._space(20)
        self._logo()
        self._space(40)
        self._trace_plot('Beschleunigung aus Geschwindigkeit:', "", "", self.data['trace_x'],
                         self.data['trace_acc_vel'])
        self._space(15)
        self._trace_plot('Beschleunigung aus Geschw. mit Filter:', "", "", self.data['trace_x'],
                         self.data['trace_acc_vel_filt'])
        self._space(15)
        self._trace_plot('Beschleunigung aus Weg:', "", "", self.data['trace_x'], self.data['trace_acc_way'])

        self.__frame_trace.addFromList(self.__elements, self.__canv)
        self.__canv.showPage()
        # Page 4
        self.__elements = []
        self.__frame_trace = Frame(0, 0, A4[0], A4[1])
        self._space(20)
        self._logo()
        self._space(40)
        self._trace_plot('Weg:', "", "", self.data['trace_x'], self.data['trace_way'])
        self._space(15)
        self._trace_plot('Spannung:', "", "", self.data['trace_x'], self.data['trace_voltage'])
        self._space(15)
        self._trace_plot('Geschwindigkeit:', "", "", self.data['trace_x'], self.data['trace_vel'])
        self.__frame_trace.addFromList(self.__elements, self.__canv)
        # Save
        self.__canv.save()

    def _logo(self, scale=0.5):
        logo = Image('./assets/logo.png')
        logo.drawWidth = logo.imageWidth * scale
        logo.drawHeight = logo.imageHeight * scale
        logo.hAlign = 'LEFT'
        logo.__setattr__('_offs_x', 30),
        self.__elements.append(logo)

    def _heading(self, text, size=24):
        s = styles.ParagraphStyle('Normal', alignment=1, fontSize=size)
        h = Paragraph(text, s)
        self.__elements.append(h)

    def _sub_heading(self, text, size=18):
        s = styles.ParagraphStyle('Normal', alignment=0, fontSize=size, leftIndent=60)
        h = Paragraph(text, s)
        self.__elements.append(h)

    def _space(self, size):
        sp = Spacer(10, size)
        self.__elements.append(sp)

    def _table_general(self):
        timestamp = "Alte File Version"
        try:
            timestamp = str(self.data['timestamp'])
        except Exception as e:
            pass
        data = [
            ["Versuchstyp:", self.data['versuchstyp']] + ["Start Position:", str(self.data['startpos']) + ' mm'],
            ["Versuchsnummer:", self.data['versuchsnummer']] + ["End Position:", str(self.data['endpos']) + ' mm'],
            ["Kommentar:", self.data['kommentar']] + ["Zuladung:", str(self.data['zuladung']) + ' kg'],
            ["Bediener:", self.data['bediener']] + ["Zeitpunkt:", timestamp]
        ]
        table = Table(data)
        tblStlye = TableStyle(
            [('GRID', (0, 0), (-1, -1), 1, colors.black),
             ]
        )
        table.setStyle(tblStlye)
        self.__elements.append(table)

    def _table_trigger(self):
        data = [
            ["Triggernr.", "Name", "Zeit", "Aktiv"] + ["Triggernr.", "Name", "Zeit", "Aktiv"],
            ["01", self.data['trigger']['01']['name'], self.data['trigger']['01']['zeit'],
             self.data['trigger']['01']['enabled']] + ["-", "-",
                                                       "-",
                                                       "-"],
            ["02", self.data['trigger']['02']['name'], self.data['trigger']['02']['zeit'],
             self.data['trigger']['02']['enabled']] + ["09", self.data['trigger']['09']['name'],
                                                       self.data['trigger']['09']['zeit'],
                                                       self.data['trigger']['09']['enabled']],
            ["03", self.data['trigger']['03']['name'], self.data['trigger']['03']['zeit'],
             self.data['trigger']['03']['enabled']] + ["10", self.data['trigger']['10']['name'],
                                                       self.data['trigger']['10']['zeit'],
                                                       self.data['trigger']['10']['enabled']],
            ["04", self.data['trigger']['04']['name'], self.data['trigger']['04']['zeit'],
             self.data['trigger']['04']['enabled']] + ["11", self.data['trigger']['11']['name'],
                                                       self.data['trigger']['11']['zeit'],
                                                       self.data['trigger']['11']['enabled']],
            ["05", self.data['trigger']['05']['name'], self.data['trigger']['05']['zeit'],
             self.data['trigger']['05']['enabled']] + ["12", self.data['trigger']['12']['name'],
                                                       self.data['trigger']['12']['zeit'],
                                                       self.data['trigger']['12']['enabled']],
            ["06", self.data['trigger']['06']['name'], self.data['trigger']['06']['zeit'],
             self.data['trigger']['06']['enabled']] + ["13", self.data['trigger']['13']['name'],
                                                       self.data['trigger']['13']['zeit'],
                                                       self.data['trigger']['13']['enabled']],
            ["07", self.data['trigger']['07']['name'], self.data['trigger']['07']['zeit'],
             self.data['trigger']['07']['enabled']] + ["14", self.data['trigger']['14']['name'],
                                                       self.data['trigger']['14']['zeit'],
                                                       self.data['trigger']['14']['enabled']],
            ["08", self.data['trigger']['08']['name'], self.data['trigger']['08']['zeit'],
             self.data['trigger']['08']['enabled']] + ["15", self.data['trigger']['15']['name'],
                                                       self.data['trigger']['15']['zeit'],
                                                       self.data['trigger']['15']['enabled']]

        ]
        table = Table(data, rowHeights=16)
        tblStlye = TableStyle(
            [('GRID', (0, 0), (-1, -1), 0, colors.black),
             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('FONTSIZE', (0, 0), (-1, -1), 8)
             ]
        )
        table.setStyle(tblStlye)
        self.__elements.append(table)

    def _puls_plot(self):
        data_soll_x = self.data['puls_x']
        data_soll_y = self.data['puls_y']
        data_ist_x = self.data['trace_x']
        data_ist_y = self.data['trace_acc_vel_filt']
        obj = io.BytesIO()
        fig = plt.figure(num=None, figsize=(10, 5.5))
        plt.plot(data_soll_x, data_soll_y)
        plt.plot([i * 1000 for i in data_ist_x], [i / 60 for i in data_ist_y])
        plt.xlabel('Zeit [ms]')
        plt.ylabel('Beschl. [m/s²]')
        plt.legend()
        fig.savefig(obj, dpi=300)
        obj.seek(0)
        image = Image(obj)
        image.drawWidth = (A4[0] / image.imageWidth) * image.imageWidth
        image.drawHeight = (A4[0] / image.imageWidth) * image.imageHeight
        self.__elements.append(image)

    def _trace_plot(self, title, xlabel, ylabel, x, y):
        scale = 0.5
        data_ist_x = x
        data_ist_y = y
        obj = io.BytesIO()
        fig = plt.figure(num=None, figsize=(10, 3.8))
        plt.plot(data_ist_x, data_ist_y)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        fig.savefig(obj, dpi=300)
        obj.seek(0)
        image = Image(obj)
        image.drawWidth = (A4[0] / image.imageWidth) * image.imageWidth
        image.drawHeight = (A4[0] / image.imageWidth) * image.imageHeight
        self.__elements.append(image)
