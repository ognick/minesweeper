import random

from game import Game
from solver import Solver

seed = random.randint(0, 1000)
print(f'Seed: {seed}')
random.seed(894)

Solver(Game(16, 30, 99)).solve()

