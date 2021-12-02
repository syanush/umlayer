import logging
import pprint
from uuid import UUID

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtSvg import QSvgGenerator
from PySide6.QtWidgets import *

from umlayer import version, model
from . import *


class MainWindow(QMainWindow):
    """Main window of the UMLayer application
    """

    def __init__(self, scene_logic, storage, data_model, interactors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_logic = scene_logic
        self._storage: ProjectStorage = storage
        self._interactors = interactors
        self._data_model = data_model

        self.scene: GraphicsScene = None
        self.sceneView: GraphicsView = None

        self.scene_logic.setWindow(self)

        self.readSettings()
        self.setDefaultFileName()
        self.initGUI()

        self.element_with_text = None
        self.createNewProject()

    @property
    def filename(self):
        return self._data_model.filename

    @property
    def project(self):
        return self._data_model.project

    def setDirty(self, dirty):
        if self.project:
            self.project.setProjectDirty(dirty)
        self.updateTitle()

    def setDefaultFileName(self):
        self._data_model.set_filename(model.constants.DEFAULT_FILENAME)

    def openProject(self):
        logging.info('Action: Open')
        self._interactors.project_interactor.open_project()

    def saveProject(self):
        logging.info('Action: Save')
        self._interactors.project_interactor.save_project()

    def saveProjectAs(self):
        logging.info('Action: Save As')
        self._interactors.project_interactor.save_project_as()

    def closeProject(self) -> bool:
        logging.info('Action: Close')
        return self._interactors.project_interactor.close_project()

    def clearScene(self):
        self.scene_logic.disableScene()
        self.sti.clear()

    def askToSaveModifiedFile(self):
        reply = QMessageBox.question(
            self,
            'Warning \u2014 Umlayer',
            'The current file has been modified.\nDo you want to save it?',
            QMessageBox.Cancel | QMessageBox.Discard | QMessageBox.Save,
            QMessageBox.Save)
        if reply == QMessageBox.Cancel:
            return model.constants.CANCEL
        if reply == QMessageBox.Discard:
            return model.constants.DISCARD
        return model.constants.SAVE

    def criticalError(self, message):
        QMessageBox.critical(self, 'Error!', message, QMessageBox.Abort)

    def isDirty(self):
        return self._interactors.project_interactor.is_dirty()

    def updateTitle(self):
        title = model.utils.build_window_title(self.filename, self.isDirty())
        self.setWindowTitle(title)
        self.updateToolbar()

    def updateToolbar(self):
        self.app_actions.saveAction.setEnabled(self.isDirty())
        self.app_actions.closeAction.setEnabled(self.project is not None)

    def writeSettings(self):
        settings = QSettings()
        settings.beginGroup("MainWindow")
        settings.setValue("geometry", self.saveGeometry())
        settings.endGroup()

    def readSettings(self):
        logging.info('Settings loading started')
        settings = QSettings()
        settings.beginGroup("MainWindow")
        geometry_array = settings.value("geometry", QByteArray())
        assert isinstance(geometry_array, QByteArray)

        if geometry_array.isEmpty():
            self.setGeometry(200, 200, 400, 300)
            self.center()
        else:
            self.restoreGeometry(geometry_array)

        logging.info('Geometry set: {0}'.format(self.geometry()))
        settings.endGroup()
        logging.info('Settings loading finished')

    def initGUI(self):
        logging.info('GUI initialization started')
        self.setupComponents()
        self.treeView.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.updateTitle()
        logging.info('GUI initialization finished')

    def setScaleIndex(self, index):
        self._scene_scale_combo.setCurrentIndex(index)

    def scaleIndex(self):
        return self._scene_scale_combo.currentIndex()

    def scaleCount(self):
        return self._scene_scale_combo.count()

    def _createSceneScaleCombo(self):
        scene_scale_combo = QComboBox()
        min_scale = 50
        max_scale = 250
        scene_scale_combo.addItems(
            [f'{scale}%' for scale in range(min_scale, max_scale + 10, 10)])
        scene_scale_combo.currentTextChanged.connect(self.scene_scale_changed)
        scene_scale_combo.setCurrentIndex(5)  # 100%
        return scene_scale_combo

    def createToolBar(self):
        self.aToolBar: QToolBar = self.addToolBar('Main')
        self.aToolBar.addAction(self.app_actions.newAction)
        self.aToolBar.addAction(self.app_actions.openAction)
        self.aToolBar.addAction(self.app_actions.saveAction)
        self.aToolBar.addAction(self.app_actions.saveAsAction)
        self.aToolBar.addAction(self.app_actions.closeAction)
        self.aToolBar.addSeparator()
        self.aToolBar.addAction(self.app_actions.cutAction)
        self.aToolBar.addAction(self.app_actions.copyAction)
        self.aToolBar.addAction(self.app_actions.pasteAction)
        self.aToolBar.addSeparator()
        self.aToolBar.addAction(self.app_actions.toggleGridAction)
        self.aToolBar.addAction(self.app_actions.bringToFrontAction)
        self.aToolBar.addAction(self.app_actions.sendToBackAction)
        self.aToolBar.addSeparator()
        self.aToolBar.addAction(self.app_actions.addActorElementAction)
        self.aToolBar.addAction(self.app_actions.addEllipseElementAction)
        self.aToolBar.addAction(self.app_actions.addTextElementAction)
        self.aToolBar.addAction(self.app_actions.addCenteredTextElementAction)
        self.aToolBar.addAction(self.app_actions.addNoteElementAction)
        self.aToolBar.addAction(self.app_actions.addSimpleClassElementAction)
        self.aToolBar.addAction(self.app_actions.addFatClassElementAction)
        self.aToolBar.addAction(self.app_actions.addPackageElementAction)
        self._line_button = self._createLineButton()
        self.aToolBar.addWidget(self._line_button)
        self._scene_scale_combo = self._createSceneScaleCombo()
        self.aToolBar.addWidget(self._scene_scale_combo)
        # self.aToolBar.addAction(self.app_actions.printProjectAction)

    def setSceneWidgetsEnabled(self, isEnabled):
        self._line_button.setEnabled(isEnabled)
        self._scene_scale_combo.setEnabled(isEnabled)

    def _createLineButton(self):
        lineButton = QPushButton('Lines')
        menu = QMenu(lineButton)
        # line icon size: 110 x 40
        menu.addAction(QAction(icon=QIcon('icons:a1.png'), text='Association', parent=lineButton,
                               triggered=lambda: self.scene_logic.addLine('lt=-')))
        menu.addAction(QAction(icon=QIcon('icons:a4.png'), text='Directional association', parent=lineButton,
                               triggered=lambda: self.scene_logic.addLine('lt=->'))),
        menu.addAction(QAction(icon=QIcon('icons:a5.png'), text='Bidirectional association', parent=lineButton,
                               triggered=lambda: self.scene_logic.addLine('lt=<->')))
        menu.addAction(QAction(icon=QIcon('icons:a7.png'), text='Aggregation', parent=lineButton,
                               triggered=lambda: self.scene_logic.addLine('lt=->>>>')))
        menu.addAction(QAction(icon=QIcon('icons:a8.png'), text='Composition', parent=lineButton,
                               triggered=lambda: self.scene_logic.addLine('lt=->>>>>')))
        menu.addAction(QAction(icon=QIcon('icons:a9.png'), text='Inheritance/Generalization', parent=lineButton,
                               triggered=lambda: self.scene_logic.addLine('lt=->>')))
        menu.addAction(QAction(icon=QIcon('icons:a10.png'), text='Realization/Implementation', parent=lineButton,
                               triggered=lambda: self.scene_logic.addLine('lt=.>>')))
        menu.addAction(QAction(icon=QIcon('icons:a11.png'), text='Dependency', parent=lineButton,
                               triggered=lambda: self.scene_logic.addLine('lt=.>')))
        menu.addAction(QAction(icon=QIcon('icons:a2.png'), text='', parent=lineButton,
                               triggered=lambda: self.scene_logic.addLine('lt=.')))
        menu.addAction(QAction(icon=QIcon('icons:a3.png'), text='Note connector', parent=lineButton,
                               triggered=lambda: self.scene_logic.addLine('lt=..')))
        menu.addAction(QAction(icon=QIcon('icons:a6.png'), text='Synchronous message', parent=lineButton,
                               triggered=lambda: self.scene_logic.addLine('lt=->>>')))
        menu.addAction(QAction(icon=QIcon('icons:a12.png'), text='Asynchronous message', parent=lineButton,
                               triggered=lambda: self.scene_logic.addLine('lt=->>>>>>')))
        lineButton.setMenu(menu)
        myStyle = LineIconsProxyStyle()
        menu.setStyle(myStyle)
        return lineButton

    def scene_scale_changed(self, scale):
        self.sceneView.scale_changed(scale)

    def createStatusBar(self):
        """Create Status Bar
        """

        self.aStatusBar = QStatusBar(self)
        self.aStatusLabel = QLabel(self.aStatusBar)
        self.aStatusBar.addWidget(self.aStatusLabel, 3)
        self.setStatusBar(self.aStatusBar)

    def createElementsWindow(self):
        elementsWindow = QDockWidget('Elements', self)
        elementsWindow.setMinimumHeight(150)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, elementsWindow)

    def createPropertyEditor(self):
        propertyWindow = QDockWidget('Property editor', self)
        self.propertyView = QPlainTextEdit()
        self.propertyView.textChanged.connect(self.on_text_changed)
        self.propertyView.setFont(Settings.element_font)
        self.propertyView.setWordWrapMode(QTextOption.NoWrap)
        self.propertyView.setEnabled(False)
        propertyWindow.setWidget(self.propertyView)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, propertyWindow)

    def on_text_changed(self):
        if self.element_with_text is None:
            return
        text = self.propertyView.toPlainText()
        self.element_with_text.setText(text)

    def on_scene_selection_changed(self):
        elements_with_text = [item for item in self.scene.selectedItems()
                             if isinstance(item, BaseElement) and
                             Abilities.EDITABLE_TEXT in item.getAbilities()]
        if len(elements_with_text) == 1:
            self.element_with_text = elements_with_text[0]
            self.propertyView.setPlainText(self.element_with_text.text())
            self.propertyView.setEnabled(True)
        else:
            self.element_with_text = None
            self.propertyView.setPlainText(None)
            self.propertyView.setEnabled(False)

    def createCentralWidget(self):
        scene_size = 2000
        self.scene: GraphicsScene = \
            GraphicsScene(self.scene_logic, -scene_size//2, -scene_size//2, scene_size, scene_size, parent=self)

        self.scene.selectionChanged.connect(self.on_scene_selection_changed)

        self.sceneView = GraphicsView(self.scene)
        self.sceneView.setRenderHints(
            QPainter.Antialiasing |
            QPainter.TextAntialiasing |
            QPainter.SmoothPixmapTransform |
            QPainter.VerticalSubpixelPositioning
        )

        shortcut = QShortcut(QKeySequence.SelectAll,
                             self.sceneView,
                             context=Qt.ShortcutContext.WidgetShortcut,
                             activated=self.scene_logic.selectAllElements)

        vbox = QVBoxLayout()
        vbox.addWidget(self.sceneView)

        self.centralWidget = QWidget()
        self.centralWidget.setLayout(vbox)
        self.setCentralWidget(self.centralWidget)

    def setupComponents(self):
        """ Initialize visual components
        """

        self.createStatusBar()  # used in actions
        self.createProjectTree()
        self.createElementsWindow()
        self.createPropertyEditor()
        self.createCentralWidget()  # used in actions

        self.app_actions = Actions(self)
        self.createMenu()
        self.createToolBar()

        self.scene_logic.disableScene()

    def createMenu(self):
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

    def center(self):
        """Center the main window
        """

        qRect = self.frameGeometry()
        centerPoint = self.screen().availableGeometry().center()
        qRect.moveCenter(centerPoint)
        self.move(qRect.topLeft())

    def closeEvent(self, event):
        if self.saveFileIfNeeded():
            self.writeSettings()
            logging.info('Main window closed')
            event.accept()
        else:
            event.ignore()

    def onTreeViewCustomContextMenuRequested(self, point):
        # show context menu
        item = self.treeView.getSelectedItem()

        if item is None:
            return

        element = self.projectItemFromItem(item)

        menu = QMenu(self.treeView)

        if type(element) is model.Folder:
            menu.addAction(self.app_actions.createDiagramAction)
            menu.addAction(self.app_actions.createFolderAction)
            if element.id != self.project.root.id:
                menu.addAction(self.app_actions.deleteProjectItemAction)
        elif type(element) is model.Diagram:
            menu.addAction(self.app_actions.deleteProjectItemAction)

        menu.exec(self.treeView.viewport().mapToGlobal(point))

    def projectItemFromItem(self, item):
        id = item.data(Qt.UserRole)
        return self.project.get(id)

    def createProjectTree(self):
        treeWindow = QDockWidget('Project', self)
        self.treeView: TreeView = TreeView(self)
        self.treeView.customContextMenuRequested.connect(self.onTreeViewCustomContextMenuRequested)

        treeWindow.setWidget(self.treeView)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, treeWindow)

        self.sti = StandardItemModel()
        self.treeView.setModel(self.sti)

    def updateTreeDataModel(self):
        self.sti.updateItemModel(self.project)
        self.treeView.setInitialState()

    def createNewProject(self):
        self._data_model.create_project()
        self.init_new_project()
        self.updateTreeDataModel()
        self.setDefaultFileName()
        self.updateTitle()

    def recreateProject(self):
        """Close old and create new project"""
        logging.info('Action: New project')
        if not self.closeProject():
            return

        self.createNewProject()

    def printStats(self):
        if self.project is not None:
            print('number of elements', self.project.count())
            print('number of items', self.sti.count())

    def load(self, filename: str):
        """Loads project data and settings from a file

        Throws exceptions in case of errors
        """

        project_items: list = self.storage_load(filename)
        root = project_items[0]

        self._data_model.create_project()
        self.project.setRoot(root)

        for project_item in project_items:
            if project_item.id != root.id:
                self.project.add(project_item, project_item.parent_id)

        self.setDirty(False)

    def doOpenProject(self, filename):
        self.load(filename)
        self.updateTreeDataModel()

    def selectedProjectItem(self):
        item = self.treeView.getSelectedItem()
        if item is None:
            return None
        id = item.data(Qt.UserRole)
        project_item = self.project.get(id)
        return project_item

    def isDiagramSelected(self):
        project_item = self.selectedProjectItem()
        if project_item is None:
            return False
        return isinstance(project_item, model.Diagram)

    def printProjectItems(self):
        """Debugging feature"""
        if self.project is None:
            print('Project is None')
            return
        self.project.printProjectItems()

    def init_new_project(self):
        root = model.Folder("Root")
        self.project.setRoot(root)
        self.project.add(model.Diagram("Diagram 1"), root.id)
        self.setDirty(False)

    def _add_project_item(self, element, parent_id):
        self.project.add(element, parent_id)

    def create_folder(self, parent_id):
        project_item = model.Folder("New folder")
        self._add_project_item(project_item, parent_id)
        return project_item

    def create_diagram(self, parent_id):
        project_item = model.Diagram("New diagram")
        self._add_project_item(project_item, parent_id)
        return project_item

    def delete_project_item(self, project_item_id: UUID):
        """Delete elements from model recursively"""
        if project_item_id == self.project.root.id:
            return
        self.project.remove(project_item_id)

    def save(self, filename: str):
        """Saves project data and settings to a file

        Throws exceptions in case of errors
        """

        if filename is None:
            raise ValueError('filename')

        project_items = self.project.project_items.values()
        self._storage.save(project_items, filename)
        self.setDirty(False)

    def storage_load(self, filename):
        return self._storage.load(filename)

    def setFilename(self, filename):
        self._interactors.set_filename(filename)

    def doSaveProject(self, filename):
        """Really save project"""

        if self.project is None:
            return

        self.scene_logic.storeScene()
        self.save(filename)

    def getFileNameFromSaveDialog(self, caption=None):
        initial_filename = self.filename or model.constants.DEFAULT_FILENAME
        filename, selected_filter = \
            QFileDialog.getSaveFileName(
                parent=self,
                caption=caption,
                dir=QDir.currentPath() + '/' + initial_filename,
                filter="All (*);;Umlayer project (*.ulr)",
                selectedFilter="Umlayer project (*.ulr)")
        return filename

    def getFileNameFromOpenDialog(self, caption=None):
        filename, selected_filter = \
            QFileDialog.getOpenFileName(
                parent=self,
                caption=caption,
                dir=QDir.currentPath(),
                filter="All (*);;Umlayer project (*.ulr)",
                selectedFilter="Umlayer project (*.ulr)")
        return filename

    def createProjectItem(self, isDiagram=True):
        parent_item: QStandardItem = self.treeView.getSelectedItem()
        parent_index = parent_item.index()
        self.treeView.expand(parent_index)
        parent_id = parent_item.data(Qt.UserRole)

        if isDiagram:
            project_item = self.create_diagram(parent_id)
        else:
            project_item = self.create_folder(parent_id)

        item = StandardItemModel.makeItem(project_item)
        parent_item.insertRow(0, [item])
        self.treeView.startEditName(item)
        self.updateTitle()

    def projectItemsFromSelection(self, selection):
        result = []
        for index in selection.indexes():
            item = self.sti.itemFromIndex(index)
            if item is None:
                continue
            id = item.data(Qt.UserRole)
            project_item = self.project.get(id)
            result.append(project_item)
        return tuple(result)

    def exportAsSvgImage(self, filename):
        tempScene = self.scene.getTempScene()
        newSceneRect = tempScene.itemsBoundingRect()
        sceneSize = newSceneRect.size().toSize()
        generator = QSvgGenerator()
        generator.setFileName(filename)
        generator.setSize(sceneSize)
        generator.setViewBox(QRect(0, 0, sceneSize.width(), sceneSize.height()))
        generator.setDescription("UML diagram")
        generator.setTitle(filename)
        painter = QPainter()
        painter.begin(generator)
        tempScene.render(painter)
        painter.end()
        tempScene.clear()
        logging.info('The scene was exported as SVG image')

    def exportAsRasterImage(self, filename):
        tempScene = self.scene.getTempScene()
        newSceneRect = tempScene.itemsBoundingRect()
        sceneSize = newSceneRect.size().toSize()
        image = QImage(sceneSize, QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        painter = QPainter()
        painter.begin(image)
        tempScene.render(painter)
        painter.end()
        image.save(filename)
        logging.info('The scene was exported as raster image')

    def getFileNameForRasterImageDialog(self):
        initial_filename = model.constants.DEFAULT_RASTER_FILENAME
        filename, selected_filter = \
            QFileDialog.getSaveFileName(
                parent=self,
                caption='Export diagram as raster image',
                dir=QDir.currentPath() + '/' + initial_filename,
                filter='PNG (*.png);;JPG (*.jpg);;JPEG (*.jpeg);;BMP (*.bmp);;PPM (*.ppm);;XBM (*.xbm);;XPM (*.xpm);;All (*)',
                selectedFilter='PNG (*.png)'
            )
        return filename

    def getFileNameForSvgImageDialog(self):
        initial_filename = model.constants.DEFAULT_SVG_FILENAME

        filename, selected_filter = \
            QFileDialog.getSaveFileName(
                parent=self,
                caption='Export diagram as SVG image',
                dir=QDir.currentPath() + '/' + initial_filename,
                filter='SVG image (*.svg);;All (*)',
                selectedFilter='SVG image (*.svg)')
        return filename

    def exportAsRasterImageHandler(self):
        filename = self.getFileNameForRasterImageDialog()

        if filename is not None and len(filename.strip()) != 0:
            self.exportAsRasterImage(filename)

    def exportAsSvgImageHandler(self):
        filename = self.getFileNameForSvgImageDialog()

        if filename is not None and len(filename.strip()) != 0:
            self.exportAsSvgImage(filename)

    def createDiagram(self):
        logging.info('Action: Create Diagram')
        self.createProjectItem(True)

    def createFolder(self):
        logging.info('Action: Create Folder')
        self.createProjectItem(False)

    def on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        # logging.info('Project selection changed')
        selected_project_items = self.projectItemsFromSelection(selected)
        deselected_project_items = self.projectItemsFromSelection(deselected)
        self.scene_logic.on_project_item_selection_changed(
            selected_project_items, deselected_project_items)

    def finishNameEditing(self):
        logging.info('Finish name editing')
        item: QStandardItem = self.treeView.getSelectedItem()
        if item is None:
            return
        id = item.data(Qt.UserRole)
        project_item = self.project.get(id)
        if project_item.name() != item.text():
            project_item.setName(item.text())
            self.setDirty(True)
        parent_item = item.parent()
        parent_item.sortChildren(0, Qt.SortOrder.AscendingOrder)
        self.treeView.scrollTo(item.index())

    def deleteSelectedItem(self):
        logging.info('Action: Delete selected project item')
        item: QStandardItem = self.treeView.getSelectedItem()
        if item is None:
            return
        id = item.data(Qt.UserRole)
        self.delete_project_item(id)
        index = item.index()
        self.sti.removeRow(index.row(), index.parent())
        self.updateTitle()

    def aboutQtWindow(self):
        logging.info('Action: About Qt window')
        QMessageBox.aboutQt(self)

    def exitApp(self):
        logging.info('Action: Exit app')
        self.close()

    def aboutWindow(self):
        logging.info('Action: About window')
        QMessageBox.about(
            self,
            'About UMLayer',
            f'<h3 align=center>UMLayer</h3>'
            f'<p align=center>{version.__version__}</p>'
            '<p align=center>UML diagram editor</p>'
            '<p align=center><a href="https://github.com/selforthis/umlayer">https://github.com/selforthis/umlayer</a></p>'
            '<p align=center>Copyright 2021 Serguei Yanush &lt;selforthis@gmail.com&gt;<p>'
            '<p align=center>MIT License</p>'
        )
