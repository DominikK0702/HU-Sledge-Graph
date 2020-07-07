import pyqtgraph as pg
from GraphCursor import Cursor
from PIL import ImageColor
from bisect import bisect_left
from scipy.signal import savgol_filter
from TraceHelper import offset_x_soll


def take_closest(array, value):
    return bisect_left(array, value)


class EditCurve(pg.PolyLineROI):

    def __init__(self, drawer):
        self.drawer = drawer
        self.points_count = 3
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
                self.drawer.mainwindow.current_data_y[self.index - (self.points_count//2) + cnt] = y
        if any:
            if self.linked:
                for cnt, i in enumerate(self.handles):
                        self.drawer.mainwindow.current_data_y[self.index - (self.points_count // 2) + cnt] = y


            self.drawer.plot(self.drawer.mainwindow.current_data_x, self.drawer.mainwindow.current_data_y, clear=True,
                             pen=self.drawer.mainwindow.pen_current,
                             name=self.drawer.cfg['STRINGS']['graph_current_label'])
            self.drawer.getPlotItem().legend.setPen(self.drawer.pen_legend)

    def setDataPoints(self, datax, datay, pos):
        self.points = []
        self.data = []
        for cnt, i in enumerate(datax):
            self.data.append([i, datay[cnt]])
        self.index = take_closest(datax, pos.x())
        self.points = self.data[self.index - self.points_count//2:self.index + (self.points_count//2)+1]
        self.setPoints(self.points, closed=False)
        for i in self.getHandles():
            print(i)
            #todo mhmhmh


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

    def add_edit_rois(self):
        pos = self.getViewBox().mapSceneToView(self.current_mouse_pos)
        if self.bez:
            self.removeItem(self.bez)
        self.bez = EditCurve(self)
        self.bez.set_point_count(self.mainwindow.spinBox_PulseEditPointCount.value())
        self.bez.set_linked(self.mainwindow.checkBox_pulseLinked.isChecked())
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
        self.plot(trace.get_axis_time(),
                  trace.get_axis_acc_from_speed(filtered=True),
                  pen=self.pen_ist, name=self.cfg['STRINGS']['graph_ist_label'])
        # Plot Ist
        self.plot(offset_x_soll(data_soll, 0),
                  data_soll,
                  pen=self.pen_soll, name=self.cfg['STRINGS']['graph_soll_label'])
        self.getPlotItem().legend.setPen(self.pen_legend)
