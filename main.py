import logging
import sys
import time
import traceback

from PySide6.QtCore import QCoreApplication

from umlayer import model, gui, storage


def run_application():
    """Construct and run the UMLayer application
    """

    logging.basicConfig(filename='umlayer.log', filemode='w', level=logging.INFO)
    logging.info('Application started')

    app = gui.UMLayerApplication(sys.argv)

    store = storage.ProjectStorageImpl()
    project_logic = model.ProjectLogic(store)
    main_window = gui.MainWindow(project_logic)
    app.setActiveWindow(main_window)
    main_window.show()

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
