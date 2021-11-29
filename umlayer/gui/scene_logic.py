import logging

from PySide6.QtCore import *
from PySide6.QtGui import *

from umlayer import model
from . import *


class SceneLogic:
    def __init__(self):
        """Do not use window here"""
        self.temp_list = []
        self._grid_enabled = False
        self.window: MainWindow = None

    def setWindow(self, window):
        self.window = window

    def setDirty(self):
        self.window.project.setDirty(True)

    def addElement(self, element: BaseElement) -> None:
        element.setPos(self.initialPosition())
        self.window.scene.addItem(element)
        self.setDirty()

    def initialPosition(self) -> QRectF:
        """Return scene coordinates of the initial position of new elements"""
        return self.window.sceneView.mapToScene(20, 20)

    def addActorElement(self):
        item = ActorElement()
        item.setText('Actor')
        self.addElement(item)

    def addPackageElement(self):
        item = PackageElement()
        item.setText('Package 1\n--\nFunctional\nPerformant')
        self.addElement(item)

    def addEllipseElement(self):
        item = EllipseElement()
        item.setText('Use Case 1')
        item.setWidth(150)
        item.setHeight(50)
        self.addElement(item)

    def addNoteElement(self):
        item = NoteElement()
        item.setText('Note..')
        self.addElement(item)

    def addTextElement(self):
        item = TextElement()
        item.setText('Left-aligned\ntext')
        self.addElement(item)

    def addCenteredTextElement(self):
        item = TextElement()
        item.setText('Centered\ntext')
        item.setCenter(True)
        self.addElement(item)

    def addSimpleClassElement(self):
        item = ClassElement()
        item.setText('SimpleClass')
        self.addElement(item)

    def addFatClassElement(self):
        text = '''FatClass
--
-task_name
--
+set_task_name(name: string)\n+run_asynchronously(monitor: Monitor)'''

        item = ClassElement()
        item.setText(text)
        self.addElement(item)

    def addLineElement(self):
        item = LineElement()
        item.setPoint1(0, 0)
        item.setPoint2(100, 100)
        self.addElement(item)

    def storeScene(self):
        if self.window.isDiagramSelected():
            self.storeSceneTo(project_item)

    def storeSceneTo(self, diagram: model.Diagram):
        logging.info(f'Store scene to {diagram.name()}')
        diagram.dtos.clear()
        for item in self.window.scene.elements():
            json_dto = item.toJson()
            diagram.dtos.append(json_dto)
        hv, hmin, hmax, vv, vmin, vmax = self.window.sceneView.scrollData()
        diagram.scroll_data = [hv, hmin, hmax, vv, vmin, vmax]

    def buildSceneFrom(self, project_item):
        for json_dto in project_item.dtos:
            element = BaseElement.fromJson(json_dto)
            # TODO: override addItem and move setNotify there
            self.window.scene.addItem(element)
        if project_item.scroll_data is not None:
            hv, hmin, hmax, vv, vmin, vmax = project_item.scroll_data
            self.window.sceneView.setScrollData(hv, hmin, hmax, vv, vmin, vmax)

    def delete_selected_elements(self):
        elements = self.window.scene.selectedElements()
        self._remove_elements(elements)

    def copy_selected_elements(self):
        elements = self.window.scene.selectedElements()
        self._serialize_elements_to_temp_storage(elements)

    def cut_selected_elements(self):
        elements = self.window.scene.selectedElements()
        self._serialize_elements_to_temp_storage(elements)
        self._remove_elements(elements)

    def paste_elements(self):
        """Pasted elements are appeared at the top left corner"""
        elements: list[Element] = [BaseElement.fromJson(json_dto) for json_dto in self.temp_list]
        if not elements:
            return

        self.setDirty()
        self.window.scene.deselectAll()

        topleft: QPointF = elements[0].pos()
        for element in elements[1:]:
            ep = element.pos()
            if topleft.x() > ep.x():
                topleft.setX(ep.x())
            if topleft.y() > ep.y():
                topleft.setY(ep.y())

        ipos: QPointF = self.initialPosition() - topleft

        for element in elements:
            element.setPos(ipos + element.pos())
            self.window.scene.addItem(element)
            element.setSelected(True)

    def disableScene(self):
        self.window.app_actions.enableSceneActions(False)
        self.refreshGrid()
        self.window.centralWidget.setEnabled(False)

    def enableScene(self):
        self.window.centralWidget.setEnabled(True)
        self.refreshGrid()
        self.window.app_actions.enableSceneActions(True)

    def on_select_project_item(self, project_item):
        logging.info(f'Project item selected: {project_item.name()}')
        if isinstance(project_item, model.Diagram):
            self.enableScene()
            self.buildSceneFrom(project_item)
        else:
            self.disableScene()

    def on_project_item_selection_changed(self, selected_items, deselected_items):
        if deselected_items:
            self.on_deselect_project_item(deselected_items[0])
        if selected_items:
            self.on_select_project_item(selected_items[0])

    def on_deselect_project_item(self, project_item):
        if isinstance(project_item, model.Diagram):
            self.storeSceneTo(project_item)
            self.window.scene.clearElements()

    def _remove_elements(self, elements):
        for element in elements:
            self.window.scene.removeItem(element)
            self.setDirty()

    def _serialize_elements_to_temp_storage(self, elements):
        self.temp_list.clear()
        for item in elements:
            json_dto = item.toJson()
            self.temp_list.append(json_dto)

    def toggleGrid(self, check: bool = False) -> None:
        self._grid_enabled = check
        self.refreshGrid()

    def refreshGrid(self):
        self.window.scene.set_grid_visible(
            self._grid_enabled and self.window.isDiagramSelected())
