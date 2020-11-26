from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
from scipy.special import comb


class OSGBezierROI(pg.ROI):
    def __init__(self, pStart, pEnd, parent, nPoints=1, nTimes=1000):
        self.pStart = pStart
        self.pEnd = pEnd
        self.parent = parent
        self.nPoints = nPoints
        self.nTimes = nTimes
        super(OSGBezierROI, self).__init__(pos=self.pStart)
        self.points = [self.get_point_factor(self.pStart, self.pEnd, i) for i in np.linspace(0, 1, self.nPoints+2)[1:-1]]
        for point in [self.pStart] + self.points + [self.pEnd]:
            self.addFreeHandle(point)

        self.plot_bezier()
        self.sigRegionChanged.connect(self.moved)

    def moved(self):
        self.plot_bezier()

    def plot_bezier(self):
        x, y = OSGBezierROI.bezier_curve([[i.get('pos').x(), i.get('pos').y()] for i in self.handles],
                                         nTimes=self.nTimes)
        self.parent.currentPlot.setData(x, y)

    def paint(self, p, opt, widget):
        pass

    @staticmethod
    def get_point_factor(p1, p2, fact):
        p1 = np.array(p1)
        p2 = np.array(p2)
        vec = p2 - p1
        return (vec * fact) + p1

    @staticmethod
    def bernstein_poly(i, n, t):
        """
         The Bernstein polynomial of n, i as a function of t
        """

        return comb(n, i) * (t ** (n - i)) * (1 - t) ** i

    @staticmethod
    def bezier_curve(points, nTimes=1000):
        """
           Given a set of control points, return the
           bezier curve defined by the control points.

           points should be a list of lists, or list of tuples
           such as [ [1,1],
                     [2,3],
                     [4,5], ..[Xn, Yn] ]
            nTimes is the number of time steps, defaults to 1000

            See http://processingjs.nihongoresources.com/bezierinfo/
        """

        nPoints = len(points)
        xPoints = np.array([p[0] for p in points])
        yPoints = np.array([p[1] for p in points])

        t = np.linspace(0.0, 1.0, nTimes)

        polynomial_array = np.array([OSGBezierROI.bernstein_poly(i, nPoints - 1, t) for i in range(0, nPoints)])

        xvals = np.dot(xPoints, polynomial_array)
        yvals = np.dot(yPoints, polynomial_array)

        return xvals, yvals


class PulseEditWidget(pg.PlotWidget):

    def __init__(self, *args, **kwargs):
        pg.setConfigOptions(antialias=True)
        super(PulseEditWidget, self).__init__(*args, **kwargs)
        self.datax = None
        self.datay = None
        self.setXRange(0, 10)
        self.setYRange(0, 10)
        self.currentPlot = None  # PlotItem
        self.currentPlot = self.plot([], [])
        self.addItem(OSGBezierROI([0, 0], [10, 10],self,2, 1000))
        self.show()


app = QtGui.QApplication([])
win = PulseEditWidget(show=True)

if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
