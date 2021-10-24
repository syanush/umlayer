import logging

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from .graphics_view import GraphicsView
from .user_element import UserElement
from .line_element import LineElement


class MainWindow(QMainWindow):
    """Main window of the UMLayer application
    """

    def __init__(self):
        super().__init__()

        self.readSettings()
        self.initGUI()

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
        self.setWindowTitle("UMLayer")
        self.show()
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

    def createCentralWidget(self):
        self.centralWidget = QWidget()

        # create project tree
        treeWindow = QDockWidget('Project', self)
        self.treeView = QTreeView()
        treeWindow.setWidget(self.treeView)
        #treeWindow.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, treeWindow)

        # create elements
        elementsWindow = QDockWidget('Elements', self)
        self.elementsView = QTextEdit()
        elementsWindow.setWidget(self.elementsView)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, elementsWindow)

        # create property editor
        propertyWindow = QDockWidget('Property editor', self)
        self.propertyView = QTextEdit()
        propertyWindow.setWidget(self.propertyView)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, propertyWindow)

        self.scene = QGraphicsScene() # 0, 0, 400, 200
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

        pixmap = QPixmap("open.png")
        pixmapitem = self.scene.addPixmap(pixmap)
        pixmapitem.setPos(250, 70)
        pixmapitem.setFlags(QGraphicsItem.ItemIsMovable)

    def setupComponents(self):
        """ Initialize visual components
        """

        self.createStatusBar()  # used in actions
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
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAction)
        self.editMenu.addAction(self.copyAction)
        self.fileMenu.addSeparator()
        self.editMenu.addAction(self.pasteAction)
        self.helpMenu.addAction(self.aboutAction)

    # Slots called when the menu actions are triggered
    def newFile(self):
        logging.info('Action: new file')

    def openFile(self):
        logging.info('Action: open file')

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
        self.newAction = QAction(QIcon('new.png'), '&New',
                                 self, shortcut=QKeySequence.New,
                                 statusTip="Create a New File",
                                 triggered=self.newFile)
        self.openAction = QAction(QIcon('open.png'), '&Open',
                                  self, shortcut=QKeySequence.Open,
                                  statusTip="Open a file in editor",
                                  triggered=self.openFile)
        self.exitAction = QAction(QIcon('exit.png'), 'E&xit',
                                  self, shortcut="Ctrl+Q",
                                  statusTip="Exit the Application",
                                  triggered=self.exitFile)
        self.copyAction = QAction(QIcon('copy.png'), 'C&opy',
                                  self, shortcut="Ctrl+C",
                                  statusTip="Copy",
                                  triggered=self.copy)
        self.pasteAction = QAction(QIcon('paste.png'), '&Paste',
                                   self, shortcut="Ctrl+V",
                                   statusTip="Paste",
                                   triggered=self.paste)
        self.aboutAction = QAction(QIcon('about.png'), 'A&bout',
                                   self, statusTip="Displays info about the app",
                                   triggered=self.aboutHelp)
        self.addRectangleAction = QAction(QIcon('rectangle.png'), '&Rectangle',
                                   self, statusTip="Add rectangle",
                                   triggered=self.addRectangle)
        self.addUserElementAction = QAction(QIcon('user_element.svg'), '&User element',
                                          self, statusTip="Add user element",
                                          triggered=self.addUserElement)
        self.addLineElementAction = QAction(QIcon('line_element.png'), '&Line element',
                                            self, statusTip="Add line element",
                                            triggered=self.addLineElement)

    def center(self):
        """Center the main window
        """

        qRect = self.frameGeometry()
        centerPoint = self.screen().availableGeometry().center()
        qRect.moveCenter(centerPoint)
        self.move(qRect.topLeft())

    def closeEvent(self, event):
        if self.userReallyWantsToQuit():
            self.writeSettings()
            logging.info('Main window closed')
            event.accept()
        else:
            event.ignore()

    def userReallyWantsToQuit(self) -> bool:
        reply = QMessageBox.Yes

        # reply = QMessageBox.question(
        #     self,
        #     'Window Close',
        #     'Are you sure you want to close the window?',
        #     QMessageBox.Yes | QMessageBox.No,
        #     QMessageBox.No)

        return reply == QMessageBox.Yes
