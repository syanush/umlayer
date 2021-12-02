#!/usr/bin/env python3

import logging
import sys
import traceback

from umlayer import version
from umlayer import model, gui, storage
from .composition_root import CompositionRoot


def init_logging():
    logging.basicConfig(filename='umlayer.log', filemode='w', level=logging.INFO)
    logging.info(f'UMLayer {version.__version__}')


def run():
    """Construct and run the UMLayer application
    """
    init_logging()

    logging.info('Application started')
    composer = CompositionRoot()
    composer.compose()
    app: QApplication = composer.app
    main_window: QMainWindow = composer.main_window
    del composer

    # app.setStyle('Fusion')
    main_window.initialize()
    app.setActiveWindow(main_window)
    main_window.show()
    logging.info('Main window displayed')
    del main_window

    result_code = app.exec()
    logging.info('Application finished')
    del app

    return result_code


def main():
    """Start function
    """

    try:
        errcode = run()
    except SystemExit:
        errcode = 0
    except Exception as ex:
        logging.exception(traceback.format_exc())
        errcode = 1
        raise ex  # TODO: comment it in release version

    sys.exit(errcode)


if __name__ == '__main__':
    main()
