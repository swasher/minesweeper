from itertools import product
import numpy as np
import random

from ..matrix import Matrix
from ..matrix import MineMode
from ..cell import Cell
from ..utility import GameState
from mouse_controller import MouseButton

from assets import *


class TkMatrix(Matrix):

    def __init__(self, width, height):
        """
        Создаем матрицу со всеми закрытыми ячейками.
        Такая матрица не свящана с экраном.

        :return:
        """
        super().__init__()
        self.height = height
        self.width = width
        self.table = np.full((height, width), Cell)

        for row in range(height):  # cell[строка][столбец]
            for col in range(width):
                self.table[row, col] = Cell(self, row, col)

        self.lastclicked = self.table[0, 0]

    def get_mined_cells(self) -> list[Cell]:
        """
        Возвращает список установленных мин в закрытых ячейках (только для Tk сапера).
        В отличие от get_num_mined - эта включает и мины с флагами!
        """
        return [self.table[row][col] for row, col in self.mines]

    def get_num_mined(self) -> int:
        """
        Кол-во не помеченных флагами мин (обычно это число на LED-индикаторе)
        """
        return len(self.get_mined_cells()) - self.get_num_flags

    def create_new_game(self, n_bombs: int = 0):
        """
        Used to create a new game.
        Fills the field with bombs and closed cells.
        This matrix is not linked to the screen.

        # TODO Сделать проверку доски на валидность после расположения мин.

        :param n_bombs: Number of bombs to place
        :return:
        """
        self.game_state = GameState.waiting
        self.mines = set()  # Initialize the set to store mine positions

        for row, col in product(range(self.height), range(self.width)):
            self.table[row, col].content = closed

        placed_mines = 0
        while placed_mines < n_bombs:
            row = random.randint(0, self.height - 1)
            col = random.randint(0, self.width - 1)

            if (row, col) not in self.mines:
                self.mines.add((row, col))
                placed_mines += 1
        self.mine_mode = MineMode.PREDEFINED

    def check_for_win(self):
        """
        Выигрыш, если:
        - количество закрытых ячеек + кол-во флагов = количеству мин
        - все (закрытые ячейки + флаги) содержат мины
        :return: True если WIN, иначе False
        """
        # Первое условие: кол-во закрытых ячеек = кол-ву оставшихся мин
        if self.get_num_closed != self.get_num_mined():
            return False

        # Второе условие: все закрытые ячейки и флаги содержат мины
        # Получаем списки ячеек
        closed_cells = self.get_closed_cells()
        flag_cells = self.get_flagged_cells()

        # Проверяем, что каждая закрытая ячейка содержит мину
        for cell in closed_cells:
            if not cell.is_mined:
                return False

        # Проверяем, что каждая ячейка с флагом содержит мину
        for cell in flag_cells:
            if not cell.is_mined:
                return False

        return True

    def click_play_left_button(self, cell):
        """
        Метод для "игры" в сапера Tk.
        :param cell:
        :return:
        """
        if cell.is_closed:
            # открываем ячейку
            if cell.is_mined:
                # Game over!
                # print("Game Over!")
                self.reveal_mines_fail(cell)
                self.game_state = GameState.fail
                return
            else:
                mines = self.around_mined_num(cell)
                cell.content = find_asset_by_value(open_cells, target_value=mines)

                # make check for win
                if self.check_for_win():
                    # print("You Win!")
                    self.reveal_mines_win()
                    self.game_state = GameState.win
                    return

                # Если вокруг ячейки нет бомб (n0), открываем все соседние ячейки
                if cell.is_empty:
                    for neighbor in self.around_closed_cells(cell):
                        self.click_play_left_button(neighbor)

        elif cell.content in digits:
            # если кол-во бомб вокруг совпадаем с цифрой - открываем все закрытые ячейки вокруг мины.
            # это поведение выполняется рекурсивно для всех соседних ячеек.
            if self.around_flagged_num(cell) == cell.content.value:
                for neighbor in self.around_closed_cells(cell):
                    self.click_play_left_button(neighbor)

    @staticmethod
    def click_play_right_button(cell):
        # todo может перенести это в метод Cell, а не Matrix?
        if cell.is_closed:
            cell.content = flag
        elif cell.is_flag:
            cell.content = closed
        else:
            pass  # do none if right click on other cells

    def click_edit_mines_predefined(self, cell, button):
        """
        Нажатие на ячейку в режиме редактирования мин.

        Нам нужно итерировать состояние ячейки по нескольким ассетам ПЛЮС
        закрытая ячейка с бомбой. Для этого введен псевдо-ассет there_is_bomb, который на самом деле является
        ЗАКРЫТОЙ ЯЧЕЙКОЙ плюс мина в matrix.mines.
        """
        is_mined = cell.is_mined
        open_cells_symbols = {c.symbol for c in open_cells}

        match cell.content.symbol, is_mined, button:
            case closed.symbol, False, MouseButton.left:
                # закрытая - ставим мину (ассет при этом не меняется - остается closed)
                cell.set_mine()
            case closed.symbol, True, MouseButton.left:
                # мина -> открываем
                cell.remove_mine()
                cell.content = n0
            case symbol, False, MouseButton.left if symbol in open_cells_symbols:
                # открытая -> закрываем
                cell.content = closed
            case flag.symbol, _, MouseButton.right:
                # удаляем флаг
                cell.remove_flag()
            case closed.symbol, _, MouseButton.right:
                # устанавливаем флаг
                cell.set_flag()

        # обновляем цифры вокруг
        cells_to_update = self.around_opened_cells(cell)
        for c in cells_to_update:
            mines = self.around_mined_num(c)
            c.content = find_asset_by_value(open_cells, target_value=mines)

        # и в самой ячейке (если она открылась)
        if cell.is_empty:
            mines = self.around_mined_num(cell)
            cell.content = find_asset_by_value(open_cells, target_value=mines)

    def click_edit_mines_undefined(self, cell, button):
        """
        Нажатие на ячейку в режиме редактирования цифр
        """
        rotating_states = [closed, n0, n1, n2, n3, n4, n5, n6, n7, n8]

        if cell.is_flag and button == MouseButton.right:
            cell.remove_flag()
        elif not cell.is_flag and button == MouseButton.right:
            cell.set_flag()
        elif button == MouseButton.left:
            if cell.content in rotating_states:
                next_asset = rotating_states[(rotating_states.index(cell.content) + 1) % len(rotating_states)]
                cell.content = next_asset

    def reveal_mines_fail(self, cell):
        mines = self.get_mined_cells()
        for m in mines:
            m.content = bomb
        cell.content = bomb_red

    def reveal_mines_win(self):
        """
        Если мы открыли все ячейки (кроме мин), то все оставшиеся закрытые ячейки с минами помечаются флагами
        """
        mines = self.get_mined_cells()
        for m in mines:
            if m.content == closed:
                m.content = flag

    def bomb_qty(self) -> int:
        """
        Возвращает число, которое на игровом поле на счетчике бомб (сколько еще спрятанных бомб на поле)
        :return:
        """
        return len(self.mines)


__all__ = ['TkMatrix']