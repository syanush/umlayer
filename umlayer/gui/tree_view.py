import logging
from uuid import UUID

from PySide6.QtCore import Qt, QItemSelectionModel, QModelIndex

from PySide6.QtGui import QFocusEvent

from PySide6.QtWidgets import (
    QTreeView,
    QAbstractItemView,
    QFrame,
    QAbstractItemDelegate,
)

from umlayer import adapters


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
        delegate: QAbstractItemDelegate = self.itemDelegate()
        delegate.closeEditor.connect(self.onCloseEditor)
        self.onFocused(True)  # Because TreeView has focus

    @property
    def proxyModel(self) -> adapters.TreeSortModel:
        return self.model()

    @property
    def itemModel(self) -> adapters.StandardItemModel:
        return self.proxyModel.sourceModel()

    @property
    def window(self):
        return self.parent().parent()

    def getProxyIndex(self, model_index: QModelIndex) -> QModelIndex:
        return self.proxyModel.mapFromSource(model_index)

    def getModelIndex(self, proxy_index: QModelIndex) -> QModelIndex:
        return self.proxyModel.mapToSource(proxy_index)

    def itemsFromProxyIndexes(self, proxy_indexes) -> list[adapters.StandardItem]:
        return [
            self.itemModel.itemFromIndex(self.getModelIndex(proxy_index))
            for proxy_index in proxy_indexes
            if proxy_index.isValid()
        ]

    def getSelectedItems(self) -> list[adapters.StandardItem]:
        return self.itemsFromProxyIndexes(self.selectedIndexes())

    def isSelected(self) -> bool:
        return bool(self.getSelectedItems())

    def getSelectedItem(self) -> adapters.StandardItem:
        """Returns selected item or throws Exception"""
        return self.getSelectedItems()[0]

    def getSelectedItemId(self) -> UUID:
        """Returns selected item id or throws Exception"""
        return self.getSelectedItem().itemId()

    def initializeTree(self) -> None:
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.expandAll()
        root_item = self.itemModel.rootItem()
        model_index: QModelIndex = root_item.index()
        proxy_index: QModelIndex = self.getProxyIndex(model_index)
        self.selectionModel().select(
            proxy_index, QItemSelectionModel.SelectionFlag.Select
        )

    def startEditName(self, item: adapters.StandardItem) -> None:
        model_index: QModelIndex = item.index()
        proxy_index: QModelIndex = self.getProxyIndex(model_index)
        self.scrollTo(proxy_index)
        self.setCurrentIndex(proxy_index)
        self.edit(proxy_index)

    def onCloseEditor(self, editor: QAbstractItemDelegate, hint) -> None:
        """Set element name after editing"""
        logging.debug("Finish name editing")
        if not self.isSelected():
            return
        item: adapters.StandardItem = self.getSelectedItem()
        item_id: UUID = item.itemId()

        name: str = item.text()
        self.window.setProjectItemName(item_id, name)

        parent_item: adapters.StandardItem = item.parent()
        parent_item.sortChildren(0, Qt.SortOrder.AscendingOrder)
        model_index: QModelIndex = item.index()
        proxy_index: QModelIndex = self.getProxyIndex(model_index)
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

    def deleteItem(self, item: adapters.StandardItem) -> None:
        model_index: QModelIndex = item.index()
        row: int = model_index.row()
        parent_index: QModelIndex = model_index.parent()
        self.itemModel.removeRow(row, parent_index)
