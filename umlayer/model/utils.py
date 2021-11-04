from .constants import *


def build_window_title(filename: str, is_dirty: bool):
    title = 'UMLayer'

    if filename:
        if len(filename) >= 4 and filename.endswith(EXTENSION):
            filename = filename[:-4]

        star = ' *' if is_dirty else ''
        title = f'{filename}{star} \u2014 ' + title

    return title
