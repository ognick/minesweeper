from game import Field, Game


def get_unknown_neighbors(field: Field, x: int, y: int) -> list[tuple[int, int]]:
    return [(x, y) for (x, y, num) in field.get_neighbors(x, y) if num == Field.UNKNOWN]


def get_marked_neighbors(field: Field, x: int, y: int) -> list[tuple[int, int]]:
    return [(x, y) for (x, y, num) in field.get_neighbors(x, y) if num == Field.MARKER]


def get_open_neighbors(field: Field, x: int, y: int) -> list[tuple[int, int, int]]:
    return [(x, y, num) for (x, y, num) in field.get_neighbors(x, y) if num > 0]


def is_valid_layout(places: int, mines: int, num: int) -> bool:
    length = 0
    active_bits_count = 0
    while num > 0:
        if (num & 0b1) > 0:
            active_bits_count += 1
            if active_bits_count > mines:
                return False

        length += 1
        if length > places:
            return False

        num >>= 1

    return mines == active_bits_count


def generate_layouts(places: int, mines: int) -> list[int]:
    result = []
    for bit_layout in range(1 << places):
        if is_valid_layout(places, mines, bit_layout):
            result.append(bit_layout)
    return result


def reduce_layouts(layouts: list[int]) -> int:
    assert len(layouts) > 0
    result = layouts[0]
    for layout in layouts:
        result &= layout
    return result


def apply_layout(neighbors: list[any], layout: int) -> list[any]:
    res = []
    i = 0
    while layout > 0:
        if (layout & 0b1) > 0:
            res.append(neighbors[i])
        i += 1
        layout >>= 1
    return res


class Solver:
    def __init__(self, game: Game):
        self.game = game

    def clone_field(self) -> Field:
        width, height = self.game.field.get_size()
        clone = Field(height, width)
        self.game.field.traverse(clone.set)
        return clone

    def mark_if_number_equals_unknowns(self, x, y, num) -> bool:
        if num < 1:
            return False

        unknown_neighbors = get_unknown_neighbors(self.game.field, x, y)
        unknown_neighbors_count = len(unknown_neighbors)
        if unknown_neighbors_count == 0:
            return False

        marked_neighbors = get_marked_neighbors(self.game.field, x, y)
        if unknown_neighbors_count == num - len(marked_neighbors):
            for x, y in unknown_neighbors:
                self.game.mark(x, y)
            return True
        return False

    def open_if_number_equals_markers(self, x, y, num) -> bool:
        if num < 1:
            return False

        marked_neighbors = get_marked_neighbors(self.game.field, x, y)
        unknown_neighbors = get_unknown_neighbors(self.game.field, x, y)
        unknown_neighbors_count = len(unknown_neighbors)
        if unknown_neighbors_count > 0 and len(marked_neighbors) == num:
            for x, y in unknown_neighbors:
                self.game.open(x, y)
            return True
        return False

    def open_if_contacted_with_enough_markers(self, x, y, num) -> bool:
        if num < 1:
            return False

        unknown_neighbors = set(get_unknown_neighbors(self.game.field, x, y))
        if not unknown_neighbors:
            return False

        open_neighbors = set()
        for nx, ny in unknown_neighbors:
            open_neighbors |= set(get_open_neighbors(self.game.field, nx, ny))
        open_neighbors.discard((x, y, num))

        if not open_neighbors:
            return False

        used_neighbors = set()
        capacity = num - len(get_marked_neighbors(self.game.field, x, y))
        for opn_x, opn_y, opn_num in open_neighbors:
            sub_unknown_neighbors = set(get_unknown_neighbors(self.game.field, opn_x, opn_y))
            if not sub_unknown_neighbors:
                continue

            if sub_unknown_neighbors - unknown_neighbors:
                continue

            if sub_unknown_neighbors & used_neighbors:
                continue

            sub_marked_neighbors = get_marked_neighbors(self.game.field, opn_x, opn_y)
            opn_num -= len(sub_marked_neighbors)
            capacity -= opn_num
            used_neighbors |= sub_unknown_neighbors

            if capacity == 0:
                free_places = unknown_neighbors - used_neighbors
                if free_places:
                    for nx, ny in free_places:
                        self.game.open(nx, ny)
                    return True
                break

        return False

    def mark_if_there_is_only_one_option(self, x, y, num) -> bool:
        result = False
        if num < 1:
            return result

        unknown_neighbors = get_unknown_neighbors(self.game.field, x, y)
        unknown_neighbors_count = len(unknown_neighbors)
        if unknown_neighbors_count == 0:
            return result

        mines_count = num - len(get_marked_neighbors(self.game.field, x, y))

        if unknown_neighbors_count > mines_count:
            layouts = []
            for layout in generate_layouts(unknown_neighbors_count, mines_count):
                planted_places = set(apply_layout(unknown_neighbors, layout))
                try:
                    for pl_x, pl_y in planted_places:
                        for opn_x, opn_y, opn_num in get_open_neighbors(self.game.field, pl_x, pl_y):
                            sub_unknown = set(get_unknown_neighbors(self.game.field, opn_x, opn_y))
                            exited_markers = get_marked_neighbors(self.game.field, opn_x, opn_y)
                            shared_places = planted_places & sub_unknown
                            if opn_num < len(exited_markers) + len(shared_places):
                                raise StopIteration

                    layouts.append(layout)
                except StopIteration:
                    continue

            layout = reduce_layouts(layouts)
            if layout > 0:
                for nx, ny in apply_layout(unknown_neighbors, layout):
                    result = True
                    self.game.mark(nx, ny)

        return result

    def solve(self):
        alive = True
        while alive and not self.game.check_done():
            alive = False
            methods =[
                self.mark_if_number_equals_unknowns,
                self.open_if_number_equals_markers,
                self.mark_if_there_is_only_one_option,
                self.open_if_contacted_with_enough_markers
            ]
            for func in methods:
                if self.game.field.traverse(func):
                    alive = True
                    break
            if alive:
                continue

        self.game.field.print()
        if self.game.check_done():
            print('SOLVED!')
            exit(0)

        print('F@CK(')
        exit(1)
