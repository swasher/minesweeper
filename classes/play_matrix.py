from itertools import product
import numpy as np
import random

from asset import *
from .matrix import Matrix
from .cell import Cell
from .utility import GameState


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
                self.table[row, col] = Cell(self, row, col)

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
        self.set_state(GameState.waiting)
        self.mines = set()  # Initialize the set to store mine positions

        for row, col in product(range(self.height), range(self.width)):
            self.table[row, col].content = asset.closed

        placed_mines = 0
        while placed_mines < n_bombs:
            row = random.randint(0, self.height - 1)
            col = random.randint(0, self.width - 1)

            if (row, col) not in self.mines:
                self.mines.add((row, col))
                placed_mines += 1

    def play_left_button(self, cell):
        """
        Метод для "игры" в сапера Tk.
        :param cell:
        :return:
        """

        match cell.content:
            case asset.closed:
                # открываем ячейку
                if cell.is_mine:
                    # Game over!
                    # print("Game Over!")
                    self.reveal_mines_fail(cell)
                    self.set_state(GameState.fail)
                    return
                else:
                    mines = len(self.around_mined_cells(cell))
                    cell.content = asset.open_cells[mines]

                    # make check for win
                    if self.check_for_win():
                        # print("You Win!")
                        self.reveal_mines_win()
                        self.set_state(GameState.win)
                        return

                    # Если вокруг ячейки нет бомб (n0), открываем все соседние ячейки
                    if cell.is_empty:
                        for neighbor in self.around_closed_cells(cell):
                            self.play_left_button(neighbor)

            case cell.content if cell.content in asset.digits:
                # TODO пока держит мышку, закрытые ячейки вокруг визуально меняем на открытые (как-бы подсвечиваем)
                # TODO это нужно реализовать в Tk части
                # если кол-во бомб вокруг совпадаем с цифрой - открываем все закрытые ячейки вокруг мины.
                flagged_cells = self.around_flagged_cells(cell)
                # print('Detect flagged cells:', flagged_cells)
                if len(flagged_cells) == cell.content.value:
                    print('Flagged equal!')
                    for neighbor in self.around_closed_cells(cell):
                        print('Neighbors: ', self.around_closed_cells(cell))

                        self.play_left_button(neighbor)

    def check_for_win(self):
        """
        Выигрыш, если:
        - количество закрытых ячеек + кол-во флагов = количеству мин
        - все (закрытые ячейки + флаги) содержат мины
        :return: True если WIN, иначе False
        """
        # Первое условие: кол-во закрытых + кол-во флагов = кол-во мин
        if self.get_num_closed() + self.get_num_flags() != self.get_num_mined():
            return False

        # Второе условие: все закрытые ячейки и флаги содержат мины
        # Получаем списки ячеек
        closed_cells = self.get_closed_cells()
        flag_cells = self.get_flag_cells()

        # Проверяем, что каждая закрытая ячейка содержит мину
        for cell in closed_cells:
            if not cell.is_mine:
                return False

        # Проверяем, что каждая ячейка с флагом содержит мину
        for cell in flag_cells:
            if not cell.is_mine:
                return False

        return True


    def play_right_button(self, cell):
        match cell.content:
            case asset.closed:
                cell.content = asset.flag
            case asset.flag:
                cell.content = asset.closed

    def reveal_mines_fail(self, cell):
        bombs = self.get_mined_cells()
        for b in bombs:
            b.content = asset.bomb
        cell.content = asset.bomb_red

    def reveal_mines_win(self):
        bombs = self.get_mined_cells()
        for b in bombs:
            if b.content == closed:
                b.content = flag

    def bomb_qty(self) -> int:
        """
        Возвращает число, которое на игровом поле на счетчике бомб (сколько еще спрятанных бомб на поле)
        :return:
        """
        return len(self.mines)