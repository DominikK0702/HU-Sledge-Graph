import pyqtgraph as pg
from Cursor import Cursor
from PIL import ImageColor


class Graph(pg.PlotWidget):
    def __init__(self, cfg):
        self.cfg = cfg

        super(Graph, self).__init__(enableMenu=self.cfg['GRAPH'].getboolean('enable_menu'))
        self.setMouseEnabled(x=self.cfg['GRAPH'].getboolean('mouseenable_x'),
                             y=self.cfg['GRAPH'].getboolean('mouseenable_x'))
        self.enableAutoRange(x=self.cfg['GRAPH'].getboolean('autorange_x'),
                             y=self.cfg['GRAPH'].getboolean('autorange_x'))
        self.showGrid(x=self.cfg['GRAPH'].getboolean('grid_x'), y=self.cfg['GRAPH'].getboolean('grid_y'))
        self.setXLabel(self.cfg['GRAPH']['name_ax_x'])
        self.setYLabel(self.cfg['GRAPH']['name_ax_y'])
        self.addLegend()
        self.pen_legend = pg.mkPen(color=ImageColor.getrgb('#' + self.cfg['GRAPH']['color_legend']),
                                   width=self.cfg['GRAPH'].getint('width_legend'))
        self.pen_trace_velocity = pg.mkPen(color=ImageColor.getrgb('#' + self.cfg['GRAPHTRACE']['color_axis_velocity']),
                                           width=self.cfg['GRAPHTRACE'].getint('width_axis_velocity'))
        self.pen_trace_2 = pg.mkPen(color=ImageColor.getrgb('#' + self.cfg['GRAPHTRACE']['color_axis_2']),
                                    width=self.cfg['GRAPHTRACE'].getint('width_axis_2'))
        self.pen_trace_voltage = pg.mkPen(color=ImageColor.getrgb('#' + self.cfg['GRAPHTRACE']['color_axis_voltage']),
                                          width=self.cfg['GRAPHTRACE'].getint('width_axis_voltage'))
        self.pen_trace_acceleration = pg.mkPen(
            color=ImageColor.getrgb('#' + self.cfg['GRAPHTRACE']['color_axis_acceleration']),
            width=self.cfg['GRAPHTRACE'].getint('width_axis_acceleration'))
        self.setBackground(self.cfg['GRAPH']['background_color'])
        self.cursor = Cursor(self)
        self.proxy = pg.SignalProxy(self.scene().sigMouseMoved, rateLimit=120, slot=self.mouseMoved)

        self.plotitem_trace_acc = None
        self.plotitem_trace_2 = None
        self.plotitem_trace_vel = None
        self.plotitem_trace_vol = None

    def mouseClicked(self, evt):
        clickEvent = evt[0]
        print(clickEvent.button())

    def mouseMoved(self, evt):
        if self.cursor.active:
            pos = evt[0]  ## using signal proxy turns original arguments into a tuple
            if self.sceneBoundingRect().contains(pos):
                mousePoint = self.getViewBox().mapSceneToView(pos)
                self.cursor.set_cursor_pos(mousePoint)

    def setXLabel(self, text):
        self.setLabel('bottom', text, color=self.cfg['GRAPH']['color_xlabel'])

    def setYLabel(self, text):
        self.setLabel('left', text, color=self.cfg['GRAPH']['color_ylabel'])

    def plot_trace(self, trace):
        self.clear()
        self.plotitem_trace_acc = self.plot(trace.get_axis_time(), trace.get_axis_acc_from_speed(filtered=True),
                                            pen=self.pen_trace_acceleration,
                                            name=self.cfg['GRAPHTRACE']['label_axis_acceleration'])

        self.plotitem_trace_vel = self.plot(trace.get_axis_time(), trace.get_axis_velocity(),
                                            pen=self.pen_trace_velocity,
                                            name=self.cfg['GRAPHTRACE']['label_axis_velocity'])

        self.plotitem_trace_vol = self.plot(trace.get_axis_time(), trace.get_axis_voltage(), pen=self.pen_trace_voltage,
                                            name=self.cfg['GRAPHTRACE']['label_axis_voltage'])

        self.plotitem_trace_2 = self.plot(trace.get_axis_time(), trace.get_axis_2(), pen=self.pen_trace_2,
                                          name=self.cfg['GRAPHTRACE']['label_axis_2'])

        self.setXLabel(self.cfg['GRAPH']['name_trace_ax_x'])
        self.setYLabel(self.cfg['GRAPH']['name_trace_ax_y'])
