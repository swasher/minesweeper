from itertools import product
import numpy as np
import random

from asset import *
from .matrix import Matrix
from .cell import Cell
from .utility import GameState
from mouse_controller import MouseButton
from .matrix import MineMode


class PlayMatrix(Matrix):


    def __init__(self, width, height):
        """
        Создаем матрицу со всеми закрытыми ячейками.
        Такая матрица не свящана с экраном.

        :return:
        """

        # TODO Скорее всего есть смысл заменить "это" на обычный __init__, и каждый раз
        #  (при необходимсоти) пересоздавать объект (вызывая super).

        self.height = height
        self.width = width
        self.table = np.full((height, width), Cell)

        for row in range(height):  # cell[строка][столбец]
            for col in range(width):
                self.table[row, col] = Cell(self, row, col)

        self.lastclicked = self.table[0, 0]

    # initialize_without_screen
    def initialize(self, width, height):
        """
        Создаем матрицу со всеми закрытыми ячейками.
        Такая матрица не свящана с экраном.

        :return:
        """

        # TODO Скорее всего есть смысл заменить "это" на обычный __init__, и каждый раз
        #  (при необходимсоти) пересоздавать объект (вызывая super).

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
        self.game_state = GameState.waiting
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
        self.mine_mode = MineMode.PREDEFINED

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

        match cell.content:
            case asset.closed:
                # открываем ячейку
                if cell.is_mined:
                    # Game over!
                    # print("Game Over!")
                    self.reveal_mines_fail(cell)
                    self.game_state = GameState.fail
                    return
                else:
                    mines = len(self.around_mined_cells(cell))
                    cell.content = asset.open_cells[mines]

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

            case cell.content if cell.content in asset.digits:
                # если кол-во бомб вокруг совпадаем с цифрой - открываем все закрытые ячейки вокруг мины.
                # это поведение выполняется рекурсивно для всех соседних ячеек.
                flagged_cells = self.around_flagged_cells(cell)
                # print('Detect flagged cells:', flagged_cells)

                ### todo надо так if self.get_num_flags() == cell.content.value:
                # но почему-то не работает - ПРОВЕРИТЬ!!!
                # не работает потому, что get_

                if len(flagged_cells) == cell.content.value:
                    for neighbor in self.around_closed_cells(cell):
                        self.click_play_left_button(neighbor)

    def click_play_right_button(self, cell):
        match cell.content:
            case asset.closed:
                cell.content = flag
            case asset.flag:
                cell.content = closed

    def click_edit_mines(self, cell, button):
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
            mines = len(self.around_mined_cells(c))
            c.content = asset.open_cells[mines]

        # и в самой ячейке (если она открылась)
        if cell.is_empty:
            mines = len(self.around_mined_cells(cell))
            cell.content = asset.open_cells[mines]

    def click_edit_digits(self, cell, button):
        """
        Нажатие на ячейку в режиме редактирования цифр
        """
        rotating_states = [asset.closed, asset.n0, asset.n1, asset.n2, asset.n3,
                           asset.n4, asset.n5, asset.n6, asset.n7, asset.n8]

        match cell.content, button:

            case asset.flag, MouseButton.right:
                # удаляем флаг
                cell.remove_flag()
            case content, MouseButton.right:
                # устанавливаем флаг
                cell.set_flag()
            case content, MouseButton.left:
                if content in rotating_states:
                    next_asset = rotating_states[(rotating_states.index(content) + 1) % len(rotating_states)]
                    cell.content = next_asset

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