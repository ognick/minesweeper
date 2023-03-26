from functools import lru_cache
from random import randint

from color import Color, print_chr, print_num


class Field(object):
    BOMB = -1
    UNKNOWN = -2
    MARKER = -3
    BOOM = -4

    def __init__(self, height: int, width: int):
        self.num_mines = None
        self.num_unknowns = width * height
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

    def traverse(self, func) -> bool:
        state = {}
        result = False
        for y, line in enumerate(self._f):
            for x, num in enumerate(line):
                if func(x, y, num, state):
                    result = True
        return result

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
        y = randint(0, height - 1)
        x = randint(0, width - 1)
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