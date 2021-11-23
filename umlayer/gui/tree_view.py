from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from . import StandardItemModel


class TreeView(QTreeView):
    def __init__(self, project_logic, *args, **kwargs):
        self.project_logic = project_logic
        super().__init__(*args, **kwargs)
        self.setHeaderHidden(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setSelectionMode(QAbstractItemView.SingleSelection)  # disable light blue selection
        self.setUniformRowHeights(True)
        self.setWordWrap(False)
        self.setSortingEnabled(True)
        # self.setStyleSheet("""""")

        self.itemDelegate().closeEditor.connect(self.onCloseEditor)

    @property
    def sti(self):
        return self.model()

    @property
    def project(self):
        return self.project_logic.project

    def selectRoot(self):
        self.selectionModel().clear()
        self.selectionModel().select(self.root_item.index(), QItemSelectionModel.SelectionFlag.Select)

    def getSelectedItem(self):
        indexes = self.selectedIndexes()

        if not indexes:
            return None

        index = indexes[0]

        if not index.isValid():
            return None

        item = self.sti.itemFromIndex(index)
        return item

    def updateTreeDataModel(self):
        self.root_item = StandardItemModel.itemize(self.project.root, self.project)
        self.sti.appendRow([self.root_item])
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.expandAll()

    def createProjectItem(self, project_item_creation_method):
        parent_item: QStandardItem = self.getSelectedItem()
        parent_index = parent_item.index()

        self.expand(parent_index)

        parent_id = parent_item.data(Qt.UserRole)
        project_item = project_item_creation_method(parent_id)
        item = StandardItemModel.makeItem(project_item)

        parent_item.insertRow(0, [item])

        item_index = item.index()
        self.scrollTo(item_index)
        self.setCurrentIndex(item_index)
        self.edit(item_index)

    def deleteProjectItem(self):
        item: QStandardItem = self.getSelectedItem()
        if item is None:
            return
        index = item.index()

        project_item = self.projectItemFromItem(item)
        self.project_logic.delete_element(project_item.id)  # model
        self.sti.removeRow(index.row(), index.parent())
        self.project.is_dirty = True  # model

    def projectItemFromItem(self, item):
        project_item_id = item.data(Qt.UserRole)
        return self.project.get(project_item_id)

    def onCloseEditor(self, editor: QAbstractItemDelegate, hint):
        """Set element name after editing"""
        item: QStandardItem = self.getSelectedItem()

        project_item = self.projectItemFromItem(item)
        if project_item.name != item.text:
            project_item.name = item.text()
            self.project.is_dirty = True

        parent_item = item.parent()
        parent_item.sortChildren(0, Qt.SortOrder.AscendingOrder)

        self.scrollTo(item.index())
