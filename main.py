import random

from game import Game
from solver import Solver

seed = random.randint(0, 1000)
random.seed(seed)

Solver(Game(16, 30, 99)).solve()
print(f'seed {seed}')
