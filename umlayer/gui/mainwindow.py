import logging
import traceback
from uuid import UUID

from PySide6.QtCore import Qt, QSettings, QDir, QItemSelection, QByteArray

from PySide6.QtGui import (
    QPainter,
    QTextOption,
    QKeySequence,
    QShortcut,
)

from PySide6.QtWidgets import (
    QMainWindow,
    QMenu,
    QToolBar,
    QStatusBar,
    QMessageBox,
    QFileDialog,
    QComboBox,
    QPushButton,
    QLabel,
    QDockWidget,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from umlayer import version, model, adapters

from . import (
    GraphicsScene,
    ExportScene,
    GraphicsView,
    TreeView,
    LineIconsProxyStyle,
    Settings,
    Actions,
    BaseElement,
    Abilities,
)


class MainWindow(QMainWindow):
    """Main window of the UMLayer application"""

    def __init__(self, scene_logic, data_model, interactors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_logic = scene_logic

        self._interactors = interactors
        self._data_model = data_model

    def initialize(self):
        self.scene_logic.setWindow(self)
        self.readSettings()
        self.initGUI()
        self.createNewProject()

    @property
    def filename(self) -> str:
        return self._data_model.filename

    @property
    def project(self) -> model.Project:
        return self._data_model.project

    def setDirty(self, dirty: bool) -> None:
        self._interactors.project_interactor.set_dirty(dirty)

    def setProjectItemName(self, item_id: UUID, name: str) -> None:
        self._interactors.project_interactor.set_project_item_name(item_id, name)

    def createFolder(self) -> None:
        logging.info("Action: Create Folder")
        self.createProjectItem(model.ProjectItemType.FOLDER)

    def createDiagram(self) -> None:
        logging.info("Action: Create Diagram")
        self.createProjectItem(model.ProjectItemType.DIAGRAM)

    def createNewProject(self) -> None:
        logging.info("Action: New project")
        self._interactors.project_interactor.create_new_project()

    def openProject(self) -> None:
        logging.info("Action: Open")
        self._interactors.project_interactor.open_project()

    def saveProject(self) -> None:
        logging.info("Action: Save")
        self._interactors.project_interactor.save_project()

    def saveProjectAs(self) -> None:
        logging.info("Action: Save As")
        self._interactors.project_interactor.save_project_as()

    def closeProject(self) -> bool:
        """Returns True if project was closed successfully, False otherwise"""
        logging.info("Action: Close")
        return self._interactors.project_interactor.close_project()

    def askToSaveModifiedProject(self) -> None:
        reply = QMessageBox.question(
            self,
            "Warning \u2014 Umlayer",
            "The current file has been modified.\nDo you want to save it?",
            QMessageBox.Cancel | QMessageBox.Discard | QMessageBox.Save,
            QMessageBox.Save,
        )
        if reply == QMessageBox.Cancel:
            return model.constants.CANCEL
        if reply == QMessageBox.Discard:
            return model.constants.DISCARD
        return model.constants.SAVE

    def showCriticalError(self, message: str) -> None:
        QMessageBox.critical(self, "Error!", message, QMessageBox.Abort)

    def isDirty(self) -> bool:
        return self._interactors.project_interactor.is_dirty()

    def updateTitle(self) -> None:
        title = model.utils.build_window_title(self.filename, self.isDirty())
        self.setWindowTitle(title)
        self.updateToolbar()

    def updateToolbar(self) -> None:
        is_dirty = self.isDirty()
        self.app_actions.saveAction.setEnabled(is_dirty)

        project_is_open = self.project is not None
        self.app_actions.saveAsAction.setEnabled(project_is_open)
        self.app_actions.closeAction.setEnabled(project_is_open)
        self.app_actions.bringToFrontAction.setEnabled(project_is_open)
        self.app_actions.sendToBackAction.setEnabled(project_is_open)

    def writeSettings(self) -> None:
        settings = QSettings()
        settings.beginGroup("MainWindow")
        settings.setValue("geometry", self.saveGeometry())
        settings.endGroup()

    def readSettings(self) -> None:
        logging.info("Settings loading started")
        settings = QSettings()
        settings.beginGroup("MainWindow")
        geometry_array = settings.value("geometry", QByteArray())
        assert isinstance(geometry_array, QByteArray)

        if geometry_array.isEmpty():
            self.setGeometry(200, 200, 400, 300)
            self.center()
        else:
            self.restoreGeometry(geometry_array)

        logging.info("Geometry set: {0}".format(self.geometry()))
        settings.endGroup()
        logging.info("Settings loading finished")

    def initGUI(self) -> None:
        logging.info("GUI initialization started")
        self.setupComponents()

        self.treeView.selectionModel().selectionChanged.connect(
            self.on_selection_changed
        )

        self.updateTitle()
        logging.info("GUI initialization finished")

    def setScaleIndex(self, index) -> None:
        self._scene_scale_combo.setCurrentIndex(index)

    def scaleIndex(self) -> int:
        return self._scene_scale_combo.currentIndex()

    def scaleCount(self) -> int:
        return self._scene_scale_combo.count()

    def _createSceneScaleCombo(self) -> QComboBox:
        scene_scale_combo = QComboBox()
        min_scale = 50
        max_scale = 250
        scene_scale_combo.addItems(
            [f"{scale}%" for scale in range(min_scale, max_scale + 10, 10)]
        )
        scene_scale_combo.currentTextChanged.connect(self.scene_scale_changed)
        scene_scale_combo.setCurrentIndex(5)  # 100%
        return scene_scale_combo

    def createToolBar(self) -> None:
        self._line_button = self._createLineButton()
        self._scene_scale_combo = self._createSceneScaleCombo()
        toolbar: QToolBar = self.addToolBar("Main")
        toolbar.addAction(self.app_actions.newAction)
        toolbar.addAction(self.app_actions.openAction)
        toolbar.addAction(self.app_actions.saveAction)
        toolbar.addAction(self.app_actions.saveAsAction)
        toolbar.addAction(self.app_actions.closeAction)
        toolbar.addSeparator()
        toolbar.addAction(self.app_actions.cutAction)
        toolbar.addAction(self.app_actions.copyAction)
        toolbar.addAction(self.app_actions.pasteAction)
        toolbar.addSeparator()
        toolbar.addAction(self.app_actions.toggleGridAction)
        toolbar.addAction(self.app_actions.bringToFrontAction)
        toolbar.addAction(self.app_actions.sendToBackAction)
        toolbar.addSeparator()
        toolbar.addAction(self.app_actions.addActorElementAction)
        toolbar.addAction(self.app_actions.addEllipseElementAction)
        toolbar.addAction(self.app_actions.addTextElementAction)
        toolbar.addAction(self.app_actions.addCenteredTextElementAction)
        toolbar.addAction(self.app_actions.addNoteElementAction)
        toolbar.addAction(self.app_actions.addSimpleClassElementAction)
        toolbar.addAction(self.app_actions.addFatClassElementAction)
        toolbar.addAction(self.app_actions.addPackageElementAction)
        toolbar.addWidget(self._line_button)
        toolbar.addWidget(self._scene_scale_combo)
        # toolbar.addAction(self.app_actions.printProjectAction)
        self.aToolBar = toolbar

    def setSceneWidgetsEnabled(self, is_enabled: bool) -> None:
        self._line_button.setEnabled(is_enabled)
        self._scene_scale_combo.setEnabled(is_enabled)

    def _createLineButton(self) -> QPushButton:
        line_button = QPushButton("Lines")
        menu = QMenu(line_button)

        for action in self.app_actions.lineActions:
            action.setParent(line_button)
            menu.addAction(action)

        line_button.setMenu(menu)
        proxy_style = LineIconsProxyStyle()
        menu.setStyle(proxy_style)
        return line_button

    def scene_scale_changed(self, scale_percent: str) -> None:
        self.sceneView.scale_changed(scale_percent)

    def createStatusBar(self) -> None:
        """Create Status Bar"""
        self.aStatusBar = QStatusBar(self)
        self.aStatusLabel = QLabel(self.aStatusBar)
        self.aStatusBar.addWidget(self.aStatusLabel, 3)
        self.setStatusBar(self.aStatusBar)

    def createElementsWindow(self) -> None:
        elements_window = QDockWidget("Elements", self)
        elements_window.setMinimumHeight(150)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, elements_window)

    def createPropertyEditor(self) -> None:
        property_window = QDockWidget("Property editor", self)
        self.propertyView = QPlainTextEdit()
        self.propertyView.textChanged.connect(self.on_text_changed)
        self.propertyView.setFont(Settings.element_font)
        self.propertyView.setWordWrapMode(QTextOption.NoWrap)
        self.propertyView.setEnabled(False)
        property_window.setWidget(self.propertyView)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, property_window)

    def on_text_changed(self) -> None:
        if self.element_with_text is None:
            return
        text = self.propertyView.toPlainText()
        self.element_with_text.setText(text)

    @staticmethod
    def isEditable(item: object) -> bool:
        return (
            isinstance(item, BaseElement)
            and Abilities.EDITABLE_TEXT in item.getAbilities()
        )

    def on_scene_selection_changed(self) -> None:
        elements_with_text = [
            item for item in self.scene.selectedItems() if self.isEditable(item)
        ]
        if len(elements_with_text) == 1:
            self.element_with_text = elements_with_text[0]
            self.propertyView.setPlainText(self.element_with_text.text())
            self.propertyView.setEnabled(True)
        else:
            self.element_with_text = None
            self.propertyView.setPlainText(None)
            self.propertyView.setEnabled(False)

    def createCentralWidget(self) -> None:
        scene_size = 2000
        self.scene: GraphicsScene = GraphicsScene(
            self.scene_logic,
            -scene_size // 2,
            -scene_size // 2,
            scene_size,
            scene_size,
            parent=self,
        )

        self.scene.selectionChanged.connect(self.on_scene_selection_changed)

        self.sceneView = GraphicsView(self.scene)
        self.sceneView.setRenderHint(QPainter.Antialiasing)
        self.sceneView.setRenderHint(QPainter.TextAntialiasing)
        self.sceneView.setRenderHint(QPainter.SmoothPixmapTransform)
        self.sceneView.setRenderHint(QPainter.VerticalSubpixelPositioning)

        _ = QShortcut(
            QKeySequence.SelectAll,
            self.sceneView,
            context=Qt.ShortcutContext.WidgetShortcut,
            activated=self.scene_logic.selectAllElements,
        )

        vbox = QVBoxLayout()
        vbox.addWidget(self.sceneView)

        self.centralWidget = QWidget()
        self.centralWidget.setLayout(vbox)
        self.setCentralWidget(self.centralWidget)

    def setupComponents(self) -> None:
        """Initialize visual components"""

        self.createStatusBar()  # used in actions
        self.createProjectTree()
        self.createElementsWindow()
        self.createPropertyEditor()
        self.createCentralWidget()  # used in actions

        self.app_actions = Actions(self)
        self.createMenu()
        self.createToolBar()

        self.disableScene()

    def createMenu(self) -> None:
        self.fileMenu = self.menuBar().addMenu("&File")
        self.editMenu = self.menuBar().addMenu("&Edit")
        self.helpMenu = self.menuBar().addMenu("&Help")

        self.fileMenu.addAction(self.app_actions.newAction)
        self.fileMenu.addAction(self.app_actions.openAction)
        self.fileMenu.addAction(self.app_actions.saveAction)
        self.fileMenu.addAction(self.app_actions.saveAsAction)
        self.fileMenu.addAction(self.app_actions.closeAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.app_actions.exportAsSvgImageAction)
        self.fileMenu.addAction(self.app_actions.exportAsRasterImageAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.app_actions.exitAction)

        self.editMenu.addAction(self.app_actions.cutAction)
        self.editMenu.addAction(self.app_actions.copyAction)
        self.editMenu.addAction(self.app_actions.pasteAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.app_actions.deleteAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.app_actions.bringToFrontAction)
        self.editMenu.addAction(self.app_actions.sendToBackAction)

        self.helpMenu.addAction(self.app_actions.aboutAction)
        self.helpMenu.addAction(self.app_actions.aboutQtAction)

    def center(self) -> None:
        """Center the main window"""

        rect = self.frameGeometry()
        center_point = self.screen().availableGeometry().center()
        rect.moveCenter(center_point)
        self.move(rect.topLeft())

    def closeEvent(self, event) -> None:
        if self._interactors.project_interactor.save_project_if_needed():
            self.writeSettings()
            logging.info("Main window closed")
            event.accept()
        else:
            event.ignore()

    def onTreeViewCustomContextMenuRequested(self, point) -> None:
        """Show context menu for item in the project tree"""
        if not self.treeView.isSelected():
            return
        item = self.treeView.getSelectedItem()
        project_item = self.projectItemFromItem(item)
        menu = QMenu(self.treeView)
        item_type = project_item.item_type

        if item_type is model.ProjectItemType.FOLDER:
            menu.addAction(self.app_actions.createDiagramAction)
            menu.addAction(self.app_actions.createFolderAction)
            if project_item.id != self.project.root.id:
                menu.addAction(self.app_actions.renameProjectItemAction)
                menu.addAction(self.app_actions.deleteProjectItemAction)
        elif item_type is model.ProjectItemType.DIAGRAM:
            menu.addAction(self.app_actions.renameProjectItemAction)
            menu.addAction(self.app_actions.deleteProjectItemAction)

        menu.exec(self.treeView.viewport().mapToGlobal(point))

    def projectItemFromItem(self, item: adapters.StandardItem) -> model.BaseItem:
        item_id = item.itemId()
        project_item: model.BaseItem = self.project.get(item_id)
        return project_item

    def _createTreeView(self) -> TreeView:
        tree_view: TreeView = TreeView(self)
        tree_view.customContextMenuRequested.connect(
            self.onTreeViewCustomContextMenuRequested
        )
        proxy_model: adapters.TreeSortModel = adapters.TreeSortModel(self)
        proxy_model.setSourceModel(adapters.StandardItemModel())
        tree_view.setModel(proxy_model)
        return tree_view

    def createProjectTree(self) -> None:
        self.treeView = self._createTreeView()
        tree_window = QDockWidget("Project", self)
        tree_window.setWidget(self.treeView)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, tree_window)

    def clearProjectTree(self) -> None:
        self.treeView.itemModel.clear()

    def disableScene(self) -> None:
        self.scene_logic.disableScene()

    def printStats(self) -> None:
        if self.project is not None:
            print("number of elements", self.project.count())
            print("number of items", self.treeView.itemModel.count())

    def getSelectedProjectItem(self) -> model.BaseItem:
        if not self.treeView.isSelected():
            return None
        item: adapters.StandardItem = self.treeView.getSelectedItem()
        item_id: UUID = item.itemId()
        project_item: model.BaseItem = self.project.get(item_id)
        return project_item

    def isDiagramSelected(self):
        if not self.treeView.isSelected():
            return False
        project_item: model.BaseItem = self.getSelectedProjectItem()
        return project_item.item_type == model.ProjectItemType.DIAGRAM

    def printProjectItems(self):
        """Debugging feature"""
        if self.project is None:
            print("Project is None")
        else:
            self.printStats()
            self.project.printProjectItems()

    def _add_project_item(self, element, parent_id):
        self.project.add(element, parent_id)

    def create_folder(self, parent_id) -> model.BaseItem:
        project_item: model.BaseItem = model.Folder("New folder")
        self._add_project_item(project_item, parent_id)
        return project_item

    def create_diagram(self, parent_id: UUID) -> model.BaseItem:
        project_item: model.BaseItem = model.Diagram("New diagram")
        self._add_project_item(project_item, parent_id)
        return project_item

    def delete_project_item(self, project_item_id: UUID) -> None:
        """Delete elements from model recursively"""
        if project_item_id == self.project.root.id:
            return
        self.project.remove(project_item_id)

    def setFilename(self, filename) -> None:
        self._interactors.set_filename(filename)

    def getFileNameFromSaveDialog(self, caption=None) -> str:
        initial_filename = self.filename or model.constants.DEFAULT_FILENAME
        filename, selected_filter = QFileDialog.getSaveFileName(
            parent=self,
            caption=caption,
            dir=QDir.currentPath() + "/" + initial_filename,
            filter="All (*);;Umlayer project (*.ulr)",
            selectedFilter="Umlayer project (*.ulr)",
        )
        return filename

    def getFileNameFromOpenDialog(self, caption=None) -> str:
        filename, selected_filter = QFileDialog.getOpenFileName(
            parent=self,
            caption=caption,
            dir=QDir.currentPath(),
            filter="All (*);;Umlayer project (*.ulr)",
            selectedFilter="Umlayer project (*.ulr)",
        )
        return filename

    def _createProjectItem(
        self, parent_id: UUID, item_type: model.ProjectItemType
    ) -> model.BaseItem:
        if item_type == model.ProjectItemType.FOLDER:
            return self.create_folder(parent_id)
        if item_type == model.ProjectItemType.DIAGRAM:
            return self.create_diagram(parent_id)
        raise ValueError("item_type")

    def createProjectItem(self, item_type: model.ProjectItemType) -> None:
        parent_item: adapters.StandardItem = self.treeView.getSelectedItem()
        parent_model_index = parent_item.index()
        parent_proxy_index = self.treeView.getProxyIndex(parent_model_index)
        self.treeView.expand(parent_proxy_index)  # treeView must use proxy index!
        parent_id = parent_item.itemId()

        project_item = self._createProjectItem(parent_id, item_type)

        item = adapters.makeItemFromProjectItem(project_item)
        parent_item.appendRow([item])
        self.treeView.startEditName(item)
        self.updateTitle()

    def getFileNameForRasterImageDialog(self) -> str:
        initial_filename = model.constants.DEFAULT_RASTER_FILENAME
        filename, selected_filter = QFileDialog.getSaveFileName(
            parent=self,
            caption="Export diagram as raster image",
            dir=QDir.currentPath() + "/" + initial_filename,
            filter=(
                "PNG (*.png);;JPG (*.jpg);;JPEG (*.jpeg);;BMP (*.bmp);;"
                "PPM (*.ppm);;XBM (*.xbm);;XPM (*.xpm);;All (*)"
            ),
            selectedFilter="PNG (*.png)",
        )
        return filename

    def getFileNameForSvgImageDialog(self) -> str:
        initial_filename = model.constants.DEFAULT_SVG_FILENAME
        filename, selected_filter = QFileDialog.getSaveFileName(
            parent=self,
            caption="Export diagram as SVG image",
            dir=QDir.currentPath() + "/" + initial_filename,
            filter="SVG image (*.svg);;All (*)",
            selectedFilter="SVG image (*.svg)",
        )
        return filename

    def exportAsRasterImageHandler(self) -> None:
        filename = self.getFileNameForRasterImageDialog()
        if filename is None or len(filename.strip()) == 0:
            return
        try:
            export_scene = ExportScene(self.scene)
            export_scene.exportAsRasterImage(filename)
            logging.info("The scene was exported as raster image")
        except Exception:
            logging.exception(traceback.format_exc())
            self.showCriticalError("Unable to export scene content as raster image!")

    def exportAsSvgImageHandler(self) -> None:
        filename = self.getFileNameForSvgImageDialog()
        if filename is None or len(filename.strip()) == 0:
            return
        try:
            export_scene = ExportScene(self.scene)
            export_scene.exportAsSvgImage(filename)
            logging.info("The scene was exported as SVG image")
        except Exception:
            logging.exception(traceback.format_exc())
            self.showCriticalError("Unable to export scene content as SVG image!")

    def on_selection_changed(
        self, selected: QItemSelection, deselected: QItemSelection
    ) -> None:
        selected_project_items = self.projectItemsFromIndexes(selected.indexes())
        deselected_project_items = self.projectItemsFromIndexes(deselected.indexes())
        self.scene_logic.on_project_item_selection_changed(
            selected_project_items, deselected_project_items
        )

    def projectItemsFromIndexes(self, proxy_indexes) -> list[model.BaseItem]:
        return [
            self.project.get(item.itemId())
            for item in self.treeView.itemsFromProxyIndexes(proxy_indexes)
        ]

    def deleteSelectedItem(self) -> None:
        logging.info("Action: Delete selected project item")
        if not self.treeView.isSelected():
            return
        item: adapters.StandardItem = self.treeView.getSelectedItem()
        self.deleteItem(item)
        self.updateTitle()

    def renameSelectedItem(self) -> None:
        logging.info("Action: Rename selected project item")
        if not self.treeView.isSelected():
            return
        item: adapters.StandardItem = self.treeView.getSelectedItem()
        self.treeView.startEditName(item)
        self.updateTitle()

    def deleteItem(self, item: adapters.StandardItem) -> None:
        """Deletes existing item with children from project tree"""
        item_id: UUID = item.itemId()

        # the order of deletion is important
        self.delete_project_item(item_id)
        self.treeView.deleteItem(item)

    def aboutQtWindow(self) -> None:
        logging.info("Action: About Qt window")
        QMessageBox.aboutQt(self)

    def exitApp(self) -> None:
        logging.info("Action: Exit app")
        self.close()

    def aboutWindow(self) -> None:
        logging.info("Action: About window")
        QMessageBox.about(
            self,
            "About UMLayer",
            f"<h3 align=center>UMLayer</h3>"
            f"<p align=center>{version.__version__}</p>"
            "<p align=center>UML diagram editor</p>"
            "<p align=center>"
            '<a href="https://github.com/selforthis/umlayer">'
            "https://github.com/selforthis/umlayer"
            "</a></p>"
            "<p align=center>Copyright 2021 Serguei Yanush &lt;selforthis@gmail.com&gt;<p>"
            "<p align=center>MIT License</p>",
        )

    def zoom(self, change):
        assert abs(change) == 1
        if change > 0 and self.scaleIndex() == self.scaleCount() - 1:
            return
        if change < 0 and self.scaleIndex() == 0:
            return
        self.setScaleIndex(self.scaleIndex() + change)
