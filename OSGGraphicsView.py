import pyqtgraph as pg
import numpy as np
from OSGROIs import OSGBezierROI


class OSGPulsePlotItem(pg.PlotItem):
    def __init__(self):
        super(OSGPulsePlotItem, self).__init__()
        self.current_plot = self.plot()

    def _plot_example(self):
        self.current_plot = self.plot(np.arange(0, 1000, 1), [0] * 999 + [100])
        self.addItem(OSGBezierROI([0, 0], [10, 10, ], 1000, self))

    def setXYLabels(self, xlabel, ylabel, xunit=None, yunit=None):
        self.setLabel('bottom',text=xlabel, units=yunit)
        self.setLabel('left', text=ylabel, units=xunit)

    def plotPulse(self, datax, datay):
        self.current_plot.setData(datax, datay)
        self.setXYLabels('Time', 'Acceleration (G)', xunit='s')


class OSGPulseGraphicsView:
    def __init__(self, graphicsview: pg.GraphicsLayoutWidget):
        self.gv = graphicsview
        self.plot_item = OSGPulsePlotItem()
        self.setup()
        #self.plot_item._plot_example()
        # Signals
        self.gv.scene().sigMouseClicked.connect(self.handle_mouse_clicked)

    def setup(self):
        # Global Config
        pg.setConfigOptions(antialias=True)
        self.gv.setBackground('#FFFFFF')
        # Init PlotItem
        self.gv.setCentralWidget(self.plot_item)

    def handle_mouse_clicked(self, event):
        if event.button() == pg.QtCore.Qt.LeftButton:
            mousepos = event.pos()
            mousepos.setX(mousepos.x() + 35)  # todo warum ist da ein offset auf x???
            click_pos = self.plot_item.getViewBox().mapSceneToView(mousepos)
