import abc
import math

from PySide6.QtCore import QPointF, QLineF
from PySide6.QtGui import QPainter, QPainterPath


class Tip(abc.ABC):
    tip_size = 0

    def __init__(self):
        self._path = None

    @abc.abstractmethod
    def recalculate(self, point1: QPointF, point2: QPointF):
        pass

    def paint(self, painter: QPainter):
        if self._path is not None:
            painter.drawPath(self._path)

    def point(self):
        return self._point

    def setPoint(self, point: QPointF):
        self._point = point


class NoTip(Tip):
    tip_size = 0

    def recalculate(self, point1: QPointF, point2: QPointF):
        self.setPoint(QPointF(point1))


class ArrowTip(Tip):
    tip_size = 15

    def recalculate(self, point1: QPointF, point2: QPointF):
        line = QLineF(point1, point2)
        angle = line.angle()
        line1 = QLineF.fromPolar(self.tip_size, angle + 30).translated(point1)
        line2 = QLineF.fromPolar(self.tip_size, angle - 30).translated(point1)
        self.setPoint(QPointF(point1))

        path = QPainterPath()
        path.moveTo(line1.p2())
        path.lineTo(point1)
        path.lineTo(line2.p2())
        self._path = path


class TriangleTip(Tip):
    tip_size = 15

    def recalculate(self, point1: QPointF, point2: QPointF):
        line = QLineF(point1, point2)
        angle = line.angle()
        line1 = QLineF.fromPolar(self.tip_size, angle + 30).translated(point1)
        line2 = QLineF.fromPolar(self.tip_size, angle - 30).translated(point1)
        line3 = QLineF(line1.p2(), line2.p2())
        self.setPoint(line3.center())

        path = QPainterPath()
        path.moveTo(point1)
        path.lineTo(line1.p2())
        path.lineTo(line2.p2())
        path.lineTo(point1)
        self._path = path


class HalfTriangleTip(Tip):
    tip_size = 15

    def recalculate(self, point1: QPointF, point2: QPointF):
        line = QLineF(point1, point2)
        angle = line.angle()
        line1 = QLineF.fromPolar(self.tip_size, angle + 30).translated(point1)
        line2 = QLineF.fromPolar(self.tip_size, angle - 30).translated(point1)
        line3 = QLineF(line1.p2(), line2.p2())
        self.setPoint(line3.center())

        path = QPainterPath()
        path.moveTo(point1)
        path.lineTo(line1.p2())
        path.lineTo(line3.center())
        path.lineTo(point1)
        self._path = path


class DiamondTip(Tip):
    tip_size = 15

    def recalculate(self, point1: QPointF, point2: QPointF):
        line = QLineF(point1, point2)
        angle = line.angle()
        line1 = QLineF.fromPolar(self.tip_size, angle + 30).translated(point1)
        line2 = QLineF.fromPolar(self.tip_size, angle - 30).translated(point1)
        line3 = QLineF.fromPolar(self.tip_size * math.sqrt(3), angle).translated(point1)
        self.setPoint(line3.p2())

        path = QPainterPath()
        path.moveTo(point1)
        path.lineTo(line1.p2())
        path.lineTo(line3.p2())
        path.lineTo(line2.p2())
        path.lineTo(point1)
        self._path = path
