from PySide6.QtGui import *


class Actions:
    def __init__(self, window):
        self.window = window
        self.createActions()

        self.toggleGridAction.triggered[bool].connect(self.window.scene_logic.toggleGrid)

    def createActions(self):
        self.newAction = QAction(
            icon=QIcon('icons:new.png'),
            text='&New',
            parent=self.window,
            shortcut=QKeySequence.New,
            statusTip='Create new project',
            triggered=self.window.recreateProject)

        self.openAction = QAction(
            QIcon('icons:open.png'), '&Open', self.window,
            shortcut=QKeySequence.Open,
            statusTip='Open project',
            triggered=self.window.logic.openProject)

        self.saveAction = QAction(
            QIcon('icons:save.png'), '&Save', self.window,
            shortcut=QKeySequence.Save,
            statusTip='Save project',
            triggered=self.window.logic.saveProject)

        self.saveAsAction = QAction(
            QIcon('icons:save_as.png'), 'Save As...', self.window,
            shortcut=QKeySequence.SaveAs,
            statusTip='Save project as...',
            triggered=self.window.logic.saveProjectAs)

        self.closeAction = QAction(
            QIcon('icons:close.png'), '&Close', self.window,
            shortcut=QKeySequence.Close,
            statusTip='Close project',
            triggered=self.window.closeProject)

        self.exitAction = QAction(
            QIcon('icons:exit.png'), '&Quit', self.window,
            shortcut=QKeySequence.Quit,
            statusTip='Quit the application',
            triggered=self.window.logic.exitApp)

        self.toggleGridAction = QAction(
            icon=QIcon('icons:grid.png'),
            text='Toggle grid',
            statusTip='Toggle grid',
            parent=None,
            checkable=True)

        self.deleteAction = QAction(
            icon=QIcon('icons:delete.png'),
            text='&Delete',
            shortcut="Delete",
            statusTip="Delete",
            parent=self.window.sceneView,
            triggered=self.window.scene_logic.delete_selected_elements)

        self.cutAction = QAction(
            icon=QIcon('icons:cut.png'),
            text='Cut',
            statusTip='Cut (Ctrl-X)',
            shortcut=QKeySequence.Cut,
            parent=self.window.sceneView,
            triggered=self.window.scene_logic.cut_selected_elements)

        self.copyAction = QAction(
            icon=QIcon('icons:copy.png'),
            text='C&opy',
            shortcut=QKeySequence.Copy,
            statusTip='Copy (Ctrl-C)',
            parent=self.window.sceneView,
            triggered=self.window.scene_logic.copy_selected_elements)

        self.pasteAction = QAction(
            icon=QIcon('icons:paste.png'),
            text='&Paste',
            shortcut=QKeySequence.Paste,
            statusTip='Paste (Ctrl-V)',
            parent=self.window.sceneView,
            triggered=self.window.scene_logic.paste_elements)

        self.aboutAction = QAction(
            QIcon('icons:about.png'), 'A&bout', self.window,
            statusTip='Displays info about the app',
            triggered=self.window.logic.aboutWindow)

        self.createDiagramAction = QAction(
            QIcon('icons:diagram.png'), 'Create diagram', self.window,
            statusTip='Create diagram',
            triggered=self.window.logic.createDiagram)

        self.createFolderAction = QAction(
            QIcon('icons:create_folder.png'), 'Create folder', self.window,
            statusTip='Create folder',
            triggered=self.window.logic.createFolder)

        self.deleteProjectItemAction = QAction(
            QIcon('icons:delete.png'), 'Delete project item', self.window,
            shortcut=QKeySequence.Delete,
            statusTip='Delete project item',
            triggered=self.window.logic.deleteSelectedItem)

        self.addActorElementAction = QAction(
            QIcon('icons:user_element.svg'), 'Actor', self.window,
            statusTip='Add actor',
            triggered=self.window.scene_logic.addActorElement)

        self.addEllipseElementAction = QAction(
            QIcon('icons:ellipse.png'), 'Ellipse', self.window,
            statusTip='Add ellipse',
            triggered=self.window.scene_logic.addEllipseElement)

        self.addLineElementAction = QAction(
            QIcon('icons:simple_line.png'), 'Line', self.window,
            statusTip='Add line',
            triggered=self.window.scene_logic.addLineElement)

        self.addRelationshipElementAction = QAction(
            QIcon('icons:arrow_triangle.png'), 'Relationship', self.window,
            statusTip='Add relationship',
            triggered=self.window.scene_logic.addLineElement)

        self.addTextElementAction = QAction(
            QIcon('icons:left_text.png'), 'Text', self.window,
            statusTip='Add text',
            triggered=self.window.scene_logic.addTextElement)

        self.addCenteredTextElementAction = QAction(
            QIcon('icons:center_text.png'), 'Centered text', self.window,
            statusTip='Add centered text',
            triggered=self.window.scene_logic.addCenteredTextElement)

        self.addNoteElementAction = QAction(
            QIcon('icons:note.png'), 'Note', self.window,
            statusTip='Add note',
            triggered=self.window.scene_logic.addNoteElement)

        self.addPackageElementAction = QAction(
            QIcon('icons:package.png'), 'Package', self.window,
            statusTip='Add package',
            triggered=self.window.scene_logic.addPackageElement)

        self.addSimpleClassElementAction = QAction(
            QIcon('icons:simple_class.png'), 'Simple class', self.window,
            statusTip='Add simple class',
            triggered=self.window.scene_logic.addSimpleClassElement)

        self.addFatClassElementAction = QAction(
            QIcon('icons:class_icon.png'), 'Fat class', self.window,
            statusTip='Add class',
            triggered=self.window.scene_logic.addFatClassElement)

        self.addHandleItemAction = QAction(
            QIcon('icons:miscellaneous.png'), '', self.window,
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
