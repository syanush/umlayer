from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QImage, QPainter, QBrush
from PySide6.QtSvg import QSvgGenerator
from PySide6.QtWidgets import QGraphicsScene

from . import GraphicsScene


class ExportScene(QGraphicsScene):
    def __init__(self, scene: GraphicsScene):
        super().__init__(sceneRect=scene.sceneRect(), parent=scene.parent())
        self._scene = scene
        self.setBackgroundBrush(QBrush(Qt.transparent))
        self.setItemIndexMethod(QGraphicsScene.BspTreeIndex)
        for element in self._scene.elements():
            self.addItem(element.clone())
        self.new_scene_rect = self.itemsBoundingRect()
        self.setSceneRect(self.new_scene_rect)
        self.scene_size = self.new_scene_rect.size().toSize()
        self.clearSelection()

    def exportAsSvgImage(self, filename) -> None:
        generator = QSvgGenerator()
        generator.setFileName(filename)
        generator.setSize(self.scene_size)
        generator.setViewBox(
            QRect(0, 0, self.scene_size.width(), self.scene_size.height())
        )
        generator.setTitle(filename)
        painter = QPainter()
        painter.begin(generator)
        self.render(painter)
        painter.end()

    def exportAsRasterImage(self, filename: str) -> None:
        image = QImage(self.scene_size, QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        painter = QPainter()
        painter.begin(image)
        self.render(painter)
        painter.end()
        image.save(filename)
