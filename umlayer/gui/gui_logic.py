import logging

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from .. import model
from . import *


class GuiLogic:
    def __init__(self):
        """Do not use window here"""

    def setWindow(self, window):
        self.window = window

    def newProject(self):
        logging.info('Action: New project')
        if not self.closeProject():
            return
        self.window.project_logic.new_project()
        self.updateTreeDataModel(self.window.project)
        self.window.filename = model.constants.DEFAULT_FILENAME
        self.window.updateTitle()

    def updateTreeDataModel(self, project):
        logging.info('Update Tree Data Model')
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

    def saveProject(self):
        logging.info('Action: Save')
        if self._isFileNameNotSet():
            filename = self._getFileNameFromSaveDialog('Save')
        else:
            filename = self.window.filename

        if len(filename) == 0:
            return

        try:
            self._doSaveProject(filename)
        except Exception:
            pass
        else:
            self.window.filename = filename
            self.window.updateTitle()

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

    def closeProject(self) -> bool:
        logging.info('Action: Close')
        if not self.saveFileIfNeeded():
            return False

        if not self._closeDiagramWindows():
            return False

        self.window.sti.clear()
        self.window.project_logic.clear_project()
        self.window.filename = None
        self.window.updateTitle()
        return True

    def saveFileIfNeeded(self) -> bool:
        logging.info('Try to save file if needed')
        if not self.window.project.dirty():
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
        logging.info('Action: Exit app')
        self.window.close()

    def aboutWindow(self):
        logging.info('Action: About window')
        QMessageBox.about(self.window, "About ...", "About window")

    def createDiagram(self):
        logging.info('Action: Create Diagram')
        self._createProjectItem(self.window.project_logic.create_diagram)

    def createFolder(self):
        logging.info('Action: Create Folder')
        self._createProjectItem(self.window.project_logic.create_folder)

    def deleteSelectedItem(self):
        logging.info('Action: Delete selected project item')
        item: QStandardItem = self.window.treeView.getSelectedItem()
        if item is None:
            return
        id = item.data(Qt.UserRole)
        self.window.project_logic.delete_project_item(id)
        index = item.index()
        self.window.sti.removeRow(index.row(), index.parent())
        self.window.updateTitle()

    def finishNameEditing(self):
        logging.info('Finish name editing')
        item: QStandardItem = self.window.treeView.getSelectedItem()
        if item is None:
            return
        id = item.data(Qt.UserRole)
        project_item = self.window.project.get(id)
        if project_item.name != item.text():
            project_item.name = item.text()
            self.window.project.is_dirty = True
        parent_item = item.parent()
        parent_item.sortChildren(0, Qt.SortOrder.AscendingOrder)
        self.window.treeView.scrollTo(item.index())

    def on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        logging.info('Project selection changed')
        selected_project_items = self._projectItemsFromSelection(selected)
        deselected_project_items = self._projectItemsFromSelection(deselected)
        self.window.scene_logic.on_project_item_selection_changed(
            selected_project_items, deselected_project_items)

    def _projectItemsFromSelection(self, selection):
        result = []
        for index in selection.indexes():
            item = self.window.sti.itemFromIndex(index)
            if item is None:
                continue
            id = item.data(Qt.UserRole)
            project_item = self.window.project.get(id)
            result.append(project_item)
        return tuple(result)

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
        self.window.project_logic.load(filename)
        self.updateTreeDataModel(self.window.project_logic.project)

    def _doSaveProject(self, filename):
        """Really save project"""
        self.window.scene_logic.storeScene()
        self.window.project_logic.save(filename)

    def _isFileNameNotSet(self) -> bool:
        return self.window.filename is None or self.window.filename == model.constants.DEFAULT_FILENAME

    def _printStats(self):
        print('number of elements', self.window.project.count())
        print('number of items', self.window.sti.count())

    def _closeDiagramWindows(self) -> bool:
        """Returns true if windows are closed successfully"""
        return True
