import logging

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from .. import model
from . import *


class SceneLogic:
    def __init__(self):
        """Do not use window here"""
        self.temp_list = []

    def setWindow(self, window):
        self.window = window

    def addElement(self, element: BaseElement) -> None:
        self.window.scene.addItem(element)
        element.setNotify(self.window.setDirty)
        self.window.setDirty()

    def addActorElement(self):
        item = ActorElement()
        item.setText('Actor')
        item.setPos(50, 50)
        self.addElement(item)

    def addPackageElement(self):
        item = PackageElement()
        item.setText('Package 1\n--\nFunctional\nPerformant')
        item.setPos(-20, -20)
        self.addElement(item)

    def addEllipseElement(self):
        item = EllipseElement()
        item.setText('Use Case 1')
        item.setWidth(150)
        item.setHeight(50)
        item.setPos(0, 0)
        self.addElement(item)

    def addNoteElement(self):
        item = NoteElement()
        item.setText('Note..')
        item.setPos(0, 0)
        self.addElement(item)

    def addTextElement(self):
        item = TextElement()
        item.setText('Left-aligned\ntext')
        item.setPos(0, 0)
        self.addElement(item)

    def addCenteredTextElement(self):
        item = TextElement()
        item.setText('Centered\ntext')
        item.setCenter(True)
        item.setPos(0, 0)
        self.addElement(item)

    def addSimpleClassElement(self):
        item = ClassElement()
        item.setText('SimpleClass')
        item.setPos(0, 0)
        self.addElement(item)

    def addFatClassElement(self):
        text = '''FatClass
        --
        -task_name
        --
        +set_task_name(name: string)\n+run_asynchronously(monitor: Monitor)'''

        item = ClassElement()
        item.setText(text)
        item.setPos(0, 0)
        self.addElement(item)

    def addLineElement(self):
        item = LineElement()
        item.setPoint1(0, 0)
        item.setPoint2(100, 100)
        item.setPos(0, 0)
        self.addElement(item)

    def addHandleItem(self):
        item = HandleItem(10)
        item.setLive(True)
        item.setPos(50, 50)
        self.window.scene.addItem(item)

    def storeScene(self):
        item: QStandardItem = self.window.treeView.getSelectedItem()
        if item is None:
            return
        id = item.data(Qt.UserRole)
        project_item = self.window.project.get(id)
        if isinstance(project_item, model.Diagram):
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
            element.setNotify(self.window.setDirty)
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
        self.window.scene.deselectAll()
        elements = [BaseElement.fromJson(json_dto) for json_dto in self.temp_list]
        for element in elements:
            # TODO: reposition elements here
            # element.setPos(QPointF(x, y))
            element.setNotify(self.window.setDirty)
            self.window.scene.addItem(element)
            element.setSelected(True)

    def disableScene(self):
        self.window.app_actions.enableElementActions(False)
        self.window.scene.set_grid_visible(False)
        self.window.centralWidget.setEnabled(False)

    def enableScene(self):
        self.window.centralWidget.setEnabled(True)
        self.window.scene.set_grid_visible(True)
        self.window.app_actions.enableElementActions(True)

    def on_select_project_item(self, project_item):
        logging.info(f'Project item selected: {project_item.name()}')
        if isinstance(project_item, model.Diagram):
            self.enableScene()
            self.buildSceneFrom(project_item)
            # TODO: focus scene view?
            # w: QWidget = self.window.centralWidget
            # s: QGraphicsScene = self.scene
            # s.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        elif isinstance(project_item, model.Folder):
            self.disableScene()
        else:
            raise NotImplementedError

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

    def _serialize_elements_to_temp_storage(self, elements):
        self.temp_list.clear()
        for item in elements:
            json_dto = item.toJson()
            self.temp_list.append(json_dto)
