from itertools import product
import numpy as np
import random

from asset import asset
from .matrix import Matrix
from .cell import Cell


class PlayMatrix(Matrix):

    # initialize_without_screen
    def initialize(self, width, height):
        """
        Создаем матрицу со всеми закрытыми ячейками.
        Такая матрица не свящана с экраном.
        :return:
        """
        self.height = height
        self.width = width
        self.table = np.full((height, width), Cell)

        for row in range(height):  # cell[строка][столбец]
            for col in range(width):
                self.table[row, col] = Cell(row, col, matrix=self)

        self.lastclicked = self.table[0, 0]

    def create_new_game(self, n_bombs: int = 0):
        """
        Used to create a new game.
        Fills the field with bombs and closed cells.
        This matrix is not linked to the screen.

        # TODO Сделать проверку доски на валидность после расположения мин.

        :param n_bombs: Number of bombs to place
        :return:
        """
        self.mines = set()  # Initialize the set to store mine positions

        for row, col in product(range(self.height), range(self.width)):
            self.table[row, col].asset = asset.closed

        placed_mines = 0
        while placed_mines < n_bombs:
            row = random.randint(0, self.height - 1)
            col = random.randint(0, self.width - 1)

            if (row, col) not in self.mines:
                self.mines.add((row, col))
                placed_mines += 1