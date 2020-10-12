import pyqtgraph as pg


class OSGPulseGraph(pg.PlotWidget):
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        super(OSGPulseGraph, self).__init__()

        self.setBackground('#FFFFFF')

    def plot_pulse(self, datax, datay):
        self.clear()
        self.plot(datax,datay)
        self.autoRange()