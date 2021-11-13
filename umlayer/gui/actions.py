from PySide6.QtGui import *


class Actions:
    def __init__(self, window):
        self.window = window
        self.logic = window.logic
        self.createActions()

    def createActions(self):
        self.newAction = QAction(
            QIcon('resources/icons/new.png'), '&New', self.window,
            shortcut=QKeySequence.New,
            statusTip='Create a New Project',
            triggered=self.logic.newProject)

        self.openAction = QAction(
            QIcon('resources/icons/open.png'), '&Open', self.window,
            shortcut=QKeySequence.Open,
            statusTip='Open a project in editor',
            triggered=self.logic.openProject)

        self.saveAction = QAction(
            QIcon('resources/icons/save.png'), '&Save', self.window,
            shortcut=QKeySequence.Save,
            statusTip='Save a project',
            triggered=self.logic.saveProject)

        self.saveAsAction = QAction(
            QIcon('resources/icons/save_as.png'), 'Save As...', self.window,
            shortcut=QKeySequence.SaveAs,
            statusTip='Save a project',
            triggered=self.logic.saveProjectAs)

        self.closeAction = QAction(
            QIcon('resources/icons/close.png'), '&Close', self.window,
            shortcut=QKeySequence.Close,
            statusTip='Close current project',
            triggered=self.logic.closeProject)

        self.exitAction = QAction(
            QIcon('resources/icons/exit.png'), '&Quit', self.window,
            shortcut=QKeySequence.Quit,
            statusTip='Quit the Application',
            triggered=self.logic.exitApp)

        self.copyAction = QAction(
            QIcon('resources/icons/copy.png'), 'C&opy', self.window,
            shortcut='Ctrl+C',
            statusTip='Copy',
            triggered=self.logic.copy)

        self.pasteAction = QAction(
            QIcon('resources/icons/paste.png'), '&Paste', self.window,
            shortcut='Ctrl+V',
            statusTip='Paste',
            triggered=self.logic.paste)

        self.aboutAction = QAction(
            QIcon('resources/icons/about.png'), 'A&bout', self.window,
            statusTip='Displays info about the app',
            triggered=self.logic.aboutHelp)

        self.addRectangleAction = QAction(
            QIcon('resources/icons/rectangle.png'), '&Rectangle', self.window,
            statusTip='Add rectangle',
            triggered=self.logic.addRectangle)

        self.addUserElementAction = QAction(
            QIcon('resources/icons/user_element.svg'), '&User element', self.window,
            statusTip='Add user element',
            triggered=self.logic.addUserElement)

        self.addLineElementAction = QAction(
            QIcon('resources/icons/line_element.png'), '&Line element', self.window,
            statusTip='Add line element',
            triggered=self.logic.addLineElement)

        self.printElementsAction = QAction(
            QIcon('resources/icons/cache.png'), 'Print', self.window,
            statusTip='print',
            triggered=self.logic.printElements)

        self.createDiagramAction = QAction(
            QIcon('resources/icons/diagram.png'), 'Create diagram', self.window,
            statusTip='Create diagram',
            triggered=self.logic.createDiagram)

        self.createFolderAction = QAction(
            QIcon('resources/icons/create_folder.png'), 'Create folder', self.window,
            statusTip='Create folder',
            triggered=self.logic.createFolder)

        self.deleteElementAction = QAction(
            QIcon('resources/icons/delete.png'), 'Delete element', self.window,
            shortcut=QKeySequence.Delete,
            statusTip='Delete element',
            triggered=self.logic.deleteElement)

        self.sceneAction1 = QAction(
            QIcon('resources/icons/miscellaneous.png'), 'Action1', self.window,
            statusTip='Action1',
            triggered=self.logic.do_action1)

        self.sceneAction2 = QAction(
            QIcon('resources/icons/miscellaneous.png'), 'Action2', self.window,
            statusTip='Action2',
            triggered=self.logic.do_action2)

        self.sceneAction3 = QAction(
            QIcon('resources/icons/miscellaneous.png'), 'Action3', self.window,
            statusTip='Action3',
            triggered=self.logic.do_action3)
