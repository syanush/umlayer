import logging

from umlayer import model


class ProjectInteractor:
    """Project operations"""

    def __init__(self, data_model: model.DataModel):
        self._data_model = data_model
        self._window = None

    @property
    def _project(self):
        return self._data_model.project

    @property
    def _filename(self):
        return self._data_model.filename

    def set_window(self, window):
        self._window = window

    def is_dirty(self):
        return False if self._project is None else self._project.dirty()

    def open_project(self):
        if not self.close_project():
            return

        filename = self._window.getFileNameFromOpenDialog('Open')

        if len(filename) == 0:
            return

        try:
            # raise Exception  # for debugging
            self._window.doOpenProject(filename)
        except Exception as ex:
            logging.error(ex)
            print(ex)
            self._window.criticalError('Unable to open project!')
        else:
            self._data_model.set_filename(filename)
            self._window.updateTitle()

    def save_project(self) -> bool:
        if self._project is None:
            return True

        if self._isFileNameNotSet():
            filename = self._window.getFileNameFromSaveDialog('Save')
        else:
            filename = self._filename

        if len(filename) == 0:
            return False

        try:
            self._window.doSaveProject(filename)
        except Exception as ex:
            logging.error(ex)
            print(ex)
            self._window.criticalError('Unable to save project!')
            return False
        else:
            self._data_model.set_filename(filename)
            self._window.updateTitle()
        return True

    def save_project_as(self):
        if self._project is None:
            return

        filename = self._window.getFileNameFromSaveDialog('Save as...')

        if len(filename) == 0:
            return

        try:
            self._window.doSaveProject(filename)
        except Exception as ex:
            logging.error(ex)
            print(ex)
            self._window.criticalError('Unable to save project!')
        else:
            self._data_model.set_filename(filename)
            self._window.updateTitle()

    def close_project(self) -> bool:
        if not self._saveFileIfNeeded():
            return False

        self._window.clearScene()
        self._data_model.delete_project()
        self._data_model.set_filename(None)
        self._window.updateTitle()
        return True

    def _isFileNameNotSet(self) -> bool:
        return self._filename is None or self._filename == model.constants.DEFAULT_FILENAME

    def _saveFileIfNeeded(self) -> bool:
        if not self._window.isDirty():
            return True

        reply = self._window.askToSaveModifiedFile()

        if reply == model.constants.SAVE:
            if not self.save_project():
                return False

        return reply != model.constants.CANCEL
