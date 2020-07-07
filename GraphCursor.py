import pyqtgraph as pg
from PIL import ImageColor


class Cursor:
    def __init__(self, graph):
        self.graph = graph
        self.cfg = self.graph.cfg
        self.active = False
        self.pen_h = pg.mkPen(color=ImageColor.getrgb(f"#{self.cfg['GRAPHCURSOR']['color_h']}"),
                              width=self.cfg['GRAPHCURSOR'].getint('width_h'))
        self.pen_v = pg.mkPen(color=ImageColor.getrgb(f"#{self.cfg['GRAPHCURSOR']['color_v']}"),
                              width=self.cfg['GRAPHCURSOR'].getint('width_v'))
        self.cursorhLine = pg.InfiniteLine(angle=0, movable=False, pen=self.pen_h)
        self.cursorvLine = pg.InfiniteLine(angle=90, movable=False, pen=self.pen_v)

    def enabled(self, state):
        self.active = state
        if state:
            self.graph.addItem(self.cursorhLine, ignoreBounds=True)
            self.graph.addItem(self.cursorvLine, ignoreBounds=True)
        else:
            self.graph.removeItem(self.cursorhLine)
            self.graph.removeItem(self.cursorvLine)

    def set_cursor_pos(self, pos):
        self.cursorvLine.setPos(pos.x())
        self.cursorhLine.setPos(pos.y())
