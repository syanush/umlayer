from umlayer import model


class SaveInteractor:
    """Save and Save As operations"""

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

    def saveProject(self):
        if self._project is None:
            return

        if self._isFileNameNotSet():
            filename = self._window.getFileNameFromSaveDialog('Save')
        else:
            filename = self._filename

        if len(filename) == 0:
            return

        try:
            self._window.doSaveProject(filename)
        except Exception as ex:
            raise ex
        else:
            self._data_model.set_filename(filename)
            self._window.updateTitle()

    def saveProjectAs(self):
        if self._project is None:
            return

        filename = self._window.getFileNameFromSaveDialog('Save as...')

        if len(filename) == 0:
            return

        try:
            self._window.doSaveProject(filename)
        except Exception as ex:
            raise ex
        else:
            self._data_model.set_filename(filename)
            self._window.updateTitle()

    def _isFileNameNotSet(self) -> bool:
        return self._filename is None or self._filename == model.constants.DEFAULT_FILENAME
