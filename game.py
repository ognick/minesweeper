import random
from enum import Enum
from functools import lru_cache


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


class Field(object):
    BOMB = -1
    UNKNOWN = -2
    MARKER = -3
    BOOM = -4

    def __init__(self, height: int, width: int):
        self.num_mines = None
        self.unknown_fields = width * height
        self._f = [[Field.UNKNOWN for _ in range(width)] for _ in range(height)]

    def generate(self, num_mines: int) -> tuple[int, int]:
        self.num_mines = num_mines
        width, height = self.get_size()

        init_x, init_y = self.get_rnd_point()
        self.set(init_x, init_y, 0)
        for x, y, _ in self.get_neighbors(init_x, init_y):
            self.set(x, y, 0)

        mines_placed = 0
        while mines_placed < num_mines:
            x, y = self.get_rnd_point()
            if self._f[y][x] == Field.UNKNOWN:
                self._f[y][x] = Field.BOMB
                mines_placed += 1

        for y in range(height):
            for x in range(width):
                if self._f[y][x] != Field.BOMB:
                    self._f[y][x] = self.get_mines_count_around(x, y)

        return init_x, init_y

    @lru_cache
    def can_get(self, x: int, y: int) -> bool:
        width, height = self.get_size()
        if y < 0 or y > height - 1:
            return False
        if x < 0 or x > width - 1:
            return False
        return True

    def get(self, x: int, y: int) -> int:
        return self._f[y][x]

    def set(self, x: int, y: int, num: int):
        self._f[y][x] = num

    @lru_cache
    def get_size(self) -> tuple[int, int]:
        height = len(self._f)
        width = len(self._f[0])
        return width, height

    def get_neighbors(self, x, y) -> list[tuple[int, int, int]]:
        result = []
        width, height = self.get_size()
        for yy in range(max(0, y - 1), min(height, y + 2)):
            for xx in range(max(0, x - 1), min(width, x + 2)):
                if yy != y or xx != x:
                    result.append((xx, yy, self._f[yy][xx]))
        return result

    def get_mines_count_around(self, x, y) -> int:
        return sum(1 for _, _, num in self.get_neighbors(x, y) if num == Field.BOMB)

    def get_rnd_point(self) -> tuple[int, int]:
        width, height = self.get_size()
        y = random.randint(0, height - 1)
        x = random.randint(0, width - 1)
        return x, y

    def print(self):
        for line in self._f:
            for num in line:
                if num == Field.MARKER:
                    print_chr('\u2691', Color.MARKER)
                elif num == 0:
                    print_chr('0', Color.BLACK)
                elif num == Field.BOMB:
                    print_chr('\u2623', Color.MARKER)
                elif num == Field.BOOM:
                    print_chr('\u2623', Color.RED)
                elif num == Field.UNKNOWN:
                    print_chr('?', Color.GRAY)
                else:
                    print_num(num)
            print()
        print()


class Game(object):
    def __init__(self, height: int, width: int, num_mines: int):
        self.__secret_field = secret_field = Field(height, width)
        init_x, init_y = secret_field.generate(num_mines)
        self.field = Field(height, width)
        self.open(init_x, init_y)

    def __rec_open(self, x, y) -> int:
        count = 0
        if self.field.get(x, y) != Field.UNKNOWN:
            return count

        if self.__secret_field.get(x, y) == Field.BOMB:
            return count

        num = self.__secret_field.get(x, y)
        self.field.set(x, y, num)
        count += 1
        if num == 0:
            for xx, yy, num in self.field.get_neighbors(x, y):
                if num == Field.UNKNOWN:
                    count += self.__rec_open(xx, yy)
        return count

    def mark(self, x, y):
        self.field.set(x, y, Field.MARKER)

    def open(self, x, y):
        if self.field.get(x, y) == Field.BOMB:
            self.field.set(x, y, Field.BOOM)
            self.field.print()
            exit(1)

        self.__rec_open(x, y)
