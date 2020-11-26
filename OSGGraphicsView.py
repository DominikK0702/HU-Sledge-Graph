import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np


class CustomROI(pg.ROI):
    def __init__(self):
        super(CustomROI, self).__init__((0,0),size=[300,10])
        self.sigRegionChanged.connect(self.eve)

    def paint(self, p, *args):
        pen = QtGui.QPen(QtGui.QColor(255,255,255))
        pen.setWidth(0.5)
        p.setPen(pen)
        start = (0,0)
        for i in [(100,10),(200,10)]:
            p.drawLine(*start,*i)
            start = i





    def eve(self,ev):
        pos_handle01 = self.getHandles()[0].pos()+self.pos()
        pos_handle02 = self.getHandles()[1].pos() + self.pos()
        pos_handle03 = self.getHandles()[2].pos() + self.pos()

        print(1)



class OSGPulsePlotItem(pg.PlotItem):
    def __init__(self):
        super(OSGPulsePlotItem, self).__init__()



    def _plot_example(self):
        self.plot(np.arange(0,1000,1),[0]*999+[100])
        self.addItem(CustomROI())

class OSGPulseGraphicsView:
    def __init__(self, graphicsview: pg.GraphicsLayoutWidget):
        self.gv = graphicsview
        self.plot_item = OSGPulsePlotItem()
        self.setup()
        self.plot_item._plot_example()
        # Signals
        self.gv.scene().sigMouseClicked.connect(self.handle_mouse_clicked)

    def setup(self):
        # Global Config
        pg.setConfigOptions(antialias=True)
        self.gv.setBackground('#333333')
        # Init PlotItem
        self.gv.setCentralWidget(self.plot_item)

    def handle_mouse_clicked(self, event):
        if event.button() == pg.QtCore.Qt.LeftButton:
            mousepos = event.pos()
            mousepos.setX(mousepos.x() + 35) # todo warum ist da ein offset auf x???
            click_pos = self.plot_item.getViewBox().mapSceneToView(mousepos)
