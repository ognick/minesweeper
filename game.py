from field import Field

class Game(object):
    def __init__(self, height: int, width: int, num_mines: int):
        self.__secret_field = secret_field = Field(height, width)
        init_x, init_y = secret_field.generate(num_mines)
        self.init_num_mines = self.num_mines = num_mines
        self.num_unknowns = height * width
        self.field = Field(height, width)
        self.open(init_x, init_y)

    def check_done(self) -> bool:
        return self.num_mines == 0 and self.num_unknowns == 0

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
        if self.__secret_field.get(x, y) != Field.BOMB:
            self.field.set(x, y, Field.BOOM)
            self.field.print()
            exit(1)

        self.field.set(x, y, Field.MARKER)
        self.num_mines -= 1
        self.num_unknowns -=1

    def open(self, x, y):
        if self.__secret_field.get(x, y) == Field.BOMB:
            self.field.set(x, y, Field.BOOM)
            self.field.print()
            print('BOOM!')
            exit(1)

        self.num_unknowns -= self.__rec_open(x, y)

    def print(self):
        width, height = self.field.get_size()
        total_places = width * height
        print(f'places:{self.num_unknowns}/{total_places}, mines:{self.num_mines}/{self.init_num_mines}')
        self.field.print()
