import logging

from PySide6.QtCore import QPointF

from . import (
    gui_utils,
    BaseElement,
    LineElement,
    ActorElement,
    PackageElement,
    EllipseElement,
    NoteElement,
    TextElement,
    ClassElement,
)

from umlayer import model


class SceneLogic:
    def __init__(self):
        """Do not use window here"""
        self.temp_list = []
        self._grid_enabled = False
        self.window = None

    def setWindow(self, window):
        self.window = window

    def setDirty(self):
        self.window.setDirty(True)

    def selectElement(self, element):
        if isinstance(element, LineElement):
            element.selectAll()
        else:
            element.setSelected(True)

    def addElement(self, element: BaseElement) -> None:
        self.window.scene.deselectAll()
        self.window.scene.addItem(element)
        element.setPos(self.initialPosition())
        self.selectElement(element)
        self.setDirty()

    def initialPosition(self) -> QPointF:
        """Return scene coordinates of the initial position of new elements"""
        pos = self.window.sceneView.mapToScene(20, 20)
        grid_pos = QPointF(gui_utils.snap_up(pos.x()), gui_utils.snap_up(pos.y()))
        return grid_pos

    def addActorElement(self):
        element = ActorElement()
        element.setText("Actor")
        self.addElement(element)

    def addPackageElement(self):
        element = PackageElement()
        element.setText("GUI\n--\n+ Window\n+ Form\n# EventHandler")
        self.addElement(element)

    def addEllipseElement(self):
        element = EllipseElement()
        element.setText("Use case 1")
        self.addElement(element)

    def addNoteElement(self):
        element = NoteElement()
        element.setText("Note..")
        self.addElement(element)

    def addTextElement(self):
        element = TextElement()
        element.setText("Left-aligned\ntext")
        self.addElement(element)

    def addCenteredTextElement(self):
        element = TextElement()
        element.setText("Centered\ntext")
        element.setCenter(True)
        self.addElement(element)

    def addSimpleClassElement(self):
        element = ClassElement()
        element.setText("<b>SimpleClass</b>")
        self.addElement(element)

    def addFatClassElement(self):
        text = """<b>FatClass</b>
--
- task_name
--
+ set_task_name(name: string)\n+ run_asynchronously(monitor: Monitor)"""

        element = ClassElement()
        element.setText(text)
        self.addElement(element)

    def addLine(self, line_text):
        element = LineElement(0, 0, 100, 0, line_text)
        self.addElement(element)

    def storeScene(self):
        if not self.window.isDiagramSelected():
            return
        diagram: model.Diagram = self.window.getSelectedProjectItem()
        self.storeSceneTo(diagram)

    def storeSceneTo(self, diagram: model.Diagram):
        logging.info(f"Store scene to {diagram.name()}")
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
        elements: list[BaseElement] = [
            BaseElement.fromJson(json_dto) for json_dto in self.temp_list
        ]
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
            new_pos = ipos + element.pos()
            # print(element, new_pos)
            element.setPos(new_pos)
            self.window.scene.addItem(element)
            self.selectElement(element)

    def disableScene(self):
        self.window.app_actions.enableSceneActions(False)
        self.refreshGrid()
        self.window.centralWidget.setEnabled(False)

    def enableScene(self):
        self.window.centralWidget.setEnabled(True)
        self.refreshGrid()
        self.window.app_actions.enableSceneActions(True)

    def isEnabled(self):
        return self.window.centralWidget.isEnabled()

    def on_select_project_item(self, project_item):
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

    def on_deselect_project_item(self, project_item: model.BaseItem) -> None:
        if project_item.item_type == model.ProjectItemType.DIAGRAM:
            self.storeSceneTo(project_item)
            logging.debug(f"The scene was stored to diagram {project_item.name()}")
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
            self._grid_enabled and self.window.isDiagramSelected()
        )

    def selectAllElements(self):
        logging.info("Action: Select all elements")

        if not self.isEnabled():
            return

        for element in self.window.scene.elements():
            self.selectElement(element)

    def bring_to_front(self):
        if not self.window.scene.selectedElements():
            return

        selected_element = self.window.scene.selectedElements()[0]
        overlap_elements = self.window.scene.collidingElements(selected_element)

        z_value = 0
        for element in overlap_elements:
            if element.zValue() >= z_value:
                z_value = element.zValue() + 0.1
        selected_element.setZValue(z_value)
        # print(z_value)
        selected_element.update()

    def send_to_back(self):
        if not self.window.scene.selectedElements():
            return

        selected_element = self.window.scene.selectedElements()[0]
        overlap_elements = self.window.scene.collidingElements(selected_element)

        z_value = 0
        for element in overlap_elements:
            if element.zValue() <= z_value:
                z_value = element.zValue() - 0.1
        selected_element.setZValue(z_value)
        selected_element.update()
