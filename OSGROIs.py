import pyqtgraph as pg
import numpy as np
from scipy.special import comb





class OSGBezierROI(pg.ROI):
    def __init__(self, p1, p4, nTimes, parent):
        self.p1 = p1
        self.p4 = p4
        self.p2 = self.get_point_factor(self.p1, self.p4, 0.25)
        self.p3 = self.get_point_factor(self.p1, self.p4, 0.75)
        self.nTimes = nTimes

        self.parent = parent
        super(OSGBezierROI, self).__init__(pos=self.p1)
        self.handlePen = pg.QtGui.QPen()
        self.handlePen.setWidth(4)
        self.handlePen.setColor(pg.QtGui.QColor(255, 0, 0))

        self.handle_p1 = self.addFreeHandle(self.p1)
        self.handle_p4 = self.addFreeHandle(self.p4)
        self.handle_p2 = self.addFreeHandle(self.p2)
        self.handle_p3 = self.addFreeHandle(self.p3)
        self.plot_bezier()

        self.sigRegionChanged.connect(self.moved)

    def bernstein_poly(self, i, n, t):
        """
         The Bernstein polynomial of n, i as a function of t
        """

        return comb(n, i) * (t ** (n - i)) * (1 - t) ** i

    def bezier_curve(self, points, nTimes=1000):
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

        polynomial_array = np.array([self.bernstein_poly(i, nPoints - 1, t) for i in range(0, nPoints)])

        xvals = np.dot(xPoints, polynomial_array)
        yvals = np.dot(yPoints, polynomial_array)

        return xvals, yvals

    def moved(self):
        self.plot_bezier()

    def plot_bezier(self):
        x, y = self.bezier_curve([self.handle_p1.pos(),
                             self.handle_p2.pos(),
                             self.handle_p3.pos(),
                             self.handle_p4.pos()],
                            nTimes=self.nTimes)
        self.parent.current_plot.setData(x, y)

    def paint(self, p, opt, widget):
        pass

    @staticmethod
    def get_point_factor(p1, p2, fact):
        p1 = np.array(p1)
        p2 = np.array(p2)
        vec = p2 - p1
        return (vec * fact) + p1

