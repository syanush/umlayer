import logging

from PySide6.QtCore import *
from PySide6.QtWidgets import *

from .. import model
from . import *


class GuiLogic:
    def __init__(self, window):
        self.window = window
        self.project = window.project
        self.project_logic = window.project_logic

    def newProject(self):
        logging.info('Action: New')
        if not self.closeProject():
            return
        self.project_logic.new_project()
        self.window.treeView.updateTreeDataModel()
        self.window.filename = model.constants.DEFAULT_FILENAME
        self.window.updateTitle()

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
        self.window.treeView.updateTreeDataModel()

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
        if not self.project.is_dirty:
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

    def copy(self):
        raise NotImplementedError

    def paste(self):
        raise NotImplementedError

    def aboutHelp(self):
        QMessageBox.about(self.window, "About ...", "About window")

    def createDiagram(self):
        self._createElement(self.project_logic.create_diagram)

    def createFolder(self):
        self._createElement(self.project_logic.create_folder)

    def _createElement(self, create_method):
        self.window.treeView.createElement(create_method)
        self.window.updateTitle()

    def deleteElement(self):
        self.window.treeView.deleteElement()
        self.window.updateTitle()
        self._printStats()

    def addActorElement(self):
        self.window.scene.addActorElement(50, 50)

    def addPackageElement(self):
        self.window.scene.addPackageElement(-20, -20)

    def addEllipseElement(self):
        self.window.scene.addEllipseElement(0, 0)

    def addNoteElement(self):
        self.window.scene.addNoteElement(0, 0)

    def addTextElement(self):
        self.window.scene.addTextElement(0, 0)

    def addCenteredTextElement(self):
        self.window.scene.addCenteredTextElement(0, 0)

    def addSimpleClassElement(self):
        self.window.scene.addSimpleClassElement(0, 0)

    def addFatClassElement(self):
        self.window.scene.addFatClassElement(0, 0)

    def addHandleElement(self):
        self.window.scene.addHandleElement(-50, -50)

    def addLineElement(self):
        self.window.scene.addLineElement(-100, -100)

    def _printStats(self):
        print('number of elements', self.project.count())
        print('number of items', self.window.sti.count())

    def printElements(self):
        self.project.printElements()

    def on_element_selection_changed(self, selected_elements, deselected_elements):
        if deselected_elements:
            self.on_deselect_element(deselected_elements[0])
        if selected_elements:
            self.on_select_element(selected_elements[0])

    def on_deselect_element(self, element):
        if isinstance(element, model.Diagram):
            self.storeSceneTo(element)
            self.window.scene.clear()

    def on_select_element(self, element):
        self.buildSceneFrom(element)

    def storeSceneTo(self, element):
        element.dtos.clear()
        for item in self.window.scene.items():
            if isinstance(item, ActorElement):
                dto = item.getDataAsDto()
                element.dtos.append(dto)

    def buildSceneFrom(self, element):
        if not isinstance(element, model.Diagram):
            return
        for dto in element.dtos:
            element = self.userElementFromDto(dto)
            # TODO: see addUserElement
            self.window.scene.addItem(element)
            print(element)

    def userElementFromDto(self, dto):
        element = ActorElement()
        element.setDataFromDto(dto)
        element.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        return element

    def elementsFromSelection(self, selection):
        result = []
        for index in selection.indexes():
            item = self.window.sti.itemFromIndex(index)
            if item is None:
                continue
            element = self.window.treeView.elementFromItem(item)
            result.append(element)
        return tuple(result)

    def on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        item = self.window.treeView.getSelectedItem()
        if item is None:
            return
        self.on_element_selection_changed(
            self.elementsFromSelection(selected),
            self.elementsFromSelection(deselected),
        )
