import logging

from PySide6.QtCore import Qt, QItemSelectionModel

from PySide6.QtGui import QStandardItem, QFocusEvent

from PySide6.QtWidgets import (
    QTreeView,
    QAbstractItemView,
    QFrame,
    QAbstractItemDelegate,
    QItemDelegate,
)

from . import ItemRoles


class TreeView(QTreeView):
    """
    Project tree widget.

    All methods must be called with proxy index (not model index)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        # also disable light blue selection
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        self.setSortingEnabled(True)
        self.setHeaderHidden(True)
        self.setUniformRowHeights(True)
        self.setWordWrap(False)
        # self.setStyleSheet("""""")

        # used to provide custom display features and editor widgets
        delegate: QItemDelegate = self.itemDelegate()
        delegate.closeEditor.connect(self.onCloseEditor)
        self.onFocused(True)  # Because TreeView has focus

    @property
    def proxyModel(self):
        return self.model()

    @property
    def itemModel(self):
        return self.proxyModel.sourceModel()

    @property
    def window(self):
        return self.parent().parent()

    def getProxyIndex(self, model_index):
        return self.proxyModel.mapFromSource(model_index)

    def getModelIndex(self, proxy_index):
        return self.proxyModel.mapToSource(proxy_index)

    def isSelected(self):
        indexes = self.selectedIndexes()
        if not indexes:
            return False
        proxy_index = indexes[0]
        return proxy_index.isValid()

    def getSelectedItem(self):
        """Returns first (and only) selected item or None"""
        indexes = self.selectedIndexes()
        if not indexes:
            return None

        proxy_index = indexes[0]
        if not proxy_index.isValid():
            return None

        model_index = self.getModelIndex(proxy_index)
        item = self.itemModel.itemFromIndex(model_index)
        return item

    def getSelectedItemId(self):
        item = self.getSelectedItem()
        if item is None:
            return None
        return self.itemModel.getId(item)

    def initializeFromProject(self, project):
        self.itemModel.initializeFromProject(project)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.expandAll()
        root_item = self.itemModel.root_item()
        model_index = root_item.index()
        proxy_index = self.getProxyIndex(model_index)
        self.selectionModel().select(
            proxy_index, QItemSelectionModel.SelectionFlag.Select
        )

    def startEditName(self, item):
        model_index = item.index()
        proxy_index = self.getProxyIndex(model_index)
        self.scrollTo(proxy_index)
        self.setCurrentIndex(proxy_index)
        self.edit(proxy_index)

    def onCloseEditor(self, editor: QAbstractItemDelegate, hint):
        """Set element name after editing"""
        logging.info("Finish name editing")
        item: QStandardItem = self.getSelectedItem()
        if item is None:
            return
        id = self.itemModel.getId(item)

        name = item.text()
        self.window.setProjectItemName(id, name)

        parent_item = item.parent()
        parent_item.sortChildren(0, Qt.SortOrder.AscendingOrder)
        model_index = item.index()
        proxy_index = self.getProxyIndex(model_index)
        self.scrollTo(proxy_index)

    def focusInEvent(self, event: QFocusEvent) -> None:
        self.onFocused(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        self.onFocused(False)
        super().focusOutEvent(event)

    def onFocused(self, is_focused: bool) -> None:
        self.setFrameStyle(
            QFrame.Panel | (QFrame.Plain if is_focused else QFrame.Sunken)
        )

    def deleteItem(self, item):
        model_index = item.index()
        row = model_index.row()
        parent_index = model_index.parent()
        self.itemModel.removeRow(row, parent_index)
