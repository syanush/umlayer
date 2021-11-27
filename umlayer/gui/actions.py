from PySide6.QtGui import *


class Actions:
    def __init__(self, window):
        self.window = window
        self.createActions()

    def createActions(self):
        self.newAction = QAction(
            icon=QIcon('resources/icons/new.png'),
            text='&New',
            parent=self.window,
            shortcut=QKeySequence.New,
            statusTip='Create a New Project',
            triggered=self.window.logic.newProject)

        self.openAction = QAction(
            QIcon('resources/icons/open.png'), '&Open', self.window,
            shortcut=QKeySequence.Open,
            statusTip='Open a project in editor',
            triggered=self.window.logic.openProject)

        self.saveAction = QAction(
            QIcon('resources/icons/save.png'), '&Save', self.window,
            shortcut=QKeySequence.Save,
            statusTip='Save a project',
            triggered=self.window.logic.saveProject)

        self.saveAsAction = QAction(
            QIcon('resources/icons/save_as.png'), 'Save As...', self.window,
            shortcut=QKeySequence.SaveAs,
            statusTip='Save a project',
            triggered=self.window.logic.saveProjectAs)

        self.closeAction = QAction(
            QIcon('resources/icons/close.png'), '&Close', self.window,
            shortcut=QKeySequence.Close,
            statusTip='Close current project',
            triggered=self.window.logic.closeProject)

        self.exitAction = QAction(
            QIcon('resources/icons/exit.png'), '&Quit', self.window,
            shortcut=QKeySequence.Quit,
            statusTip='Quit the Application',
            triggered=self.window.logic.exitApp)

        # self.deleteAction = QAction(
        #     QIcon('resources/icons/delete.png'), '&Delete', self.window,
        #     shortcut="Delete",
        #     statusTip="Delete",
        #     triggered=self.logic.delete)

        # self.cutAction = QAction(
        #     QIcon('resources/icons/cut.png'), 'Cut', self.window,
        #     shortcut='Ctrl+X',
        #     statusTip='Cut (Ctrl-X)',
        #     triggered=self.logic.cut)

        # self.copyAction = QAction(
        #     QIcon('resources/icons/copy.png'), 'C&opy', self.window,
        #     shortcut='Ctrl+C',
        #     statusTip='Copy (Ctrl-C)',
        #     triggered=self.logic.copy)

        # self.pasteAction = QAction(
        #     QIcon('resources/icons/paste.png'), '&Paste', self.window,
        #     shortcut='Ctrl+V',
        #     statusTip='Paste (Ctrl-V)',
        #     triggered=self.logic.paste)

        self.aboutAction = QAction(
            QIcon('resources/icons/about.png'), 'A&bout', self.window,
            statusTip='Displays info about the app',
            triggered=self.window.logic.aboutWindow)

        self.printElementsAction = QAction(
            QIcon('resources/icons/cache.png'), 'Print', self.window,
            statusTip='print',
            triggered=self.window.project.printProjectItems)

        self.printSceneElementsAction = QAction(
            QIcon('resources/icons/cache.png'), 'Print', self.window,
            statusTip='print scene elements',
            triggered=self.window.scene.printItems)

        self.createDiagramAction = QAction(
            QIcon('resources/icons/diagram.png'), 'Create diagram', self.window,
            statusTip='Create diagram',
            triggered=self.window.logic.createDiagram)

        self.createFolderAction = QAction(
            QIcon('resources/icons/create_folder.png'), 'Create folder', self.window,
            statusTip='Create folder',
            triggered=self.window.logic.createFolder)

        self.deleteProjectItemAction = QAction(
            QIcon('resources/icons/delete.png'), 'Delete project item', self.window,
            shortcut=QKeySequence.Delete,
            statusTip='Delete project item',
            triggered=self.window.logic.deleteSelectedItem)

        self.addActorElementAction = QAction(
            QIcon('resources/icons/user_element.svg'), 'Actor', self.window,
            statusTip='Add actor',
            triggered=self.window.scene_logic.addActorElement)

        self.addEllipseElementAction = QAction(
            QIcon('resources/icons/ellipse.png'), 'Ellipse', self.window,
            statusTip='Add ellipse',
            triggered=self.window.scene_logic.addEllipseElement)

        self.addLineElementAction = QAction(
            QIcon('resources/icons/simple_line.png'), 'Line', self.window,
            statusTip='Add line',
            triggered=self.window.scene_logic.addLineElement)

        self.addRelationshipElementAction = QAction(
            QIcon('resources/icons/arrow_triangle.png'), 'Relationship', self.window,
            statusTip='Add relationship',
            triggered=self.window.scene_logic.addLineElement)

        self.addTextElementAction = QAction(
            QIcon('resources/icons/left_text.png'), 'Text', self.window,
            statusTip='Add text',
            triggered=self.window.scene_logic.addTextElement)

        self.addCenteredTextElementAction = QAction(
            QIcon('resources/icons/center_text.png'), 'Centered text', self.window,
            statusTip='Add centered text',
            triggered=self.window.scene_logic.addCenteredTextElement)

        self.addNoteElementAction = QAction(
            QIcon('resources/icons/note.png'), 'Note', self.window,
            statusTip='Add note',
            triggered=self.window.scene_logic.addNoteElement)

        self.addPackageElementAction = QAction(
            QIcon('resources/icons/package.png'), 'Package', self.window,
            statusTip='Add package',
            triggered=self.window.scene_logic.addPackageElement)

        self.addSimpleClassElementAction = QAction(
            QIcon('resources/icons/simple_class.png'), 'Simple class', self.window,
            statusTip='Add simple class',
            triggered=self.window.scene_logic.addSimpleClassElement)

        self.addFatClassElementAction = QAction(
            QIcon('resources/icons/class_icon.png'), 'Fat class', self.window,
            statusTip='Add class',
            triggered=self.window.scene_logic.addFatClassElement)

        self.addHandleItemAction = QAction(
            QIcon('resources/icons/miscellaneous.png'), '', self.window,
            statusTip='Add handle',
            triggered=self.window.scene_logic.addHandleItem)

        self.exportAsRasterImageAction = QAction(
            text='Export as raster image...',
            parent=self.window,
            statusTip='Export as raster image...',
            triggered=self.window.logic.exportAsRasterImageHandler)

        self.exportAsSvgImageAction = QAction(
            text='Export as SVG image...',
            parent=self.window,
            statusTip='Export as SVG image...',
            triggered=self.window.logic.exportAsSvgImageHandler)

    def enableSceneActions(self, enable):
        self.addActorElementAction.setEnabled(enable)
        self.addEllipseElementAction.setEnabled(enable)
        self.addLineElementAction.setEnabled(enable)
        self.addRelationshipElementAction.setEnabled(enable)
        self.addTextElementAction.setEnabled(enable)
        self.addCenteredTextElementAction.setEnabled(enable)
        self.addNoteElementAction.setEnabled(enable)
        self.addSimpleClassElementAction.setEnabled(enable)
        self.addFatClassElementAction.setEnabled(enable)
        self.addPackageElementAction.setEnabled(enable)
        self.exportAsSvgImageAction.setEnabled(enable)
        self.exportAsRasterImageAction.setEnabled(enable)
