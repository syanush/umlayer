from enum import Enum

from PySide6.QtCore import Qt, QPointF, QRectF, QLineF
from PySide6.QtGui import QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QGraphicsScene,
    QStyleOptionGraphicsItem,
)

from . import (
    gui_utils,
    Abilities,
    BaseElement,
    Settings,
    NoTip,
    Tip,
    HandleItem,
    ArrowTip,
    TriangleTip,
    DiamondTip,
    HalfTriangleTip,
)


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


class LineElement(BaseElement):
    def __init__(
        self,
        x1: float = 0,
        y1: float = 0,
        x2: float = 0,
        y2: float = 0,
        text: str = None,
        parent=None,
    ):
        super().__init__(parent=parent)
        self._abilities = {Abilities.EDITABLE_TEXT}

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        self._text = text or ""

        self._line_type = LineType.Solid
        self._tip1: TipType = TipType.Empty
        self._tip2: TipType = TipType.Empty
        self._tip1_figure: Tip = NoTip()
        self._tip2_figure: Tip = NoTip()

        self._handle = {
            1: HandleItem(Settings.LINE_HANDLE_SIZE),
            2: HandleItem(Settings.LINE_HANDLE_SIZE),
        }

        self.is_move_enabled = True
        self._position = QPointF()
        self.on_zvalue_change()

        self.setPoint1(x1, y1)
        self.setPoint2(x2, y2)

        self._handle[1].position_changed_signal.connect(self.on_handle1_move)
        self._handle[2].position_changed_signal.connect(self.on_handle2_move)

        for handle in self._handle.values():
            handle.selection_changed_signal.connect(self._handle_selection_changed)

        self.setLive(False)
        # self._recalculate()

    def on_scene_change(self, scene: QGraphicsScene):
        for handle in self._handle.values():
            if scene is None:
                self.scene().removeItem(handle)
            else:
                scene.addItem(handle)

    def on_zvalue_change(self):
        for handle in self._handle.values():
            handle.setZValue(self.zValue() + 1.0)

    def text(self):
        return self._text

    def setText(self, text: str):
        if self._text != text:
            self._text = text
            self.recalculate_handle_move()
            self.notify()

    def point1(self):
        return self._point1

    def setPoint1(self, x: float, y: float):
        point = QPointF(x, y)
        self.is_move_enabled = False
        self._handle[1].setPos(self.pos() + point)
        self.is_move_enabled = True
        self._recalculate()
        self.notify()

    def point2(self):
        return self._point2

    def setPoint2(self, x: float, y: float):
        point = QPointF(x, y)
        self.is_move_enabled = False
        self._handle[2].setPos(self.pos() + point)
        self.is_move_enabled = True
        self._recalculate()
        self.notify()

    def selectAll(self):
        self.setSelected(True)
        for handle in self._handle.values():
            handle.setSelected(True)

    def toDto(self):
        dto = super().toDto()
        dto["x1"] = self.point1().x()
        dto["y1"] = self.point1().y()
        dto["x2"] = self.point2().x()
        dto["y2"] = self.point2().y()
        dto["text"] = self.text()
        return dto

    def setFromDto(self, dto: dict):
        super().setFromDto(dto)
        self.setPoint1(dto["x1"], dto["y1"])
        self.setPoint2(dto["x2"], dto["y2"])
        self.setText(dto["text"])

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def shape(self) -> QPainterPath:
        return self._shape_path

    def calculateShape(self, point1, point2):
        line = QLineF(point1, point2)
        angle = line.angle()
        line1 = QLineF.fromPolar(Settings.LINE_HALF_WIDTH, angle + 90).translated(
            point1
        )
        line2 = QLineF.fromPolar(Settings.LINE_HALF_WIDTH, angle - 90).translated(
            point1
        )
        line3 = QLineF.fromPolar(Settings.LINE_HALF_WIDTH, angle - 90).translated(
            point2
        )
        line4 = QLineF.fromPolar(Settings.LINE_HALF_WIDTH, angle + 90).translated(
            point2
        )

        path = QPainterPath()
        path.moveTo(line1.p2())
        path.lineTo(line2.p2())
        path.lineTo(line3.p2())
        path.lineTo(line4.p2())
        path.lineTo(line1.p2())
        return path

    _pen_style_from_line_type = {
        LineType.Solid: Qt.SolidLine,
        LineType.Dash: Qt.DashLine,
        LineType.Dot: Qt.DotLine,
    }

    def paint(
        self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None
    ) -> None:
        def get_tip_brush(tip_type):
            if tip_type in [
                TipType.FullTriangle,
                TipType.FullDiamond,
                TipType.FullHalfTriangle,
            ]:
                brush = (
                    Settings.LINE_SELECTED_BRUSH
                    if self.isSelected()
                    else Settings.ELEMENT_NORMAL_BRUSH
                )
            else:
                brush = (
                    Settings.ELEMENT_SELECTED_TRANSPARENT_BRUSH
                    if self.isSelected()
                    else Settings.ELEMENT_NORMAL_TRANSPARENT_BRUSH
                )
            return brush

        x1 = self._tip1_figure.point().x()
        y1 = self._tip1_figure.point().y()
        x2 = self._tip2_figure.point().x()
        y2 = self._tip2_figure.point().y()

        pen = (
            Settings.LINE_SELECTED_PEN
            if self.isSelected()
            else Settings.ELEMENT_NORMAL_PEN
        )

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

        # pen = Settings.ELEMENT_SELECTED_PEN if self.isSelected() else Settings.ELEMENT_NORMAL_PEN
        # painter.setPen(pen)
        # painter.setBrush(Settings.ELEMENT_NORMAL_TRANSPARENT_BRUSH)
        # painter.drawRect(self.boundingRect())
        #
        # painter.drawPath(self.shape())

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        self.positionNotify(change)
        if (
            self.scene()
            and change == QGraphicsItem.ItemPositionChange
            and QApplication.mouseButtons() == Qt.LeftButton
        ):
            return QPointF(gui_utils.snap(value.x()), gui_utils.snap(value.y()))
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.on_item_move(value)
        if change == QGraphicsItem.ItemSceneChange:
            self.on_scene_change(value)
        if change == QGraphicsItem.ItemZValueHasChanged:
            self.on_zvalue_change()
        if change == QGraphicsItem.ItemSelectedHasChanged:
            is_selected = bool(value)
            self.setLive(is_selected)
        return super().itemChange(change, value)

    def setLive(self, is_live):
        """A line must stay live when the line or its handle were selected"""
        is_really_live = (
            is_live
            or self.isSelected()
            or self._handle[1].isSelected()
            or self._handle[2].isSelected()
        )
        self._is_live = is_really_live
        for handle in self._handle.values():
            handle.setLive(is_really_live)
        # self.update()

    def _handle_selection_changed(self, is_selected):
        self.setLive(is_selected)

    def on_item_move(self, position):
        if self.is_move_enabled:
            delta = position - self._position
            self._position = position
            self.recalculate_item_move(delta)

    def recalculate_item_move(self, delta):
        """item -> handles"""
        self.prepareGeometryChange()

        self.is_move_enabled = False
        for handle in self._handle.values():
            handle.moveBy(delta.x(), delta.y())
        self.is_move_enabled = True

        self.update()

    def on_handle1_move(self, point):
        if self.is_move_enabled:
            self.recalculate_handle_move()

    def on_handle2_move(self, point):
        if self.is_move_enabled:
            self.recalculate_handle_move()

    def recalculate_handle_move(self):
        """handles -> item"""
        initial_rect = QRectF(self._handle[1].pos(), self._handle[2].pos()).normalized()
        self.is_move_enabled = False
        self.setPos(initial_rect.topLeft())
        self.is_move_enabled = True
        self._position = self.pos()
        self._recalculate()

    _tip_class_from_tip_type = {
        TipType.Empty: NoTip,
        TipType.Arrow: ArrowTip,
        TipType.HollowTriangle: TriangleTip,
        TipType.FullTriangle: TriangleTip,
        TipType.HollowDiamond: DiamondTip,
        TipType.FullDiamond: DiamondTip,
        TipType.FullHalfTriangle: HalfTriangleTip,
    }

    def _recalculate(self):
        self.prepareGeometryChange()
        self._parse_text()

        p1 = self._handle[1].pos()
        p2 = self._handle[2].pos()

        initial_rect = QRectF(p1, p2).normalized()
        topLeft = initial_rect.topLeft()
        q1 = p1 - topLeft
        q2 = p2 - topLeft

        self._point1 = q1
        self._point2 = q2

        self._shape_path = self.calculateShape(q1, q2)

        tip1_class = self._tip_class_from_tip_type[self._tip1]
        self._tip1_figure = tip1_class()
        self._tip1_figure.recalculate(q1, q2)
        tip2_class = self._tip_class_from_tip_type[self._tip2]
        self._tip2_figure = tip2_class()
        self._tip2_figure.recalculate(q2, q1)

        max_size = max(
            Settings.ELEMENT_PEN_SIZE,
            Settings.ELEMENT_SHAPE_SIZE,
            self._tip1_figure.tip_size,
            self._tip2_figure.tip_size,
        )

        extra = Settings.LINE_HANDLE_SIZE + max_size / 2
        final_rect = QRectF(q1, q2).normalized()
        self._bounding_rect = final_rect.adjusted(-extra, -extra, extra, extra)

        self.update()

    def _parse_text(self):
        """Parse

        Every line of text is either command or text for central label

        """
        label_lines = []
        lines = self.text().split("\n")
        for line in lines:
            if len(line) >= 4 and line[:3] == "lt=":
                self.set_line_type_from_text(line[3:])
            else:
                label_lines.append(line)
        self._label_text = "\n".join(label_lines)

    _tip_types = [
        TipType.Empty,
        TipType.Arrow,
        TipType.HollowTriangle,
        TipType.FullTriangle,
        TipType.HollowDiamond,
        TipType.FullDiamond,
        TipType.FullHalfTriangle,
    ]

    _tip1_type_from_txt = dict(
        zip(["", "<", "<<", "<<<", "<<<<", "<<<<<", "<<<<<<"], _tip_types)
    )
    _tip2_type_from_txt = dict(
        zip(["", ">", ">>", ">>>", ">>>>", ">>>>>", ">>>>>>"], _tip_types)
    )

    _lt_from_splitter = {
        "-": LineType.Solid,
        ".": LineType.Dash,
        "..": LineType.Dot,
    }

    def set_line_type_from_text(self, txt: str):
        """Parse line type"""

        if txt.find("-") >= 0:
            splitter = "-"
        elif txt.find("..") >= 0:
            splitter = ".."
        elif txt.find(".") >= 0:
            splitter = "."
        else:
            splitter = "-"

        self._line_type = self._lt_from_splitter[splitter]

        tips = txt.split(splitter)

        self._tip1 = TipType.Empty
        if len(tips) > 0:
            self._tip1 = self._tip1_type_from_txt.get(tips[0]) or TipType.Empty

        self._tip2 = TipType.Empty
        if len(tips) > 1:
            self._tip2 = self._tip2_type_from_txt.get(tips[1]) or TipType.Empty
