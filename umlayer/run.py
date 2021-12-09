#!/usr/bin/env python3

import logging
import os
import sys
import traceback

from PySide6.QtWidgets import QApplication, QMainWindow


def run():
    """Construct and run the UMLayer application"""
    from composition_root import CompositionRoot

    init_logging()

    from umlayer import version
    logging.info("")
    logging.info(f"UMLayer {version.__version__}")

    logging.info("Application started")
    composer = CompositionRoot()
    composer.compose()
    app = composer.app
    main_window = composer.main_window
    del composer

    # app.setStyle('Fusion')
    main_window.initialize()
    app.setActiveWindow(main_window)
    main_window.show()
    logging.info("Main window displayed")
    del main_window

    result_code = app.exec()
    logging.info("Application finished")
    del app

    return result_code


def init_logging():
    log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("umlayer.log")
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)  # sys.stderr (default), sys.stdout
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)


def main():
    """Start function"""

    try:
        errcode = run()
    except SystemExit:
        errcode = 0
    except Exception as ex:
        logging.exception(traceback.format_exc())
        errcode = 1
        raise ex  # TODO: comment this in release version

    sys.exit(errcode)


if __name__ == "__main__":
    sys.path.append(os.path.join(sys.path[0], ".."))
    main()
