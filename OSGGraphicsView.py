import pyqtgraph as pg
import numpy as np

class OSGPulsePlotItem(pg.PlotItem):
    def __init__(self):
        super(OSGPulsePlotItem, self).__init__()

    def _plot_example(self):
        self.plot(np.arange(0,1000,1), np.sin(np.arange(0,10,0.01)))

class OSGPulseGraphicsView:
    def __init__(self, graphicsview: pg.GraphicsLayoutWidget):
        self.gv = graphicsview
        self.plot_item = OSGPulsePlotItem()
        self.setup()
        self.plot_item._plot_example()

    def setup(self):
        # Global Config
        pg.setConfigOptions(antialias=True)
        self.gv.setBackground('#333333')
        # Init PlotItem
        self.gv.setCentralWidget(self.plot_item)