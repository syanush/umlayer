import logging

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from .graphics_view import GraphicsView
from .user_element import UserElement
from .line_element import LineElement

from .tree_view import TreeView
from .standard_item_model import StandardItemModel

import umlayer.model.constants as constants
import umlayer.model.utils as utils
from umlayer.model.folder import Folder
from umlayer.model.diagram import Diagram


class MainWindow(QMainWindow):
    """Main window of the UMLayer application
    """

    def __init__(self, project_logic):
        super().__init__()

        self.project_logic = project_logic
        self.readSettings()
        self.setDefaultFileName()
        self.initGUI()

    @property
    def project(self):
        return self.project_logic.project

    def isFileNameNotSet(self) -> bool:
        return self.filename is None or self.filename == constants.DEFAULT_FILENAME

    def setDefaultFileName(self):
        self.filename = constants.DEFAULT_FILENAME

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

    def is_dirty(self):
        return self.project.is_dirty

    def _updateTitle(self, filename):
        title = utils.build_window_title(filename, self.is_dirty())
        self.setWindowTitle(title)
        self.show()

    def updateTitle(self):
        self._updateTitle(self.filename)

    def initGUI(self):
        logging.info('GUI initialization started')
        self.setupComponents()
        self.updateTitle()
        logging.info('GUI initialization finished')

    def createToolBar(self):
        self.aToolBar = self.addToolBar('Main')
        self.aToolBar.addAction(self.newAction)
        self.aToolBar.addSeparator()
        self.aToolBar.addAction(self.copyAction)
        self.aToolBar.addAction(self.pasteAction)
        self.aToolBar.addAction(self.addRectangleAction)
        self.aToolBar.addAction(self.addUserElementAction)
        self.aToolBar.addAction(self.addLineElementAction)
        self.aToolBar.addAction(self.printElementsAction)

    def createStatusBar(self):
        """Create Status Bar
        """

        self.aStatusBar = QStatusBar(self)

        self.aStatusLabel = QLabel(self.aStatusBar)

        self.aProgressBar = QProgressBar(self.aStatusBar)
        self.aProgressBar.setMinimum(0)
        self.aProgressBar.setMaximum(100)

        self.aStatusBar.addWidget(self.aStatusLabel, 3)
        self.aStatusBar.addWidget(self.aProgressBar, 1)
        self.setStatusBar(self.aStatusBar)

    def showProgress(self, progress):
        """ Function to show progress
        """

        self.aProgressBar.setValue(progress)
        if progress == 100:
            self.aStatusLabel.setText('Ready')
        else:
            self.aStatusLabel.setText('Loading...')
        return

    def createElementsWindow(self):
        # create elements
        elementsWindow = QDockWidget('Elements', self)
        self.elementsView = QTextEdit()
        elementsWindow.setWidget(self.elementsView)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, elementsWindow)

    def createPropertyEditor(self):
        # create property editor
        propertyWindow = QDockWidget('Property editor', self)
        self.propertyView = QTextEdit()
        propertyWindow.setWidget(self.propertyView)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, propertyWindow)

    def createCentralWidget(self):
        self.centralWidget = QWidget()

        self.scene = QGraphicsScene()  # 0, 0, 400, 200
        # self.createScene()

        self.sceneView = GraphicsView(self.scene)
        self.sceneView.setRenderHints(
            QPainter.Antialiasing |
            QPainter.TextAntialiasing |
            QPainter.SmoothPixmapTransform |
            QPainter.VerticalSubpixelPositioning
        )

        vbox = QVBoxLayout()
        vbox.addWidget(self.sceneView)
        self.centralWidget.setLayout(vbox)

        self.setCentralWidget(self.centralWidget)

    def createScene(self):
        rect = QGraphicsRectItem(0, 0, 200, 50)

        # Set the origin (position) of the rectangle in the scene.
        rect.setPos(50, 20)

        # Define the brush (fill).
        brush = QBrush(Qt.red)
        rect.setBrush(brush)

        # Define the pen (line)
        pen = QPen(Qt.cyan)
        pen.setWidth(10)
        rect.setPen(pen)

        rect.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.scene.addItem(rect)

        ellipse = QGraphicsEllipseItem(0, 0, 100, 100)
        ellipse.setPos(75, 30)

        brush = QBrush(Qt.blue)
        ellipse.setBrush(brush)

        pen = QPen(Qt.green)
        pen.setWidth(5)
        ellipse.setPen(pen)

        # Add the items to the scene. Items are stacked in the order they are added.
        self.scene.addItem(ellipse)

        # Movable items
        ellipse.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

        textitem = self.scene.addText('QGraphics is fun!')
        textitem.setPos(150, 120)
        textitem.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

        qpolygon = QPolygonF([
            QPointF(30, 60),
            QPointF(70, 40),
            QPointF(40, 20),
            QPointF(20, 15),
        ])

        polygon = self.scene.addPolygon(qpolygon, QPen(Qt.GlobalColor.darkGreen))
        polygon.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

        pixmap = QPixmap('resources/icons/open.png')
        pixmapitem = self.scene.addPixmap(pixmap)
        pixmapitem.setPos(250, 70)
        pixmapitem.setFlags(QGraphicsItem.ItemIsMovable)

    def setupComponents(self):
        """ Initialize visual components
        """

        self.createStatusBar()  # used in actions
        self.createProjectTree()
        self.createElementsWindow()
        self.createPropertyEditor()
        self.createCentralWidget()  # used in actions

        self.createActions()
        self.createMenu()
        self.createToolBar()

    def createMenu(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.editMenu = self.menuBar().addMenu("&Edit")
        self.helpMenu = self.menuBar().addMenu("&Help")

        self.fileMenu.addAction(self.newAction)
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.saveAsAction)
        self.fileMenu.addAction(self.closeAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAction)
        self.editMenu.addAction(self.copyAction)
        self.fileMenu.addSeparator()
        self.editMenu.addAction(self.pasteAction)
        self.helpMenu.addAction(self.aboutAction)

    # Slots called when the menu actions are triggered
    def newProject(self):
        logging.info('Action: New')
        if not self.closeProject():
            return
        self.project_logic.new_project()

        self.treeView.updateTreeDataModel()

        self.filename = constants.DEFAULT_FILENAME
        self.updateTitle()

    def _getFileNameFromOpenDialog(self, caption=None):
        fileName, selectedFilter = \
            QFileDialog.getOpenFileName(
                parent=None,
                caption=caption,
                dir=QDir.currentPath(),
                filter="All (*);;Umlayer project (*.ulr)",
                selectedFilter="Umlayer project (*.ulr)")
        return fileName

    def openProject(self):
        logging.info('Action: Open')
        if not self.closeProject():
            return

        fileName = self._getFileNameFromOpenDialog('Open')

        if len(fileName) == 0:
            return

        try:
            self.doOpenProject(fileName)
        except Exception as ex:
            print(ex)
        else:
            self.filename = fileName
            self.updateTitle()

        self.printStats()

    def doOpenProject(self, filename):
        self.project_logic.load(filename)
        self.treeView.updateTreeDataModel()

    def _getFileNameFromSaveDialog(self, caption=None):
        initial_filename = self.filename or constants.DEFAULT_FILENAME
        fileName, selectedFilter = \
            QFileDialog.getSaveFileName(
                parent=None,
                caption=caption,
                dir=QDir.currentPath() + '/' + initial_filename,
                filter="All (*);;Umlayer project (*.ulr)",
                selectedFilter="Umlayer project (*.ulr)")
        return fileName

    def saveProject(self):
        fileName = self._getFileNameFromSaveDialog('Save') if self.isFileNameNotSet() else self.filename

        if len(fileName) == 0:
            return

        try:
            self.doSaveProject(fileName)
        except:
            pass
        else:
            self.filename = fileName
            self.updateTitle()

    def doSaveProject(self, filename):
        """Really save project"""
        self.project_logic.save(filename)

    def saveProjectAs(self):
        logging.info('Action: Save As')

        fileName = self._getFileNameFromSaveDialog('Save as...')

        if len(fileName) == 0:
            return

        try:
            self.doSaveProject(fileName)
        except Exception as ex:
            pass
        else:
            self.filename = fileName
            self.updateTitle()

    def closeDiagramWindows(self) -> bool:
        """Returns true if windows are closed successfully"""
        return True

    def closeProject(self) -> bool:
        logging.info('Action: Close')
        if not self.saveFileIfNeeded():
            return False

        if not self.closeDiagramWindows():
            return False

        self.clearTreeDataModel()
        self.project_logic.clear_project()
        self.filename = None
        self.updateTitle()
        return True

    def exitFile(self):
        self.close()

    def copy(self):
        pass

    def paste(self):
        pass

    def aboutHelp(self):
        QMessageBox.about(self, "About ...",
                          "This example demonstrates the use "
                          "of Menu Bar")

    def addUserElement(self):
        logging.info('Add user element')
        element = UserElement()
        element.setPos(50, 50)
        element.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.scene.addItem(element)

    def addLineElement(self):
        logging.info('Add line element')
        element = LineElement()
        element.setPos(50, 50)
        element.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.scene.addItem(element)

    def addRectangle(self):
        logging.info('Add rectangle')

        rect = QGraphicsRectItem(0, 0, 200, 50)

        # Set the origin (position) of the rectangle in the scene.
        rect.setPos(50, 20)

        # Define the brush (fill).
        brush = QBrush(Qt.red)
        rect.setBrush(brush)

        # Define the pen (line)
        pen = QPen(Qt.cyan)
        pen.setWidth(10)
        rect.setPen(pen)

        rect.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.scene.addItem(rect)

    # Function to create actions for menus
    def createActions(self):
        self.newAction = QAction(QIcon('resources/icons/new.png'), '&New',
                                 self, shortcut=QKeySequence.New,
                                 statusTip='Create a New Project',
                                 triggered=self.newProject)
        self.openAction = QAction(QIcon('resources/icons/open.png'), '&Open',
                                  self, shortcut=QKeySequence.Open,
                                  statusTip='Open a project in editor',
                                  triggered=self.openProject)
        self.saveAction = QAction(QIcon('resources/icons/save.png'), '&Save',
                                  self, shortcut=QKeySequence.Save,
                                  statusTip='Save a project',
                                  triggered=self.saveProject)
        self.saveAsAction = QAction(QIcon('resources/icons/save_as.png'), 'Save As...',
                                    self, shortcut=QKeySequence.SaveAs,
                                    statusTip='Save a project',
                                    triggered=self.saveProjectAs)
        self.closeAction = QAction(QIcon('resources/icons/close.png'), '&Close',
                                   self, shortcut=QKeySequence.Close,
                                   statusTip='Close current project',
                                   triggered=self.closeProject)
        self.exitAction = QAction(QIcon('resources/icons/exit.png'), '&Quit',
                                  self, shortcut=QKeySequence.Quit,
                                  statusTip='Quit the Application',
                                  triggered=self.exitFile)
        self.copyAction = QAction(QIcon('resources/icons/copy.png'), 'C&opy',
                                  self, shortcut='Ctrl+C',
                                  statusTip='Copy',
                                  triggered=self.copy)
        self.pasteAction = QAction(QIcon('resources/icons/paste.png'), '&Paste',
                                   self, shortcut='Ctrl+V',
                                   statusTip='Paste',
                                   triggered=self.paste)
        self.aboutAction = QAction(QIcon('resources/icons/about.png'), 'A&bout',
                                   self, statusTip='Displays info about the app',
                                   triggered=self.aboutHelp)
        self.addRectangleAction = QAction(QIcon('resources/icons/rectangle.png'), '&Rectangle',
                                          self, statusTip='Add rectangle',
                                          triggered=self.addRectangle)
        self.addUserElementAction = QAction(QIcon('resources/icons/user_element.svg'), '&User element',
                                            self, statusTip='Add user element',
                                            triggered=self.addUserElement)
        self.addLineElementAction = QAction(QIcon('resources/icons/line_element.png'), '&Line element',
                                            self, statusTip='Add line element',
                                            triggered=self.addLineElement)
        self.printElementsAction = QAction(QIcon('resources/icons/cache.png'), 'Print',
                                           self, statusTip='print',
                                           triggered=self.project.printElements)
        self.createDiagramAction = QAction(QIcon('resources/icons/diagram.png'), 'Create diagram',
                                           self, statusTip='Create diagram',
                                           triggered=self.createDiagram)
        self.createFolderAction = QAction(QIcon('resources/icons/create_folder.png'), 'Create folder',
                                          self, statusTip='Create folder',
                                          triggered=self.createFolder)
        self.deleteElementAction = QAction(QIcon('resources/icons/delete.png'), 'Delete element',
                                           self, shortcut=QKeySequence.Delete, statusTip='Delete element',
                                           triggered=self.deleteElement)

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

    def saveFileIfNeeded(self) -> bool:
        if not self.is_dirty():
            return True

        reply = QMessageBox.question(
            self,
            'Warning \u2014 Umlayer',
            'The current file has been modified.\nDo you want to save it?',
            QMessageBox.Cancel | QMessageBox.Discard | QMessageBox.Save,
            QMessageBox.Save)

        if reply == QMessageBox.Save:
            self.saveProject()

        return reply != QMessageBox.Cancel

    def onTreeViewCustomContextMenuRequested(self, point):
        # show context menu
        item = self.treeView.getSelectedItem()

        if item is None:
            return

        element = self.treeView.elementFromItem(item)

        menu = QMenu(self.treeView)

        if type(element) is Folder:
            menu.addAction(self.createDiagramAction)
            menu.addAction(self.createFolderAction)
            if element.id != self.project.root.id:
                menu.addAction(self.deleteElementAction)
        elif type(element) is Diagram:
            menu.addAction(self.deleteElementAction)

        menu.exec(self.treeView.viewport().mapToGlobal(point))

    def createProjectTree(self):
        treeWindow = QDockWidget('Project', self)
        self.treeView = TreeView(self, self.project_logic)
        self.treeView.customContextMenuRequested.connect(self.onTreeViewCustomContextMenuRequested)
        self.treeView.itemDelegate().closeEditor.connect(self.treeView.onCloseEditor)

        treeWindow.setWidget(self.treeView)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, treeWindow)

        self.sti = StandardItemModel()
        self.treeView.setModel(self.sti)
        self.treeView.updateTreeDataModel()

        shortcut = QShortcut(QKeySequence.Delete,
                             self.treeView,
                             context=Qt.WidgetShortcut,
                             activated=self.deleteElement)

    def clearTreeDataModel(self):
        self.sti.clear()

    def createElement(self, create_method):
        self.treeView.createElement(create_method)
        self.updateTitle()

    def createFolder(self):
        self.createElement(self.project_logic.create_folder)

    def createDiagram(self):
        self.createElement(self.project_logic.create_diagram)

    def deleteElement(self):
        self.treeView.deleteElement()
        self.updateTitle()
        self.printStats()

    def printStats(self):
        print('number of elements', self.project.count())
        print('number of items', self.sti.count())
