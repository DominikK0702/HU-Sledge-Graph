import pyqtgraph as pg
from Cursor import Cursor
from TraceHelper import Trace
from PIL import ImageColor

class TraceAxis:
    def __init__(self, traceplot):
        self.trace_plot = traceplot
        self.enabled = False
        self.axis = None

    def addPlot(self, row, col, title):
        self.axis = self.trace_plot.addPlot(row=row, col=col, title=title)

    def plot(self, datax, datay):
        if self.axis is not None:
            self.axis.plot(datax, datay)

    def clearPlot(self):
        self.axis.clear()
        self.axis = None

    def linkY(self, axis):
        self.axis.setXLink(axis.axis)

class TracePlot(pg.GraphicsLayoutWidget):
    VM_MULTI = 0
    VM_SINGLE = 1

    def __init__(self, cfg):
        self.cfg = cfg
        super(TracePlot, self).__init__()
        self.viewmode = TracePlot.VM_MULTI
        self.plot_active = False
        self.config()
        self.trace = Trace()
        self.axis_01 = TraceAxis(self)
        self.axis_02 = TraceAxis(self)
        self.axis_03 = TraceAxis(self)
        self.axis_04 = TraceAxis(self)

    def config(self):
        self.setBackground((255,255,255))

    def load_trace_csv(self, filename):
        self.trace.load_trace_csv(filename=filename)
        self.plot_active = True

    def load_trace_acx(self, filename):
        self.trace.load_trace_acx(filename=filename)
        self.plot_active = True

    def autoRange(self):
        if self.plot_active:
            self.axis_01.axis.autoRange()

    def set_viewmode(self, viewmode):
        if self.plot_active and viewmode == TracePlot.VM_SINGLE:
            self.plot_trace_single()
        elif self.plot_active and viewmode == TracePlot.VM_MULTI:
            self.plot_trace_multi()

        self.viewmode = viewmode

    def clear_trace(self):
        self.trace.clear()
        self.clear()
        self.plot_active = False

    def plot_trace_single(self):
        pass

    def plot_trace_multi(self):
        self.clear()
        self.axis_01.addPlot(1,0, self.cfg['GRAPHTRACE']['label_axis_velocity'])
        self.axis_01.plot(self.trace.get_axis_time(), self.trace.get_axis_acc_from_speed(filtered=True))

        self.axis_02.addPlot(2, 0, self.cfg['GRAPHTRACE']['label_axis_2'])
        self.axis_02.plot(self.trace.get_axis_time(), self.trace.get_axis_2())

        self.axis_03.addPlot(3, 0, self.cfg['GRAPHTRACE']['label_axis_voltage'])
        self.axis_03.plot(self.trace.get_axis_time(), self.trace.get_axis_voltage())

        self.axis_04.addPlot(4, 0, self.cfg['GRAPHTRACE']['label_axis_acceleration'])
        self.axis_04.plot(self.trace.get_axis_time(), self.trace.get_axis_velocity())

        self.axis_01.linkY(self.axis_04)
        self.axis_02.linkY(self.axis_01)
        self.axis_03.linkY(self.axis_01)
        self.axis_04.linkY(self.axis_01)

        self.autoRange()



class Graph(pg.PlotWidget):
    def __init__(self, cfg):
        self.cfg = cfg

        super(Graph, self).__init__(enableMenu=self.cfg['GRAPH'].getboolean('enable_menu'))
        self.edit_mode = False
        self.dragging = False
        self.current_drag_pos = None
        self.drag_start_pos = None
        self.drag_end_pos = None
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
        self.proxy = pg.SignalProxy(self.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.proxy1 = pg.SignalProxy(self.scene().sigMouseClicked, rateLimit=60, slot=self.mouseClicked)
        self.plotitem_trace_acc = None
        self.plotitem_trace_2 = None
        self.plotitem_trace_vel = None
        self.plotitem_trace_vol = None


    def mouseClicked(self, evt):
        clickEvent = evt[0]
        if self.edit_mode and clickEvent.button() == pg.QtCore.Qt.LeftButton:
            self.dragging = not self.dragging
            if self.dragging:
                self.drag_start_pos = self.getViewBox().mapSceneToView(clickEvent.pos())
            else:
                self.drag_end_pos = self.getViewBox().mapSceneToView(clickEvent.pos())
                print('End:',self.drag_end_pos)

    def mouseMoved(self, evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.dragging:
            self.current_drag_pos = self.getViewBox().mapSceneToView(pos)
            print('Start:',self.drag_start_pos)
            print('Current', self.current_drag_pos)

        if self.cursor.active:
            if self.sceneBoundingRect().contains(pos):
                mousePoint = self.getViewBox().mapSceneToView(pos)
                self.cursor.set_cursor_pos(mousePoint)
                print(f"{mousePoint.x()} - {mousePoint.y()}")

    def toggle_edit_mode(self, state):
        if state:
            self.setMouseEnabled(x=False, y=False)
            self.edit_mode = True
        else:
            self.setMouseEnabled(x=self.cfg['GRAPH'].getboolean('mouseenable_x'),
                                 y=self.cfg['GRAPH'].getboolean('mouseenable_x'))
            self.edit_mode = False

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
