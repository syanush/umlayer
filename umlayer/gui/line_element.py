from enum import Enum

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from . import *


class LineType(Enum):
    Solid = 0
    Dash = 1
    Dot = 2


class TipType(Enum):
    Empty = 0
    Arrow = 1
    HollowTriangle = 2
    FullTriangle = 3
    HollowDiamond = 4
    FullDiamond = 5
    FullHalfTriangle = 6


class LineElement(QGraphicsItem, BaseElement):
    def __init__(self, x1: float = 0, y1: float = 0, x2: float = 0, y2: float = 0, text: str = None, parent=None):
        super().__init__(parent)
        BaseElement.__init__(self)
        self._abilities = {Abilities.EDITABLE_TEXT}

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        self._handle1 = HandleItem(Settings.LINE_HANDLE_SIZE, parent=self)
        self._handle1.position_changed_signal.connect(self._handle1_position_changed)
        self._handle1.selection_changed_signal.connect(self._handle_selection_changed)
        self._handle1.setSelected(False)

        self._handle2 = HandleItem(Settings.LINE_HANDLE_SIZE, parent=self)
        self._handle2.position_changed_signal.connect(self._handle2_position_changed)
        self._handle2.selection_changed_signal.connect(self._handle_selection_changed)
        self._handle2.setSelected(False)

        self.stroker = QPainterPathStroker()
        self.stroker.setWidth(Settings.LINE_STROKER_WIDTH)

        self._text = text or ''
        self._point1 = QPointF(x1, y1)
        self._point2 = QPointF(x2, y2)
        self._line_type = LineType.Solid
        self._tip1: TipType = TipType.Empty
        self._tip2: TipType = TipType.Empty
        self._tip1_figure: Tip = NoTip()
        self._tip2_figure: Tip = NoTip()

        self.setLive(False)
        self._recalculate()

    def text(self):
        return self._text

    def setText(self, text: str):
        if self._text != text:
            self._text = text
            self.notify()
            self._recalculate()

    def point1(self):
        return self._point1

    def setPoint1(self, x1: float, y1: float):
        point1 = QPointF(x1, y1)
        if self._point1 != point1:
            self._point1 = point1
            self.notify()
            self._recalculate()

    def point2(self):
        return self._point2

    def setPoint2(self, x2, y2):
        point2 = QPointF(x2, y2)
        if self._point2 != point2:
            self._point2 = point2
            self.notify()
            self._recalculate()

    def selectAll(self):
        self.setSelected(True)
        self._handle1.setSelected(True)
        self._handle2.setSelected(True)

    def setZValue(self, z: float) -> None:
        self._handle1.setZValue(z + 1.0)
        self._handle2.setZValue(z + 1.0)
        super().setZValue(z)

    def toDto(self):
        dto = super().toDto()
        dto['x1'] = self.point1().x()
        dto['y1'] = self.point1().y()
        dto['x2'] = self.point2().x()
        dto['y2'] = self.point2().y()
        dto['text'] = self.text()
        return dto

    def setFromDto(self, dto: dict):
        super().setFromDto(dto)
        self.setPoint1(dto['x1'], dto['y1'])
        self.setPoint2(dto['x2'], dto['y2'])
        self.setText(dto['text'])

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def shape(self) -> QPainterPath:
        return self._shape_path

    _pen_style_from_line_type = {
        LineType.Solid: Qt.SolidLine,
        LineType.Dash: Qt.DashLine,
        LineType.Dot: Qt.DotLine,
    }

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        def get_tip_brush(tip_type):
            if tip_type in [TipType.FullTriangle, TipType.FullDiamond, TipType.FullHalfTriangle]:
                brush = Settings.LINE_SELECTED_BRUSH if self.isSelected() else Settings.ELEMENT_NORMAL_BRUSH
            else:
                brush = Settings.ELEMENT_SELECTED_TRANSPARENT_BRUSH if self.isSelected() else Settings.ELEMENT_NORMAL_TRANSPARENT_BRUSH
            return brush

        x1 = self._tip1_figure.point().x()
        y1 = self._tip1_figure.point().y()
        x2 = self._tip2_figure.point().x()
        y2 = self._tip2_figure.point().y()

        pen = Settings.LINE_SELECTED_PEN if self.isSelected() else Settings.ELEMENT_NORMAL_PEN

        line_pen = QPen(pen)
        line_pen_style = self._pen_style_from_line_type[self._line_type]
        line_pen.setStyle(line_pen_style)

        painter.setPen(line_pen)
        painter.drawLine(x1, y1, x2, y2)

        painter.setPen(pen)

        painter.setBrush(get_tip_brush(self._tip1))
        self._tip1_figure.paint(painter)

        painter.setBrush(get_tip_brush(self._tip2))
        self._tip2_figure.paint(painter)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        self.positionNotify(change)
        if self.scene() and \
                change == QGraphicsItem.ItemPositionChange and \
                QApplication.mouseButtons() == Qt.LeftButton:
            return QPointF(gui_utils.snap(value.x()), gui_utils.snap(value.y()))
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            is_selected = bool(value)
            self.setLive(is_selected)
        return super().itemChange(change, value)

    def setLive(self, is_live):
        """A line must stay live when the line or its handle were selected"""
        is_really_live = is_live or self.isSelected() or self._handle1.isSelected() or self._handle2.isSelected()
        self._is_live = is_really_live
        self._handle1.setLive(is_really_live)
        self._handle2.setLive(is_really_live)
        self._recalculate()

    def _handle_selection_changed(self, is_selected):
        self.setLive(is_selected)

    def _handle1_position_changed(self, point):
        self.setPoint1(point.x(), point.y())

    def _handle2_position_changed(self, point):
        self.setPoint2(point.x(), point.y())

    _tip_class_from_tip_type = {
        TipType.Empty: NoTip,
        TipType.Arrow: ArrowTip,
        TipType.HollowTriangle: TriangleTip,
        TipType.FullTriangle: TriangleTip,
        TipType.HollowDiamond: DiamondTip,
        TipType.FullDiamond: DiamondTip,
        TipType.FullHalfTriangle: HalfTriangleTip
    }

    def _recalculate(self):
        self.prepareGeometryChange()
        self._parse_text()

        p1 = self.point1()
        p2 = self.point2()

        tip1_class = self._tip_class_from_tip_type[self._tip1]
        self._tip1_figure = tip1_class()
        self._tip1_figure.recalculate(p1, p2)

        tip2_class = self._tip_class_from_tip_type[self._tip2]
        self._tip2_figure = tip2_class()
        self._tip2_figure.recalculate(p2, p1)

        self._handle1.setPos(p1)
        self._handle2.setPos(p2)

        extra = max(self._tip1_figure.tip_size, self._tip2_figure.tip_size)
        rect = QRectF(p1, QSizeF(p2.x() - p1.x(), p2.y() - p1.y()))
        self._bounding_rect = rect.normalized().adjusted(-extra, -extra, extra, extra)

        path = QPainterPath()
        path.moveTo(p1)
        path.lineTo(p2)
        path.lineTo(p1)
        self._shape_path = self.stroker.createStroke(path)

        self.update()

    def _parse_text(self):
        """Parse

        Every line of text is either command or text for central label

        """
        label_lines = []
        lines = self.text().split('\n')
        for line in lines:
            if len(line) >= 4 and line[:3] == 'lt=':
                self.set_line_type_from_text(line[3:])
            else:
                label_lines.append(line)
        self._label_text = '\n'.join(label_lines)

    _tip_types = [TipType.Empty, TipType.Arrow, TipType.HollowTriangle,
                  TipType.FullTriangle, TipType.HollowDiamond, TipType.FullDiamond,
                  TipType.FullHalfTriangle]

    _tip1_type_from_txt = dict(zip(['', '<', '<<', '<<<', '<<<<', '<<<<<', '<<<<<<'], _tip_types))
    _tip2_type_from_txt = dict(zip(['', '>', '>>', '>>>', '>>>>', '>>>>>', '>>>>>>'], _tip_types))

    _lt_from_splitter = {
        '-': LineType.Solid,
        '.': LineType.Dash,
        '..': LineType.Dot,
    }

    def set_line_type_from_text(self, txt: str):
        """Parse line type"""

        if txt.find('-') >= 0:
            splitter = '-'
        elif txt.find('..') >= 0:
            splitter = '..'
        elif txt.find('.') >= 0:
            splitter = '.'
        else:
            splitter = '-'

        self._line_type = self._lt_from_splitter[splitter]

        tips = txt.split(splitter)

        self._tip1 = TipType.Empty
        if len(tips) > 0:
            self._tip1 = self._tip1_type_from_txt.get(tips[0]) or TipType.Empty

        self._tip2 = TipType.Empty
        if len(tips) > 1:
            self._tip2 = self._tip2_type_from_txt.get(tips[1]) or TipType.Empty
