import pyqtgraph as pg
from GraphCursor import Cursor
from PIL import ImageColor
from bisect import bisect_left
from scipy.signal import savgol_filter
from TraceHelper import offset_x_soll
from scipy import interpolate
from loguru import logger


def take_closest(array, value):
    return bisect_left(array, value)


class EditCurve(pg.PolyLineROI):

    def __init__(self, drawer):
        self.drawer = drawer
        self.points_count = 3
        self.mode_interpolate = False
        self.mode_standard = False
        self.mode_y_linked = False
        self.index = None
        self.linked = False
        self.points = []
        self.data = []
        self.line_pen = pg.mkPen(color=(0, 0, 0, 255), width=2)
        pg.PolyLineROI.__init__(self, [], movable=False)
        self.handleSize = 7
        self.handlePen.setColor(pg.QtGui.QColor(0, 0, 0))
        self.pen.setColor(pg.QtGui.QColor(0, 0, 0))

        self.sigRegionChangeFinished.connect(self.finished)

    def set_point_count(self, count):
        if count <= 2:
            count = 2
        if (count % 2) == 0:
            self.points_count = count + 1
        else:
            self.points_count = count

    def set_linked(self, state):
        self.linked = state

    def finished(self):
        data = []
        any = False
        for cnt, i in enumerate(self.handles):
            if i['pos'].__repr__().find('PyQt5.QtCore.QPointF') >= 0:
                any = True
                y = i['pos'].y()
                self.moved_y = y
                x = i['pos'].x()
                self.moved_x = x
                self.drawer.mainwindow.current_data_y[self.index - (self.points_count // 2) + cnt] = y
        if any:
            if self.mode_y_linked:
                for cnt, i in enumerate(self.handles):
                    self.drawer.mainwindow.current_data_y[self.index - (self.points_count // 2) + cnt] = self.moved_y

            elif self.mode_interpolate:
                x = [self.handles[0]['pos'].x(),x,self.handles[-1]['pos'].x(),self.handles[-1]['pos'].x()+0.0001]
                y = [self.handles[0]['pos'].y(),y,self.handles[-1]['pos'].y(),self.handles[-1]['pos'].y()]
                try:
                    f = interpolate.interp1d(x, y, kind='cubic')
                except:
                    logger.error("Drag Pulse Interpolate canceled")
                    return
                intp = [f(i['pos'].x()) for i in self.handles]
                for cnt, i in enumerate(intp):
                    self.drawer.mainwindow.current_data_y[self.index - (self.points_count // 2) + cnt] = float(i)

            self.drawer.plot(self.drawer.mainwindow.current_data_x, self.drawer.mainwindow.current_data_y, clear=True,
                             pen=self.drawer.mainwindow.pen_current,
                             name=self.drawer.cfg['STRINGS']['graph_current_label'])
            self.drawer.setTitle(f'{self.drawer.mainwindow.current_file_name} Modifiziert')
            self.drawer.getPlotItem().legend.setPen(self.drawer.pen_legend)

    def setDataPoints(self, datax, datay, pos):
        self.mode_interpolate = self.drawer.mainwindow.radioButton_interpolate.isChecked()
        self.mode_standard = self.drawer.mainwindow.radioButton_standard.isChecked()
        self.mode_y_linked = self.drawer.mainwindow.radioButton_y_linked.isChecked()
        self.points = []
        self.data = []
        for cnt, i in enumerate(datax):
            self.data.append([i, datay[cnt]])
        self.index = take_closest(datax, pos.x())
        self.points = self.data[self.index - self.points_count // 2:self.index + (self.points_count // 2) + 1]
        self.setPoints(self.points, closed=False)
        for h in self.handles:
            h['item'].xChanged.connect(self.lock_x)
            h['item'].yChanged.connect(self.intp_y)

    def lock_x(self):
        for cnt, i in enumerate(self.points):
            self.handles[cnt]['item'].setX(i[0])

    def intp_y(self):
        if self.mode_interpolate:
            try:
                any = False
                for cnt, i in enumerate(self.handles):
                    if i['pos'].__repr__().find('PyQt5.QtCore.QPointF') >= 0:
                        self.moved_y = i['pos'].y()
                        self.moved_x = self.points[cnt][0]
                        #self.moved_x = i['pos'].x()
                        any = True

                if any:
                    x = [self.handles[0]['pos'].x(), self.moved_x, self.handles[-1]['pos'].x(), self.handles[-1]['pos'].x() + 0.000001]
                    y = [self.handles[0]['pos'].y(), self.moved_y, self.handles[-1]['pos'].y(), self.handles[-1]['pos'].y()]
                    f = interpolate.interp1d(x, y, kind='cubic')
                    intp = [f(i['pos'].x()) for i in self.handles]
                    for cnt, i in enumerate(intp):
                        self.handles[cnt]['item'].setY(i)
                        #self.drawer.mainwindow.current_data_y[self.index - (self.points_count // 2) + cnt] = float(i)
            except Exception as e:
                self.drawer.mainwindow.statusbar.showMessage(str(e))

        elif self.mode_y_linked:
            any = False
            for cnt, i in enumerate(self.handles):
                if i['pos'].__repr__().find('PyQt5.QtCore.QPointF') >= 0:
                    self.moved_y = i['pos'].y()
                    self.moved_x = self.points[cnt][0]
                    # self.moved_x = i['pos'].x()
                    any = True

            if any:
                for cnt, i in enumerate(self.handles):
                    i['item'].setY(self.moved_y)


class Graph(pg.PlotWidget):
    def __init__(self, cfg, mainwindow):
        self.cfg = cfg
        self.mainwindow = mainwindow
        super(Graph, self).__init__()
        self.edit_mode = False
        self.current_mouse_pos = None
        self.bez = None
        self.setMouseEnabled(x=self.cfg['GRAPH'].getboolean('mouseenable_x'),
                             y=self.cfg['GRAPH'].getboolean('mouseenable_x'))
        self.enableAutoRange(x=self.cfg['GRAPH'].getboolean('autorange_x'),
                             y=self.cfg['GRAPH'].getboolean('autorange_x'))
        self.showGrid(x=self.cfg['GRAPH'].getboolean('grid_x'),
                      y=self.cfg['GRAPH'].getboolean('grid_y'))
        self.setXLabel(self.cfg['GRAPH']['name_ax_x'])
        self.setYLabel(self.cfg['GRAPH']['name_ax_y'])
        self.addLegend()
        self.pen_legend = pg.mkPen(color=ImageColor.getrgb('#' + self.cfg['GRAPH']['color_legend']),
                                   width=self.cfg['GRAPH'].getint('width_legend'))
        self.pen_soll = pg.mkPen(color=ImageColor.getrgb('#' + self.cfg['GRAPH']['color_compare_soll']),
                                 width=self.cfg['GRAPH'].getint('width_compare_soll'))
        self.pen_ist = pg.mkPen(color=ImageColor.getrgb('#' + self.cfg['GRAPH']['color_compare_ist']),
                                width=self.cfg['GRAPH'].getint('width_compare_ist'))
        self.setBackground(self.cfg['GRAPH']['background_color'])
        self.cursor = Cursor(self)
        self.proxy_mousemove = pg.SignalProxy(self.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.proxy_mouseclick = pg.SignalProxy(self.scene().sigMouseClicked, rateLimit=60, slot=self.mouseClicked)
        self.connect_components()

    def connect_components(self):
        self.mainwindow.cb_pulse_view.currentIndexChanged.connect(self.view_changed)

    def view_changed(self):
        # todo Untereinander Überlappend
        print(1)

    def auto_range(self):
        self.autoRange()

    def add_edit_rois(self):
        pos = self.getViewBox().mapSceneToView(self.current_mouse_pos)
        if self.bez:
            self.removeItem(self.bez)
        self.bez = EditCurve(self)
        self.bez.set_point_count(self.mainwindow.spinBox_PulseEditPointCount.value())
        self.bez.set_linked(self.mainwindow.radioButton_y_linked.isChecked())
        self.bez.setDataPoints(self.mainwindow.current_data_x, self.mainwindow.current_data_y, pos)
        self.addItem(self.bez)

    def mouseClicked(self, evt):
        clickEvent = evt[0]
        if self.edit_mode and clickEvent.button() == pg.QtCore.Qt.LeftButton:
            if len(self.mainwindow.current_data_x) <= 0:
                return
            self.add_edit_rois()

    def mouseMoved(self, evt):
        pos = evt[0]
        self.current_mouse_pos = pos
        if self.cursor.active:
            if self.sceneBoundingRect().contains(pos):
                mousePoint = self.getViewBox().mapSceneToView(pos)
                self.cursor.set_cursor_pos(mousePoint)

    def toggle_edit_mode(self, state):
        self.edit_mode = state

    def setXLabel(self, text):
        self.setLabel('bottom', text, color=self.cfg['GRAPH']['color_xlabel'])

    def setYLabel(self, text):
        self.setLabel('left', text, color=self.cfg['GRAPH']['color_ylabel'])

    def plot_compare(self, trace, data_soll):
        # Plot Soll
        offset_soll = 50
        scaled_soll_data = [i * 0.981 for i in data_soll]
        soll_x = [i * 1000 for i in offset_x_soll(data_soll, offset_soll)]
        self.plot(soll_x,
                  scaled_soll_data,
                  pen=self.pen_soll, name=self.cfg['STRINGS']['graph_soll_label'])


        cut_trace = True
        pulsdauer = soll_x[-1] + 50
        ist_x = []
        ist_y = []
        if cut_trace:
            ist_x = [i * 1000 for i in trace.get_axis_time() if i*1000 <= pulsdauer]
            ist_y = [i/60 for i in trace.get_axis_acc_from_speed(filtered=True)[:len(ist_x)]]
        else:
            ist_x = [i * 1000 for i in trace.get_axis_time()]
            ist_y = [i/60 for i in trace.get_axis_acc_from_speed(filtered=True)]
        # Plot Ist
        self.plot(ist_x, ist_y,
                  pen=self.pen_ist, name=self.cfg['STRINGS']['graph_ist_label'])


        self.auto_range()
        self.setXLabel(self.cfg['GRAPH']['name_ax_compare_x'])
        self.setYLabel(self.cfg['GRAPH']['name_ax_compare_y'])
        self.getPlotItem().legend.setPen(self.pen_legend)
