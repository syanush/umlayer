import sys

from umlayer import model
from umlayer import gui
from umlayer import storage
from umlayer import usecases


class CompositionRoot:
    """Creates concrete realizations and wires the application up"""

    def compose(self) -> None:
        """The object graph is constructed here"""

        self._app = gui.UMLayerApplication(sys.argv)

        data_model = model.DataModel()
        project_storage = storage.ProjectStorageImpl()

        project_interactor = usecases.ProjectInteractor(data_model, project_storage)
        interactors = usecases.Interactors(data_model, project_interactor)

        scene_logic = gui.SceneLogic()
        self._main_window = gui.MainWindow(scene_logic, data_model, interactors)
        interactors.set_window(self._main_window)

    @property
    def main_window(self):
        return self._main_window

    @property
    def app(self):
        return self._app
