from enum import Enum


class Color(Enum):
    WHITE = '\033[1;37m'
    BLUE = '\033[1;34m'
    GREEN = '\033[1;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    PURPLE = '\033[1;35m'
    CYAN = '\033[1;36m'
    BLACK = '\033[1;30m'
    GRAY = '\033[1;37m'
    MARKER = '\033[1;39m'
    RESET = '\033[0m'


NUM_TO_COLOR = {i: color for i, color in enumerate(Color)}


def print_chr(c: chr, color: Color):
    print(f'{color.value}{c}{Color.RESET.value}', end=' ')


def print_num(num: int, color = None):
    if color is None:
        color = NUM_TO_COLOR[num]
    print(f'{color.value}{num}{Color.RESET.value}', end=' ')