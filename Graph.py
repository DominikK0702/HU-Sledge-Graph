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
        self.setBackground(self.cfg['GRAPH']['background_color'])
        self.cursor = Cursor(self)
        self.proxy = pg.SignalProxy(self.scene().sigMouseMoved, rateLimit=120, slot=self.mouseMoved)

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