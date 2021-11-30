import logging
import pprint

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from umlayer import model
from . import *


class MainWindow(QMainWindow):
    """Main window of the UMLayer application
    """

    def __init__(self, project_logic, logic, scene_logic, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._project = None
        self.project_logic = project_logic
        self.logic = logic
        self.scene_logic = scene_logic

        self.scene: GraphicsScene = None
        self.sceneView: GraphicsView = None

        self.logic.setWindow(self)
        self.scene_logic.setWindow(self)

        self.readSettings()
        self.setDefaultFileName()
        self.initGUI()

        self.element_with_text = None
        self.createNewProject()

    @property
    def project(self):
        return self._project

    def onIsDirtyChanged(self):
        self.updateTitle()

    def setDefaultFileName(self):
        self.filename = model.constants.DEFAULT_FILENAME

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

    def isDirty(self):
        is_dirty = False if self._project is None else self._project.dirty()
        return is_dirty

    def updateTitle(self):
        title = model.utils.build_window_title(self.filename, self.isDirty())
        self.setWindowTitle(title)

    def initGUI(self):
        logging.info('GUI initialization started')
        self.setupComponents()
        self.treeView.selectionModel().selectionChanged.connect(self.logic.on_selection_changed)
        # self.logic.updateTreeDataModel(self.project)
        self.updateTitle()
        logging.info('GUI initialization finished')

    def setScaleIndex(self, index):
        self._scene_scale_combo.setCurrentIndex(index)

    def scaleIndex(self):
        return self._scene_scale_combo.currentIndex()

    def scaleCount(self):
        return self._scene_scale_combo.count()

    def createToolBar(self):
        self._scene_scale_combo = QComboBox()
        min_scale = 50
        max_scale = 250
        self._scene_scale_combo.addItems(
            [f'{scale}%' for scale in range(min_scale, max_scale + 10, 10)])
        self._scene_scale_combo.currentTextChanged.connect(self.scene_scale_changed)
        self.setScaleIndex(5)  # 100%

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
        self.aToolBar.addAction(self.app_actions.addLineElementAction)
        self.aToolBar.addAction(self.app_actions.addRelationshipElementAction)
        self.aToolBar.addAction(self.app_actions.addTextElementAction)
        self.aToolBar.addAction(self.app_actions.addCenteredTextElementAction)
        self.aToolBar.addAction(self.app_actions.addNoteElementAction)
        self.aToolBar.addAction(self.app_actions.addSimpleClassElementAction)
        self.aToolBar.addAction(self.app_actions.addFatClassElementAction)
        self.aToolBar.addAction(self.app_actions.addPackageElementAction)
        self.aToolBar.addWidget(self._scene_scale_combo)

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
        if self.logic.saveFileIfNeeded():
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
        self.treeView: TreeView = TreeView(self.project_logic, self)
        self.treeView.customContextMenuRequested.connect(self.onTreeViewCustomContextMenuRequested)

        treeWindow.setWidget(self.treeView)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, treeWindow)

        self.sti = StandardItemModel()
        self.treeView.setModel(self.sti)

    def _getNewProject(self):
        project = model.Project()
        project.isDirtyChangedEvent.subscribe(self.onIsDirtyChanged)
        return project

    def updateTreeDataModel(self):
        self.sti.updateItemModel(self._project)
        self.treeView.setInitialState()

    def createNewProject(self):
        self._project = self._getNewProject()
        self.project_logic.init_new_project(self._project)
        self.updateTreeDataModel()
        self.filename = model.constants.DEFAULT_FILENAME
        self.updateTitle()

    def recreateProject(self):
        """Close old and create new project"""
        logging.info('Action: New project')
        if not self.closeProject():
            return

        self.createNewProject()

    def closeProject(self) -> bool:
        logging.info('Action: Close')
        if not self.logic.saveFileIfNeeded():
            return False

        self.scene_logic.disableScene()
        self.sti.clear()
        if self._project is not None:
            self._project.isDirtyChangedEvent.unsubscribe(self.onIsDirtyChanged)
        self._project = None
        self.filename = None
        self.updateTitle()
        return True

    def printStats(self):
        if self._project is not None:
            print('number of elements', self._project.count())
            print('number of items', self.sti.count())

    def load(self, filename: str):
        """Loads project data and settings from a file

        Throws exceptions in case of errors
        """

        project_items: list = self.project_logic.storage_load(filename)
        root = project_items[0]

        self._project = self._getNewProject()
        self._project.setRoot(root)

        for project_item in project_items:
            if project_item.id != root.id:
                self._project.add(project_item, project_item.parent_id)

        self._project.setDirty(False)

    def doOpenProject(self, filename):
        self.load(filename)
        self.updateTreeDataModel()

    def selectedProjectItem(self):
        item = self.treeView.getSelectedItem()
        if item is None:
            return None
        id = item.data(Qt.UserRole)
        project_item = self._project.get(id)
        return project_item

    def isDiagramSelected(self):
        project_item = self.selectedProjectItem()
        if project_item is None:
            return False
        return isinstance(project_item, model.Diagram)
