import pyqtgraph as pg
from Cursor import Cursor
from TraceHelper import Trace
from PIL import ImageColor


class TraceAxis:
    def __init__(self, traceplot, axisname):
        self.trace_plot = traceplot
        self.name = axisname
        self.enabled = False
        self.axis = None
        self.pen = None

    def set_pen(self, hexrgb, width):
        self.pen = pg.mkPen(color='#' + hexrgb, width=1)

    def addPlot(self, row, col):
        self.axis = self.trace_plot.addPlot(row=row, col=col, title=self.name)

    def remove(self):
        self.trace_plot.removeItem(self.axis)

    def plot(self, datax, datay, pen=None):
        if self.axis is not None:
            if pen is None:
                pen = self.pen
            self.axis.plot(datax, datay, pen=pen)

    def clearPlot(self):
        self.axis.clear()

    def linkX(self, axis):
        self.axis.setXLink(axis.axis)


class TracePlot(pg.GraphicsLayoutWidget):
    VM_MULTI = 0
    VM_SINGLE = 1

    def __init__(self, cfg, mainwindow):
        self.cfg = cfg
        self.mainwindow = mainwindow
        super(TracePlot, self).__init__()
        self.viewmode = TracePlot.VM_MULTI
        self.plot_active = False
        self.config()
        self.trace = Trace()
        self.active_axis = []

    def config(self):
        self.setBackground((255, 255, 255))
        self.connect_btns()

    def connect_btns(self):
        self.mainwindow.cb_trace_ax_way.clicked.connect(self.change_axis)
        self.mainwindow.cb_trace_ax_vel.clicked.connect(self.change_axis)
        self.mainwindow.cb_trace_ax_voltage.clicked.connect(self.change_axis)
        self.mainwindow.cb_trace_ax_acc_way.clicked.connect(self.change_axis)
        self.mainwindow.cb_trace_ax_acc_vel.clicked.connect(self.change_axis)
        self.mainwindow.cb_trace_ax_acc_vel_filtered.clicked.connect(self.change_axis)
        self.mainwindow.cb_trace_view.currentIndexChanged.connect(self.set_viewmode)

    def change_axis(self):
        if not self.plot_active:
            return

        for i in self.active_axis:
            i.clearPlot()
            i.remove()

        self.active_axis = []

        row = 1
        if self.mainwindow.cb_trace_ax_way.isChecked():
            trace_axis = TraceAxis(self, self.cfg['GRAPHTRACE']['label_axis_way'])
            trace_axis.addPlot(row, 0)
            trace_axis.set_pen(self.cfg['GRAPHTRACE']['color_axis_way'], self.cfg['GRAPHTRACE']['width_axis_way'], )
            self.active_axis.append(trace_axis)
            if self.viewmode == TracePlot.VM_MULTI:
                row += 1
            else:
                return self.plot()

        if self.mainwindow.cb_trace_ax_vel.isChecked():
            trace_axis = TraceAxis(self, self.cfg['GRAPHTRACE']['label_axis_velocity'])
            trace_axis.addPlot(row, 0)
            trace_axis.set_pen(self.cfg['GRAPHTRACE']['color_axis_velocity'],
                               self.cfg['GRAPHTRACE']['width_axis_velocity'], )
            self.active_axis.append(trace_axis)
            if self.viewmode == TracePlot.VM_MULTI:
                row += 1
            else:
                return self.plot()

        if self.mainwindow.cb_trace_ax_voltage.isChecked():
            trace_axis = TraceAxis(self, self.cfg['GRAPHTRACE']['label_axis_voltage'])
            trace_axis.addPlot(row, 0)
            trace_axis.set_pen(self.cfg['GRAPHTRACE']['color_axis_voltage'],
                               self.cfg['GRAPHTRACE']['width_axis_voltage'], )
            self.active_axis.append(trace_axis)
            if self.viewmode == TracePlot.VM_MULTI:
                row += 1
            else:
                return self.plot()

        if self.mainwindow.cb_trace_ax_acc_way.isChecked():
            trace_axis = TraceAxis(self, self.cfg['GRAPHTRACE']['label_axis_acc_way'])
            trace_axis.addPlot(row, 0)
            trace_axis.set_pen(self.cfg['GRAPHTRACE']['color_axis_acc_way'],
                               self.cfg['GRAPHTRACE']['width_axis_acc_way'], )
            self.active_axis.append(trace_axis)
            if self.viewmode == TracePlot.VM_MULTI:
                row += 1
            else:
                return self.plot()

        if self.mainwindow.cb_trace_ax_acc_vel.isChecked():
            trace_axis = TraceAxis(self, self.cfg['GRAPHTRACE']['label_axis_acc_vel'])
            trace_axis.addPlot(row, 0)
            trace_axis.set_pen(self.cfg['GRAPHTRACE']['color_axis_acc_vel'],
                               self.cfg['GRAPHTRACE']['width_axis_acc_vel'], )
            self.active_axis.append(trace_axis)
            if self.viewmode == TracePlot.VM_MULTI:
                row += 1
            else:
                return self.plot()

        if self.mainwindow.cb_trace_ax_acc_vel_filtered.isChecked():
            trace_axis = TraceAxis(self, self.cfg['GRAPHTRACE']['label_axis_acc_vel_filtered'])
            trace_axis.addPlot(row, 0)
            trace_axis.set_pen(self.cfg['GRAPHTRACE']['color_axis_acc_vel_filtered'],
                               self.cfg['GRAPHTRACE']['width_axis_acc_vel_filtered'], )
            self.active_axis.append(trace_axis)
            if self.viewmode == TracePlot.VM_MULTI:
                row += 1
            else:
                return self.plot()

        self.plot()

    def load_trace_csv(self, filename):
        self.clear_trace()
        self.trace.load_trace_csv(filename=filename)
        self.plot_active = True
        self.change_axis()

    def load_trace_acx(self, filename):
        self.trace.load_trace_acx(filename=filename)
        self.plot_active = True
        self.change_axis()

    def autoRange(self):
        # if self.plot_active:
        #    self.ax_.axis.autoRange()
        pass

    def set_viewmode(self):
        index = self.mainwindow.cb_trace_view.currentIndex()
        if index == TracePlot.VM_MULTI:
            self.viewmode = TracePlot.VM_MULTI
        elif index == TracePlot.VM_SINGLE:
            self.viewmode = TracePlot.VM_SINGLE
        self.change_axis()

    def clear_trace(self):
        self.trace.clear()
        self.clear()
        self.active_axis = []
        self.plot_active = False

    def plot(self):
        first_ax = None
        last_ax = None
        for cnt, ax in enumerate(self.active_axis):
            if self.viewmode == TracePlot.VM_MULTI:
                if cnt == 0:
                    first_ax = ax
                elif cnt == len(self.active_axis) - 1:
                    last_ax = ax
                    first_ax.linkX(last_ax)
                else:
                    ax.linkX(first_ax)
            elif self.viewmode == TracePlot.VM_SINGLE:

                if self.mainwindow.cb_trace_ax_way.isChecked():
                    ax.plot(self.trace.get_axis_time(), self.trace.get_axis_way(),pen=pg.mkPen(
                        color=ImageColor.getrgb(f'#{self.cfg["GRAPHTRACE"]["color_axis_way"]}'),
                        width=self.cfg['GRAPHTRACE'].getint('width_axis_way')
                    ))

                if self.mainwindow.cb_trace_ax_vel.isChecked():
                    ax.plot(self.trace.get_axis_time(), self.trace.get_axis_velocity(),pen=pg.mkPen(
                        color=ImageColor.getrgb(f'#{self.cfg["GRAPHTRACE"]["color_axis_velocity"]}'),
                        width=self.cfg['GRAPHTRACE'].getint('width_axis_velocity')
                    ))

                if self.mainwindow.cb_trace_ax_voltage.isChecked():
                    ax.plot(self.trace.get_axis_time(), self.trace.get_axis_voltage(),pen=pg.mkPen(
                        color=ImageColor.getrgb(f'#{self.cfg["GRAPHTRACE"]["color_axis_voltage"]}'),
                        width=self.cfg['GRAPHTRACE'].getint('width_axis_voltage')
                    ))

                if self.mainwindow.cb_trace_ax_acc_way.isChecked():
                    ax.plot(self.trace.get_axis_time(), self.trace.get_axis_acceleration(),pen=pg.mkPen(
                        color=ImageColor.getrgb(f'#{self.cfg["GRAPHTRACE"]["color_axis_acc_way"]}'),
                        width=self.cfg['GRAPHTRACE'].getint('width_axis_acc_way')
                    ))

                if self.mainwindow.cb_trace_ax_acc_vel.isChecked():
                    ax.plot(self.trace.get_axis_time(), self.trace.get_axis_acc_from_speed(),pen=pg.mkPen(
                        color=ImageColor.getrgb(f'#{self.cfg["GRAPHTRACE"]["color_axis_acc_vel"]}'),
                        width=self.cfg['GRAPHTRACE'].getint('width_axis_acc_vel')
                    ))

                if self.mainwindow.cb_trace_ax_acc_vel_filtered.isChecked():
                    ax.plot(self.trace.get_axis_time(), self.trace.get_axis_acc_from_speed(filtered=True),pen=pg.mkPen(
                        color=ImageColor.getrgb(f'#{self.cfg["GRAPHTRACE"]["color_axis_acc_vel_filtered"]}'),
                        width=self.cfg['GRAPHTRACE'].getint('width_axis_acc_vel_filtered')
                    ))

            if ax.name == self.cfg['GRAPHTRACE']['label_axis_way']:
                ax.plot(self.trace.get_axis_time(), self.trace.get_axis_way())

            elif ax.name == self.cfg['GRAPHTRACE']['label_axis_velocity']:
                ax.plot(self.trace.get_axis_time(), self.trace.get_axis_velocity())

            elif ax.name == self.cfg['GRAPHTRACE']['label_axis_voltage']:
                ax.plot(self.trace.get_axis_time(), self.trace.get_axis_voltage())

            elif ax.name == self.cfg['GRAPHTRACE']['label_axis_acc_way']:
                ax.plot(self.trace.get_axis_time(), self.trace.get_axis_acceleration())

            elif ax.name == self.cfg['GRAPHTRACE']['label_axis_acc_vel']:
                ax.plot(self.trace.get_axis_time(), self.trace.get_axis_acc_from_speed())

            elif ax.name == self.cfg['GRAPHTRACE']['label_axis_acc_vel_filtered']:
                ax.plot(self.trace.get_axis_time(), self.trace.get_axis_acc_from_speed(filtered=True))

        self.mainwindow.tabWidget.setCurrentIndex(1)
        self.autoRange()


class Graph(pg.PlotWidget):
    def __init__(self, cfg, mainwindow):
        self.cfg = cfg
        self.mainwindow = mainwindow

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
        self.setBackground(self.cfg['GRAPH']['background_color'])
        self.cursor = Cursor(self)
        self.proxy = pg.SignalProxy(self.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.proxy1 = pg.SignalProxy(self.scene().sigMouseClicked, rateLimit=60, slot=self.mouseClicked)

    def mouseClicked(self, evt):
        clickEvent = evt[0]
        if self.edit_mode and clickEvent.button() == pg.QtCore.Qt.LeftButton:
            self.dragging = not self.dragging
            if self.dragging:
                self.drag_start_pos = self.getViewBox().mapSceneToView(clickEvent.pos())
            else:
                self.drag_end_pos = self.getViewBox().mapSceneToView(clickEvent.pos())
                print('End:', self.drag_end_pos)

    def mouseMoved(self, evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.dragging:
            self.current_drag_pos = self.getViewBox().mapSceneToView(pos)
            print('Start:', self.drag_start_pos)
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
