import os

from . import constants


def build_window_title(filename: str, is_dirty: bool):
    title = 'UMLayer'

    if filename:
        if len(filename) >= 4 and filename.endswith(constants.EXTENSION):
            filename = filename[:-4]

        star = ' *' if is_dirty else ''
        title = f'{filename}{star} \u2014 ' + title

    return title


def is_empty(seq):
    return seq is None or len(seq) == 0
