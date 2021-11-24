import logging

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from .. import model
from . import *


class GuiLogic:
    def __init__(self):
        self.temp_list = []

    def _notify(self):
        if not self.project.dirty():
            self.project.setDirty(True)
            self.window.updateTitle()

    def setWindow(self, window):
        self.window = window

    @property
    def project_logic(self):
        return self.window.project_logic

    @property
    def project(self):
        return self.window.project

    @property
    def scene(self):
        return self.window.scene

    def newProject(self):
        logging.info('Action: New')
        if not self.closeProject():
            return
        self.project_logic.new_project()
        self.updateTreeDataModel(self.project)
        self.window.filename = model.constants.DEFAULT_FILENAME
        self.window.updateTitle()

    def updateTreeDataModel(self, project):
        self.window.sti.updateItemModel(project)
        self.window.treeView.setInitialState()

    def openProject(self):
        logging.info('Action: Open')
        if not self.closeProject():
            return

        filename = self._getFileNameFromOpenDialog('Open')

        if len(filename) == 0:
            return

        try:
            self._doOpenProject(filename)
        except Exception as ex:
            print(ex)
        else:
            self.window.filename = filename
            self.window.updateTitle()

        self._printStats()

    def _getFileNameFromOpenDialog(self, caption=None):
        filename, selected_filter = \
            QFileDialog.getOpenFileName(
                parent=self.window,
                caption=caption,
                dir=QDir.currentPath(),
                filter="All (*);;Umlayer project (*.ulr)",
                selectedFilter="Umlayer project (*.ulr)")
        return filename

    def _getFileNameFromSaveDialog(self, caption=None):
        initial_filename = self.window.filename or model.constants.DEFAULT_FILENAME
        filename, selected_filter = \
            QFileDialog.getSaveFileName(
                parent=self.window,
                caption=caption,
                dir=QDir.currentPath() + '/' + initial_filename,
                filter="All (*);;Umlayer project (*.ulr)",
                selectedFilter="Umlayer project (*.ulr)")
        return filename

    def _doOpenProject(self, filename):
        self.project_logic.load(filename)
        self.updateTreeDataModel(self.project_logic.project)

    def saveProject(self):
        filename = self._getFileNameFromSaveDialog('Save') \
            if self._isFileNameNotSet() else self.window.filename

        if len(filename) == 0:
            return

        try:
            self._doSaveProject(filename)
        except Exception:
            pass
        else:
            self.window.filename = filename
            self.window.updateTitle()

    def _isFileNameNotSet(self) -> bool:
        return self.window.filename is None or self.window.filename == model.constants.DEFAULT_FILENAME

    def saveProjectAs(self):
        logging.info('Action: Save As')

        filename = self._getFileNameFromSaveDialog('Save as...')

        if len(filename) == 0:
            return

        try:
            self._doSaveProject(filename)
        except Exception as ex:
            pass
        else:
            self.window.filename = filename
            self.window.updateTitle()

    def _doSaveProject(self, filename):
        """Really save project"""
        self.project_logic.save(filename)

    def closeProject(self) -> bool:
        logging.info('Action: Close')
        if not self.saveFileIfNeeded():
            return False

        if not self._closeDiagramWindows():
            return False

        self._clearTreeDataModel()
        self.project_logic.clear_project()
        self.window.filename = None
        self.window.updateTitle()
        return True

    def _clearTreeDataModel(self):
        self.window.sti.clear()

    def _closeDiagramWindows(self) -> bool:
        """Returns true if windows are closed successfully"""
        return True

    def saveFileIfNeeded(self) -> bool:
        if not self.project.dirty():
            return True

        reply = QMessageBox.question(
            self.window,
            'Warning \u2014 Umlayer',
            'The current file has been modified.\nDo you want to save it?',
            QMessageBox.Cancel | QMessageBox.Discard | QMessageBox.Save,
            QMessageBox.Save)

        if reply == QMessageBox.Save:
            self.saveProject()

        return reply != QMessageBox.Cancel

    def exitApp(self):
        self.window.close()

    def delete(self):
        raise NotImplementedError

    def cut(self):
        raise NotImplementedError

    def copy(self):
        raise NotImplementedError

    def paste(self):
        raise NotImplementedError

    def aboutHelp(self):
        QMessageBox.about(self.window, "About ...", "About window")

    def createDiagram(self):
        self._createProjectItem(self.project_logic.create_diagram)

    def createFolder(self):
        self._createProjectItem(self.project_logic.create_folder)

    def _createProjectItem(self, project_item_creation_method):
        parent_item: QStandardItem = self.window.treeView.getSelectedItem()
        parent_index = parent_item.index()

        self.window.treeView.expand(parent_index)

        parent_id = parent_item.data(Qt.UserRole)
        project_item = project_item_creation_method(parent_id)
        item = StandardItemModel.makeItem(project_item)

        parent_item.insertRow(0, [item])
        self.window.treeView.startEditName(item)
        self.window.updateTitle()

    def deleteSelectedItem(self):
        item: QStandardItem = self.window.treeView.getSelectedItem()
        if item is None:
            return
        id = item.data(Qt.UserRole)
        self.project_logic.delete_element(id)
        index = item.index()
        self.window.sti.removeRow(index.row(), index.parent())
        self.window.updateTitle()

    def finishNameEditing(self):
        item: QStandardItem = self.window.treeView.getSelectedItem()
        id = item.data(Qt.UserRole)
        project_item = self.project.get(id)
        if project_item.name != item.text():
            project_item.name = item.text()
            self.project.is_dirty = True
        parent_item = item.parent()
        parent_item.sortChildren(0, Qt.SortOrder.AscendingOrder)
        self.window.treeView.scrollTo(item.index())

    def _projectItemsFromSelection(self, selection):
        result = []
        for index in selection.indexes():
            item = self.window.sti.itemFromIndex(index)
            if item is None:
                continue
            id = item.data(Qt.UserRole)
            project_item = self.project.get(id)
            result.append(project_item)
        return tuple(result)

    def addActorElement(self):
        self.window.scene.addActorElement(50, 50, self._notify)

    def addPackageElement(self):
        self.window.scene.addPackageElement(-20, -20, self._notify)

    def addEllipseElement(self):
        self.window.scene.addEllipseElement(0, 0, self._notify)

    def addNoteElement(self):
        self.window.scene.addNoteElement(0, 0, self._notify)

    def addTextElement(self):
        self.window.scene.addTextElement(0, 0, self._notify)

    def addCenteredTextElement(self):
        self.window.scene.addCenteredTextElement(0, 0, self._notify)

    def addSimpleClassElement(self):
        self.window.scene.addSimpleClassElement(0, 0, self._notify)

    def addFatClassElement(self):
        self.window.scene.addFatClassElement(0, 0, self._notify)

    def addHandleItem(self):
        self.window.scene.addHandleItem(50, 50)

    def addLineElement(self):
        self.window.scene.addLineElement(0, 0, self._notify)

    def _printStats(self):
        print('number of elements', self.project.count())
        print('number of items', self.window.sti.count())

    def printProjectItems(self):
        self.project.printProjectItems()

    def printSceneElements(self):
        self.window.scene.printItems()

    def on_project_item_selection_changed(self, selected_items, deselected_items):
        if deselected_items:
            self.on_deselect_project_item(deselected_items[0])
        if selected_items:
            self.on_select_project_item(selected_items[0])

    def on_deselect_project_item(self, project_item):
        if isinstance(project_item, model.Diagram):
            self.storeSceneTo(project_item)
            self.window.scene.clearElements()

    def on_select_project_item(self, project_item):
        if isinstance(project_item, model.Diagram):
            self.enableScene()
            self.buildSceneFrom(project_item)
            # w: QWidget = self.window.centralWidget
            #
            # w.focusNextChild()
            s: QGraphicsScene = self.scene
            s.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        elif isinstance(project_item, model.Folder):
            self.disableScene()
        else:
            raise NotImplementedError

    def disableScene(self):
        self.window.app_actions.enableElementActions(False)
        self.scene.set_grid_visible(False)
        self.window.centralWidget.setEnabled(False)

    def enableScene(self):
        self.window.centralWidget.setEnabled(True)
        self.scene.set_grid_visible(True)
        self.window.app_actions.enableElementActions(True)

    def storeSceneTo(self, project_item):
        project_item.dtos.clear()
        for item in self.window.scene.elements():
            json_dto = item.toJson()
            project_item.dtos.append(json_dto)
        hv, hmin, hmax, vv, vmin, vmax = self.window.sceneView.scrollData()
        project_item.scroll_data = [hv, hmin, hmax, vv, vmin, vmax]

    def buildSceneFrom(self, project_item):
        for json_dto in project_item.dtos:
            element = BaseElement.fromJson(json_dto)
            # TODO: override addItem and move setNotify there
            element.setNotify(self._notify)
            self.scene.addItem(element)
        if project_item.scroll_data is not None:
            hv, hmin, hmax, vv, vmin, vmax = project_item.scroll_data
            self.window.sceneView.setScrollData(hv, hmin, hmax, vv, vmin, vmax)

    def on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        selected_project_items = self._projectItemsFromSelection(selected)
        deselected_project_items = self._projectItemsFromSelection(deselected)
        self.on_project_item_selection_changed(selected_project_items, deselected_project_items)

    def copy_selected_elements(self):
        elements = self.scene.selectedElements()
        self.serialize_elements_to_temp_storage(elements)

    def delete_selected_elements(self):
        elements = self.scene.selectedElements()
        self._remove_elements(elements)

    def cut_selected_elements(self):
        elements = self.scene.selectedElements()
        self.serialize_elements_to_temp_storage(elements)
        self._remove_elements(elements)

    def paste_elements(self):
        self.scene.deselectAll()
        elements = [BaseElement.fromJson(json_dto) for json_dto in self.temp_list]
        for element in elements:
            # TODO: reposition elements here
            # element.setPos(QPointF(x, y))
            element.setNotify(self._notify)
            self.scene.addItem(element)
            element.setSelected(True)

    def serialize_elements_to_temp_storage(self, elements):
        self.temp_list.clear()
        for item in elements:
            json_dto = item.toJson()
            self.temp_list.append(json_dto)

    def _remove_elements(self, elements):
        for element in elements:
            self.scene.removeItem(element)
