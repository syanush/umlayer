from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


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
    def window(self):
        return self.parent().parent()

    def getSelectedItem(self):
        indexes = self.selectedIndexes()

        if not indexes:
            return None

        index = indexes[0]

        if not index.isValid():
            return None

        item = self.sti.itemFromIndex(index)
        return item

    def setInitialState(self):
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.expandAll()
        root_item = self.sti.root_item()
        self.selectionModel().select(root_item.index(), QItemSelectionModel.SelectionFlag.Select)

    def startEditName(self, item):
        item_index = item.index()
        self.scrollTo(item_index)
        self.setCurrentIndex(item_index)
        self.edit(item_index)

    def onCloseEditor(self, editor: QAbstractItemDelegate, hint):
        """Set element name after editing"""
        self.window.logic.finishNameEditing()
