import math

from . import Settings


def snap(x: float) -> float:
    return math.floor(x / Settings.BLOCK_SIZE) * Settings.BLOCK_SIZE


def snap_up(x: float) -> float:
    return math.ceil(x / Settings.BLOCK_SIZE) * Settings.BLOCK_SIZE


def snap_round(x: float) -> float:
    return round(x / Settings.BLOCK_SIZE) * Settings.BLOCK_SIZE


def split_to_sections(text) -> list[str]:
    """ "Return the list of text sections.

    The separator of the sections is '--\n' line in the original text
    """
    lines = text.split("\n")
    sections = []
    section_lines = []
    for line in lines:
        if line == "--":
            section = "\n".join(section_lines)
            sections.append(section)
            section_lines.clear()
        else:
            section_lines.append(line)
    section = "\n".join(section_lines)
    sections.append(section)
    section_lines.clear()
    return sections

    # print(parseText('--')) # 2
    # print(parseText('--\n')) # 2
    # print(parseText('--\n--')) # 3
    # print(parseText('--\n--\n')) # 3


def split_to_two_sections(text: str) -> list[str]:
    sections = split_to_sections(text)
    text1 = sections[0]
    text2 = "\n--\n".join(sections[1:]) if len(sections) > 1 else ""
    return [text1, text2]
