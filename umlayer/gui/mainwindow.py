import logging

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


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
        if geometry_array.isEmpty():
            self.setGeometry(200, 200, 400, 300)
            self.center()
        else:
            assert isinstance(geometry_array, QByteArray)
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

    def createStatusBar(self):
        """Create Status Bar
        """

        self.aStatusLabel = QLabel()

        self.aProgressBar = QProgressBar(self)
        self.aProgressBar.setMinimum(0)
        self.aProgressBar.setMaximum(100)

        self.aStatusBar = QStatusBar(self)
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
        self.setCentralWidget(self.centralWidget)

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
        reply = QMessageBox.question(
            self,
            'Window Close',
            'Are you sure you want to close the window?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)

        return reply == QMessageBox.Yes
