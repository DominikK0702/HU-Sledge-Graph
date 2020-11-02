import pyqtgraph as pg
import math

class OSGPulseGraphicsView():
    def __init__(self, graphicsview: pg.GraphicsLayoutWidget):
        self.gv = graphicsview
        pg.setConfigOptions(antialias=True)
        self.plot_item = None
        self.resetPlot()
        self.setPlot(pg.PlotItem(y=[math.sin(i/200) for i in range(1000)]))
        self.setup()


    def setup(self):
        self.gv.setBackground('#333333')

    def resetPlot(self):
        if self.plot_item is not None: self.gv.removeItem(self.plot_item)

        
    def setPlot(self, plotitem):
        self.resetPlot()
        self.plot_item = self.gv.addItem(plotitem)