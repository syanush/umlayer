import os

from . import constants


def icon_path(filename: str) -> str:
    return os.path.join('resources/icons', filename)


def build_window_title(filename: str, is_dirty: bool):
    title = 'UMLayer'

    if filename:
        if len(filename) >= 4 and filename.endswith(constants.EXTENSION):
            filename = filename[:-4]

        star = ' *' if is_dirty else ''
        title = f'{filename}{star} \u2014 ' + title

    return title
