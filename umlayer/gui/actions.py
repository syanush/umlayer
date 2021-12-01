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
            statusTip='Create new project',
            parent=self.window,
            shortcut=QKeySequence.New,
            triggered=self.window.recreateProject)

        self.openAction = QAction(
            icon=QIcon('icons:open.png'),
            text='&Open',
            statusTip='Open project',
            parent=self.window,
            shortcut=QKeySequence.Open,
            triggered=self.window.logic.openProject)

        self.saveAction = QAction(
            icon=QIcon('icons:save.png'),
            text='&Save',
            statusTip='Save project',
            parent=self.window,
            shortcut=QKeySequence.Save,
            triggered=self.window.logic.saveProject)

        self.saveAsAction = QAction(
            icon=QIcon('icons:save_as.png'),
            text='Save As...',
            statusTip='Save project as...',
            parent=self.window,
            shortcut=QKeySequence.SaveAs,
            triggered=self.window.logic.saveProjectAs)

        self.closeAction = QAction(
            icon=QIcon('icons:close.png'),
            text='&Close',
            statusTip='Close project',
            parent=self.window,
            shortcut=QKeySequence.Close,
            triggered=self.window.closeProject)

        self.exportAsRasterImageAction = QAction(
            text='Export as raster image...',
            statusTip='Export as raster image...',
            parent=self.window,
            triggered=self.window.logic.exportAsRasterImageHandler)

        self.exportAsSvgImageAction = QAction(
            text='Export as SVG image...',
            statusTip='Export as SVG image...',
            parent=self.window,
            triggered=self.window.logic.exportAsSvgImageHandler)

        self.aboutAction = QAction(
            icon=QIcon('icons:about.png'),
            text='A&bout',
            statusTip='Displays info about the app',
            parent=self.window,
            triggered=self.window.logic.aboutWindow)

        self.aboutQtAction = QAction(
            icon=QIcon('icons:qt.png'),
            text='About Qt',
            statusTip='Displays info about Qt',
            parent=self.window,
            triggered=self.window.logic.aboutQtWindow)

        self.exitAction = QAction(
            icon=QIcon('icons:exit.png'),
            text='&Quit',
            statusTip='Quit the application',
            parent=self.window,
            shortcut=QKeySequence.Quit,
            triggered=self.window.logic.exitApp)

        self.createDiagramAction = QAction(
            icon=QIcon('icons:diagram.png'),
            text='Create diagram',
            statusTip='Create diagram',
            parent=self.window.treeView,
            triggered=self.window.logic.createDiagram)

        self.createFolderAction = QAction(
            icon=QIcon('icons:create_folder.png'),
            text='Create folder',
            statusTip='Create folder',
            parent=self.window.treeView,
            triggered=self.window.logic.createFolder)

        self.deleteProjectItemAction = QAction(
            icon=QIcon('icons:delete.png'),
            text='Delete project item',
            shortcut=QKeySequence.Delete,
            parent=self.window.treeView,
            statusTip='Delete project item',
            triggered=self.window.logic.deleteSelectedItem)

        self.toggleGridAction = QAction(
            icon=QIcon('icons:grid.png'),
            text='Toggle grid',
            statusTip='Toggle grid',
            parent=self.window.sceneView,
            checkable=True)

        self.deleteAction = QAction(
            icon=QIcon('icons:delete.png'),
            text='&Delete',
            statusTip="Delete",
            shortcut=QKeySequence.Delete,
            parent=self.window.sceneView,
            triggered=self.window.scene_logic.delete_selected_elements)

        self.selectAllElementsAction = QAction(
            text='Select all elements',
            statusTip='Select all elements',
            shortcut=QKeySequence.SelectAll,
            parent=self.window.sceneView,
            triggered=self.window.scene_logic.selectAllElements)

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
            statusTip='Copy (Ctrl-C)',
            parent=self.window.sceneView,
            shortcut=QKeySequence.Copy,
            triggered=self.window.scene_logic.copy_selected_elements)

        self.pasteAction = QAction(
            icon=QIcon('icons:paste.png'),
            text='&Paste',
            statusTip='Paste (Ctrl-V)',
            parent=self.window.sceneView,
            shortcut=QKeySequence.Paste,
            triggered=self.window.scene_logic.paste_elements)

        self.addActorElementAction = QAction(
            icon=QIcon('icons:user_element.svg'),
            text='Actor',
            statusTip='Add actor',
            parent=self.window.sceneView,
            triggered=self.window.scene_logic.addActorElement)

        self.addEllipseElementAction = QAction(
            icon=QIcon('icons:ellipse.png'),
            text='Ellipse',
            statusTip='Add ellipse',
            parent=self.window.sceneView,
            triggered=self.window.scene_logic.addEllipseElement)

        self.addTextElementAction = QAction(
            icon=QIcon('icons:left_text.png'),
            text='Text',
            statusTip='Add text',
            parent=self.window.sceneView,
            triggered=self.window.scene_logic.addTextElement)

        self.addCenteredTextElementAction = QAction(
            icon=QIcon('icons:center_text.png'),
            text='Centered text',
            statusTip='Add centered text',
            parent=self.window.sceneView,
            triggered=self.window.scene_logic.addCenteredTextElement)

        self.addNoteElementAction = QAction(
            icon=QIcon('icons:note.png'),
            text='Note',
            statusTip='Add note',
            parent=self.window.sceneView,
            triggered=self.window.scene_logic.addNoteElement)

        self.addSimpleClassElementAction = QAction(
            icon=QIcon('icons:simple_class.png'),
            text='Simple class',
            parent=self.window.sceneView,
            statusTip='Add simple class',
            triggered=self.window.scene_logic.addSimpleClassElement)

        self.addFatClassElementAction = QAction(
            icon=QIcon('icons:class_icon.png'),
            text='Fat class',
            parent=self.window.sceneView,
            statusTip='Add class',
            triggered=self.window.scene_logic.addFatClassElement)

        self.addPackageElementAction = QAction(
            icon=QIcon('icons:package.png'),
            text='Package',
            statusTip='Add package',
            parent=self.window.sceneView,
            triggered=self.window.scene_logic.addPackageElement)

        self.bringToFrontAction = QAction(
            icon=QIcon('icons:bring_to_front.png'),
            text='Bring to &Front',
            statusTip='Bring item to front',
            parent=self.window.sceneView,
            shortcut='Ctrl+F',
            triggered=self.window.scene_logic.bring_to_front)

        self.sendToBackAction = QAction(
            icon=QIcon('icons:send_to_back.png'),
            text='Send to &Back',
            statusTip='Send item to back',
            parent=self.window.sceneView,
            shortcut='Ctrl+B',
            triggered=self.window.scene_logic.send_to_back)

    def enableSceneActions(self, enable):
        self.exportAsSvgImageAction.setEnabled(enable)
        self.exportAsRasterImageAction.setEnabled(enable)

        self.cutAction.setEnabled(enable)
        self.copyAction.setEnabled(enable)
        self.pasteAction.setEnabled(enable)
        self.deleteAction.setEnabled(enable)

        self.toggleGridAction.setEnabled(enable)
        self.bringToFrontAction.setEnabled(enable)
        self.sendToBackAction.setEnabled(enable)

        self.addActorElementAction.setEnabled(enable)
        self.addEllipseElementAction.setEnabled(enable)
        self.addTextElementAction.setEnabled(enable)
        self.addCenteredTextElementAction.setEnabled(enable)
        self.addNoteElementAction.setEnabled(enable)
        self.addSimpleClassElementAction.setEnabled(enable)
        self.addFatClassElementAction.setEnabled(enable)
        self.addPackageElementAction.setEnabled(enable)

        self.window.setSceneWidgetsEnabled(enable)
