import json
import datetime
import io
import matplotlib.pyplot as plt

from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer, PageBreak, PageTemplate
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader


class ProtocolJSON:
    def __init__(self):
        self.versuchsnummer = '132456789'
        self.versuchstyp = 'Crash Type XYZ mit Aufbau 123'
        self.bediener = 'Ignaz'
        self.kommentar = 'is vulle wäsch gegn di wond gfoan, was ned warum'
        self.startpos = '100'
        self.endpos = '1100'
        self.zuladung = '39'
        self.puls_x = [1, 2, 3, 4, 5]
        self.puls_y = [1, 2, 3, 4, 5]
        self.trace = None

    def set_trace(self, traceObj):
        self.trace = traceObj

    def load(self, file):
        with open(file, 'r', encoding='utf-8') as f:
            self.data = json.loads(f.read())

    def save(self, file):
        self.data = {
            'versuchsnummer'    : self.versuchsnummer,
            'versuchstyp'       : self.versuchstyp,
            'bediener'          : self.bediener,
            'kommentar'         : self.kommentar,
            'startpos'          : self.startpos,
            'endpos'            : self.endpos,
            'zuladung'          : self.zuladung,
            'puls_x'            : self.puls_x,
            'puls_y'            : self.puls_y,
            'trace_vel'         : self.trace.get_axis_velocity(),
            'trace_x'           : self.trace.get_axis_time(),
            'trace_way'         : self.trace.get_axis_way(),
            'trace_acc_way'     : self.trace.get_axis_acceleration(),
            'trace_acc_vel'     : self.trace.get_axis_acc_from_speed(filtered=False),
            'trace_acc_vel_filt': self.trace.get_axis_acc_from_speed(filtered=True),
            'trace_voltage'     : self.trace.get_axis_voltage()
        }
        with open(file, 'w', newline='', encoding='utf-8') as f:
            f.write(json.dumps(self.data))


class ProtocolPDF:
    def __init__(self, filename):
        self.doc = SimpleDocTemplate(filename, pagesize=A4)
        self.doc.title = 'Protokoll'
        self.elements = []
        # Document Format
        self._logo(0.4)
        self._heading()
        self._spacer(20)
        self._heading_section('Parameter:')
        self._table()
        self._spacer(20)
        #self._nextPage()
        self._heading_section('Vorgabe Puls:')
        self._plot([0,1,2,3,4],[4,3,2,4,5],
                   [0,1,2,3,4],[4,2,2,4,1],
                   'Zeit [ms]','Beschleunigung [G]','Puls Soll-Ist')


        self.doc.build(self.elements)

    def _nextPage(self):
        self.elements.append(PageBreak())

    def _logo(self,scale):
        logo = Image('./assets/logo.png')
        logo.drawHeight = logo.imageHeight*scale
        logo.drawWidth = logo.imageWidth*scale
        logo.__setattr__('_offs_x',-220)
        logo.__setattr__('_offs_y', 50)
        self.elements.append(logo)

    def _heading(self):
        heading_style = getSampleStyleSheet()['Heading1']
        heading_style.alignment = 1
        heading = Paragraph('Versuchsprotokoll',heading_style)
        self.elements.append(heading)

    def _heading_section(self, text):
        heading_style = getSampleStyleSheet()['Heading2']
        heading_style.alignment = 0
        heading = Paragraph(text,heading_style)
        self.elements.append(heading)

    def _spacer(self, size):
        spacer = Spacer(0,size)
        self.elements.append(spacer)

    def _plot(self,datax,datay, datax1,datay1,labelx,labely,title):
        plt.plot(datax,datay)
        plt.plot(datax1,datay1)
        plt.xlabel(labelx)
        plt.ylabel(labely)
        plt.title(title)
        image = io.BytesIO()
        plt.savefig(image,dpi=300)
        plot = Image(image)
        plot.drawWidth = plot.imageWidth * (A4[0] / plot.imageWidth)
        plot.drawHeight = plot.imageHeight * (A4[0] / plot.imageWidth)
        self.elements.append(plot)

    def _table(self):
        table_data = [
            [' '*40,' '*110],
            ['Versuchsnummer:', '132465798'],
            ['Versuchstyp:', 'ABC'],
            ['Bediener:', 'Ingnaz'],
            ['Kommentar:', 'kommentar der bisl länger it'],
            ['Startposition:','100 mm'],
            ['Endposition:', '1100 mm'],
            ['Zuladung:', '39 kg'],
            ['Datum:', datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')]

        ]
        tblStyle = TableStyle([('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                               ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                               ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),
                               ('LINEBELOW', (0, 1), (-1, -1), 1, colors.black),
                               ('BOX', (0, 1), (-1, -1), 1, colors.black),
                               ('BOX', (0, 1), (0, -1), 1, colors.black)])
        #tblStyle.add('BACKGROUND', (0, 0), (1, 0), colors.lightblue)
        tblStyle.add('BACKGROUND', (0, 1), (-1, -1), colors.white)
        table = Table(table_data,  rowHeights=20,hAlign='LEFT')
        table.setStyle(tblStyle)
        self.elements.append(table)


if __name__ == '__main__':
    class Page1:
        def __init__(self, canvas: Canvas):
            self.canvas = canvas

        def create(self):
            self._logo(0.4)
            self._heading('Versuchsprotokoll')
            self.canvas.showPage()

        def _logo(self, scale):
            logo = Image('./assets/logo.png')
            logo.drawHeight = logo.imageHeight * scale
            logo.drawWidth = logo.imageWidth * scale
            logo.drawOn(self.canvas,40,self.canvas._pagesize[1]-50)

        def _heading(self, text):
            heading_style = getSampleStyleSheet()['Heading1']
            heading_style.alignment = 1
            heading = Paragraph(text, heading_style)
            heading.drawOn(self.canvas,0,300)


    class Protocol(Canvas):
        def __init__(self, *args, **kwargs):
            Canvas.__init__(self, *args, **kwargs)
            self.setTitle('Versuchsprotokoll HU Sledge')
            self.page1 = Page1(self)
            self.page1.create()


    c = Protocol(filename='test.pdf',pagesize=A4)
    c.save()
