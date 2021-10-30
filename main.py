import logging
import sys
import time
import traceback

from PySide6.QtCore import QCoreApplication

from umlayer.gui.app import UMLayerApplication
from umlayer.gui.mainwindow import MainWindow
from umlayer.model.project_logic import ProjectLogic
from umlayer.storage.project_storage_impl import ProjectStorageImpl


def run_application():
    """Construct and run the UMLayer application
    """

    logging.basicConfig(filename='umlayer.log', filemode='w', level=logging.INFO)
    logging.info('Application started')

    app = UMLayerApplication(sys.argv)

    storage = ProjectStorageImpl()
    project_logic = ProjectLogic(storage)
    main_window = MainWindow(project_logic)
    app.setActiveWindow(main_window)

    # Pretend that a file download is in progress
    QCoreApplication.processEvents()
    filedownload = 0
    while (filedownload <= 100):
        main_window.showProgress(filedownload)
        QCoreApplication.processEvents()
        filedownload = filedownload + 20
        time.sleep(0.2)
    QCoreApplication.processEvents()

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
    except Exception:
        logging.exception(traceback.format_exc())
        errcode = 1

    sys.exit(errcode)


if __name__ == '__main__':
    main()
