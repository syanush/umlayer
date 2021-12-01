#!/usr/bin/env python3

import logging
import sys
import traceback

from umlayer import version
from umlayer import model, gui, storage


def run_application():
    """Construct and run the UMLayer application
    """

    logging.basicConfig(filename='umlayer.log', filemode='w', level=logging.INFO)
    logging.info(f'UMLayer {version.__version__}')

    app = gui.UMLayerApplication(sys.argv)
    # app.setStyle('Fusion')

    logging.info('Application started')

    store = storage.ProjectStorageImpl()
    gui_logic = gui.GuiLogic()
    scene_logic = gui.SceneLogic()
    main_window = gui.MainWindow(gui_logic, scene_logic, store)
    app.setActiveWindow(main_window)
    main_window.show()

    logging.info('Main window displayed')

    result_code = app.exec()
    main_window = None
    app = None

    logging.info('Application finished')

    return result_code


def main():
    """Start function
    """

    try:
        errcode = run_application()
    except SystemExit:
        errcode = 0
    except Exception as ex:
        logging.exception(traceback.format_exc())
        errcode = 1
        raise ex  # TODO: comment it in release version

    sys.exit(errcode)


if __name__ == '__main__':
    main()
