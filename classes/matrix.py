import os
import functools
import math
import operator
import time
import secrets
import pickle
import cv2 as cv
from enum import IntEnum

import numpy as np
from itertools import product

from asset import *
from .cell import Cell
import mouse_controller
from mouse_controller import MouseButton as mb
from datetime import datetime
from .board import board
from config import config
from .utility import GameState, MineMode
from .matrix_io import MatrixIO

"""
Соглашения:
get_closed - возвращает только закрытые и НЕ отмеченные флагами
"""


class Matrix:
    """
    Описывает набор ячеек игрового поля и реализует логику.
    В этой части собраны методы, общие как для Tk-версии (наследник play_matrix), так
    и для Solver'а (наследник solve_matrix)
    """
    def __init__(self, width: int = 0, height: int = 0):
        self.io = MatrixIO(self)
        self.width = width   # height of matrix (number of rows)
        self.height = height  # width of matrix (number of cols)
        self.table = np.full((self.height, self.width), Cell)  # matrix itself; numpy 2D array of Cell object
        self._game_state: GameState = GameState.waiting
        self._mine_mode = MineMode.UNDEFINED

        # TODO Переместить эти две строчки в PlayMatrix? с одной стороны, известные мины
        #  только в Playmatrix могут быть, с другой, у нас есть методы, которые используют мины и находятся в Matrix
        #  для унификации расположения однотипных методов.
        self.mines = set()  # set of bombs for Tk playing


    def initialize(self):
        """
        Инициализация матрицы.
        Выполняется в дочерних классах либо экранной матрицей, либо для Tk пустыми ячейками.
        Дочерние классы имеют различные сигнатуры параметров!

        TODO переделать, чтобы вся инициализация выполнялась в __init__.
         При необходимости создавать новый объект, а не переинициализировать старый.
        """
        pass

    def save(self):
        text = self.matrix_to_text()
        self.io.save(text)

    def load(self, file_path: str):
        self.io.load(file_path)

    @property
    def game_state(self) -> GameState:
        """
        Возвращает текущее состояние игры.
        :return: GameState enum
        """
        return self._game_state

    @game_state.setter
    def game_state(self, state: GameState):
        """
        Устанавливает состояние игры.
        :param state: GameState enum
        """
        self._game_state = state

    @property
    def mine_mode(self) -> MineMode:
        """Возвращает режим расположения мин"""
        return self._mine_mode

    @mine_mode.setter
    def mine_mode(self, mode: MineMode):
        """Устанавливает режим расположения мин"""
        self._mine_mode = mode

    @staticmethod
    def cell_distance(cell1: Cell, cell2: Cell) -> float:
        d = math.hypot(cell1.row - cell2.row, cell1.col - cell2.col)
        return d

    def matrix_to_text(self):
        matrix = []
        for row in range(self.height):
            line = ''
            for col in range(self.width):
                cell = self.table[row, col]
                line += cell.content.symbol
            line = ' '.join(line)
            matrix.append(line)
        return matrix

    def display(self):
        """
        Выводит в консоль текущее изображение поля (матрицу)
        Мы не можем тут использовать matrix_to_text, потому что та функция не показывает мины в матрице.
        :return: Возвращает матрицу типа array of strings
        """
        print('---DISPLAY---')

        if self.mine_mode == MineMode.PREDEFINED:
            matrix_view = [
                ' '.join(
                    asset.there_is_bomb.symbol
                    if ((row, col) in self.mines and not self.table[row, col].is_flag)  # -> показываем мину, если по коорд. row, col находится мина И в ячейке нет флага
                    else self.table[row, col].content.symbol
                    for col in range(self.width))
                for row in range(self.height)
            ]
        else:
            matrix_view = [
                ' '.join(
                    self.table[row, col].content.symbol
                    for col in range(self.width))
                for row in range(self.height)
            ]
        print('\n'.join(matrix_view))
        return matrix_view

    def around_cells(self, cell: Cell) -> list[Cell]:
        """
        Returns a list of cells surrounding the given cell (including diagonals).
        Uses NumPy's capabilities to handle edge cases efficiently.

        Для ячейки в центре это будет 8 "соседей", для угловой - 3, для ячейки возле стенки - 5.

        Args:
            cell: Cell object with row and col attributes

        Returns:
            list[Cell]: List of neighboring cells
        """
        rows, cols = self.table.shape

        # Calculate valid row and column ranges
        row_start = max(0, cell.row - 1)
        row_end = min(rows, cell.row + 2)
        col_start = max(0, cell.col - 1)
        col_end = min(cols, cell.col + 2)

        # Get the subarray of neighboring cells
        neighbors = self.table[row_start:row_end, col_start:col_end]

        # Convert to flat list and remove the center cell
        cells = neighbors.flatten().tolist()
        center_idx = (cell.row - row_start) * (col_end - col_start) + (cell.col - col_start)
        cells.pop(center_idx)

        return cells

    def around_closed_cells(self, cell) -> list[Cell]:
        """
        Возвращает список закрытых ячеек вокруг ячейки cell.
        Флаги не считаются закрытыми ячейками.
        :param cell: instance of Cell class
        :return: array of Cell instances
        """
        closed_cells = list([x for x in self.around_cells(cell) if x.is_closed])
        return closed_cells

    def around_flagged_cells(self, cell) -> list[Cell]:
        """
        Возвращает список ячеек-флагов вокруг ячейки cell
        :param cell: instance of Cell class
        :return: array of Cell instances
        """
        flagged_cells = list([x for x in self.around_cells(cell) if x.is_flag])
        return flagged_cells

    def around_digit_cells(self, cell) -> list[Cell]:
        """
        Возвращает список ячеек-цифр вокруг ячейки cell
        :param cell: instance of Cell class
        :return: array of Cell instances
        """
        flagged_cells = list([x for x in self.around_cells(cell) if x.is_digit])
        return flagged_cells

    def around_opened_cells(self, cell) -> list[Cell]:
        """
        Возвращает список открытых ячеек вокруг ячейки cell.
        :param cell: instance of Cell class
        :return: array of Cell instances
        """
        flagged_cells = list([x for x in self.around_cells(cell) if x.is_open])
        return flagged_cells

    def around_mined_cells(self, cell) -> list[Cell]:
        """
        Возвращает список ячеек-мин вокруг ячейки cell.
        Используется для tk-версии с известно расположенными минами.
        :param cell: instance of Cell class
        :return: array of Cell instances
        """
        mines = list([x for x in self.around_cells(cell) if x.is_mined])
        return mines

    def get_closed_cells(self) -> list[Cell]:
        """
        Возвращает все закрытые ячейки (которые закрыты и НЕ отмечены флагом)
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_closed])
        return cells

    def get_opened_cells(self) -> list[Cell]:
        """
        Возвращает все открытые ячейки (это цифры плюс пустая ячейка)
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_open])
        return cells

    def get_flag_cells(self) -> list[Cell]:
        """
        Возвращает список закрытых ячеек, уже помеченных флагами
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_flag])
        return cells

    def get_digit_cells(self) -> list[Cell]:
        """
        Возвращает список открытых ячеек (без нулевых ячеек)
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_digit])
        return cells

    def get_open_cells(self) -> list[Cell]:
        """
        Возвращает список открытых ячеек (включая нули).
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_open])
        return cells

    def get_bombs_cells(self) -> list[Cell]:
        """
        Возвращает список бомб (которые видны, если игра окончена). Используется в game_over
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_bomb])
        return cells

    def get_mined_cells(self) -> list[Cell]:
        """
        Возвращает список установленных мин в закрытых ячейках (только для Tk сапера).
        :return:
        """
        return [self.table[row][col] for row, col in self.mines]

    def get_noguess_cell(self) -> list[Cell]:
        """
        Первый ход для no-guess игр. Возвращает отмеченную крестиком клетку.
        :return: list of Cell objects
        """
        cell = list([x for x in self.table.flat if x.is_noguess])
        return cell

    def get_num_closed(self) -> int:
        """
        Кол-во закрытых ячеек (флаг не считается закрытой ячейкой!)
        """
        return len(self.get_closed_cells())

    def get_num_flags(self) -> int:
        """
        Кол-во установленных флагов
        """
        return len(self.get_flag_cells())

    def get_num_mined(self) -> int:
        """
        Кол-во мин (только для Tk)
        """
        return len(self.get_mined_cells())

    def is_mine(self, cell) -> bool:
        return (cell.row, cell.col) in self.mines

    @property
    def you_fail(self) -> bool:
        """
        Если в матрице есть бомбы - то FAIL (бомбы - это открытое изображение бомбы после проигрыша)
        :return:
        """
        revealed_bombs = self.get_bombs_cells()
        if len(revealed_bombs):
            self.game_state = GameState.fail
            return True

    @property
    def you_win(self) -> bool:
        """
        Имплементируется по разному в Tk и в экранной версии.
        """
        pass

    def bomb_qty(self) -> int:
        """
        Имеет совершенно разную имплементацию в Tk и в экранной версии.
        Tk знает количество мин из матрицы.
        Экранная версия считает количество мин по LED счетчику.
        """
        pass

    # def save(self, mine_mode: MineMode):
    #     pass
    #
    # def load(self, file):
    #     pass


    # def save(self, mine_mode: MineMode):
    #     """
    #     Сохраняет Матрицу в текстовый файл.
    #
    #     РЕЖИМЫ ПОД ВОПРОСОМ!!!!!!
    #     Режимы:
    #     - PREDEFINED - матрица знает о расположении мин (для Tk)
    #     - UNDEFINED - матрица не знает о расположении мин (для Tk и экранной версии)
    #
    #     × - закрытая клетка
    #     ơ - закрытая клетка с миной (только для PREDEFINED)
    #     ⚑ - флаг
    #     ⚐ - неверно поставленный флаг (мины нет) (только для PREDEFINED)
    #     · - открытая клетка (0)
    #     1-8 - открытая клетка с цифрой
    #
    #     Формат:
    #
    #     [properties]
    #     width = 8
    #     height = 8
    #     mine_mode = PREDEFINED | UNDEFINED
    #
    #     [matrix]
    #     × × × ơ × × × × ×
    #     × × × 2 × × ơ × ×
    #     ơ × 1 ơ 1 1 1 1 ×
    #     × × 2 1 1 · · 1 ⚐
    #     × ơ 2 × 1 · · 1 ⚑
    #     × × × ơ 2 1 · 2 2
    #     × × × × ⚑ 2 1 1 ⚑
    #     × × × × × ⚑ 1 1 1
    #     × × × × × × × × ⚐
    #
    #     [solutions]
    #     # reserved for future use
    #     """
    #     dir = 'saves'
    #     file_name = 'save_' + datetime.now().strftime("%d-%b-%Y--%H.%M.%S.%f") + '.txt'
    #     file_path = os.path.join(dir, file_name)
    #
    #     if not os.path.exists(dir):
    #         os.makedirs(dir)
    #
    #     with open(file_path, 'w', encoding='utf-8') as outp:
    #         # Записываем секцию матрицы
    #         outp.write("[properties]\n")
    #         outp.write(f"width = {self.width}\n")
    #         outp.write(f"height = {self.height}\n")
    #         mode = mine_mode.name
    #         outp.write(f"mode = {mode}\n")
    #
    #         outp.write("\n[matrix]\n")
    #         for row in range(self.height):
    #             line = ''
    #             for col in range(self.width):
    #                 cell = self.table[row, col]
    #
    #                 if mine_mode == MineMode.PREDEFINED and cell.is_mined and cell.content == asset.closed:
    #                     line += there_is_bomb.symbol  # 'ơ'
    #                 elif mine_mode == MineMode.PREDEFINED and not cell.is_mined and cell.content == asset.flag:
    #                     line += bomb_wrong.symbol  # '⚐'
    #                 else:
    #                     line += cell.content.symbol
    #
    #             line = ' '.join(line)
    #             outp.write(line + '\n')
    #
    #         outp.write("\n[solution]")
    #     print('Matrix saved to', file_path)

    # def load(self, file_path: str):
    #     """
    #     Загружает Матрицу из текстового файла.
    #     См. метод save() для описания формата файлат и символов.
    #
    #     Args:
    #         file_path (str): Путь к файлу сохранения
    #
    #     Returns:
    #         None
    #
    #     Raises:
    #         FileNotFoundError: Если файл не найден
    #         ValueError: Если формат файла некорректен
    #     """
    #     import os
    #     from asset import asset
    #
    #     if not os.path.exists(file_path):
    #         raise FileNotFoundError(f"Save file not found: {file_path}")
    #
    #     # Словарь для обратного преобразования: буква -> asset
    #     symbol_to_asset = {
    #         asset.closed.symbol: asset.closed,
    #         asset.flag.symbol: asset.flag,
    #         asset.there_is_bomb.symbol: asset.there_is_bomb,
    #         asset.bomb_wrong.symbol: asset.bomb_wrong,
    #     }
    #
    #     # Добавляем цифры от 0 до 8
    #     for i, digit_asset in enumerate(asset.open_cells):
    #         symbol_to_asset[digit_asset.symbol] = digit_asset
    #
    #     current_section = None
    #     matrix_data = []
    #
    #     with open(file_path, 'r', encoding='utf-8') as inp:
    #         for line in inp:
    #             line = line.strip()
    #
    #             # Пропускаем пустые строки
    #             if not line:
    #                 continue
    #
    #             # Обработка заголовков секций
    #             if line.startswith('[') and line.endswith(']'):
    #                 current_section = line[1:-1]
    #                 continue
    #
    #             if current_section == 'properties':
    #                 key, value = line.split(' = ')
    #                 if key == 'width':
    #                     self.width = int(value)
    #                 elif key == 'height':
    #                     self.height = int(value)
    #                 elif key == 'mode':
    #                     if value in ['PREDEFINED', 'UNDEFINED']:
    #                         loaded_mine_mode = MineMode[value]
    #                     else:
    #                         raise ValueError(f"Invalid mode: {value}")
    #
    #             elif current_section == 'matrix':
    #                 # Убираем пробелы между символами, если они есть
    #                 line = ''.join(line.split())
    #                 matrix_data.append(line)
    #
    #             elif current_section == 'solution':
    #                 # reserved for future use
    #                 ...
    #
    #     # Инициализируем матрицу
    #     self.table = np.full((self.height, self.width), Cell)
    #     self.mines = set()
    #
    #     # Заполняем матрицу данными
    #     for row in range(self.height):
    #         for col in range(self.width):
    #             symbol = matrix_data[row][col]
    #             cell = Cell(self, row=row, col=col)
    #
    #             # Конвертируем символ в asset
    #             if symbol not in symbol_to_asset:
    #                 raise ValueError(f"Unknown symbol in save file: {symbol}")
    #             cell.content = symbol_to_asset[symbol]
    #
    #             # Если это мина, то добавляем в список мин, а ячейку закрываем
    #             if cell.content == asset.there_is_bomb:
    #                 self.mines.add((row, col))
    #                 cell.content = asset.closed
    #
    #             # # Если это "правильный" флаг, то значит в ячейке есть мина
    #             if cell.content == asset.flag:
    #                 self.mines.add((row, col))
    #                 cell.content = asset.flag
    #
    #
    #             # Если это "неправильный" флаг, то значит в ячейке мины нет, а флаг нужно заменить на обычный, чтобы
    #             # получилось как перед сохранением
    #             if cell.content == asset.bomb_wrong:
    #                 cell.content = asset.flag
    #
    #             self.table[row, col] = cell
    #
    #     print(f'Matrix loaded from {file_path}')
    #     self.display()

    def reset(self):
        """
        Нажимает на рожицу, чтобы перезапустить поле
        TODO BUG Рожицы нет в играх на маленьких полях - на кастомных полях MinSweeper.Online шириной 7 и меньше
        :return:

        Сделать, чтобы эти настройки брались из asset.
        Пока что мне кажется можно координату X брать как половину поля,
        а Y из ассета
        """

        face_coord_x = (self.region_x2 - self.region_x1)//2 + self.region_x1
        face_coord_y = self.region_y1 + board.smile_y_coord
        mouse_controller.click(face_coord_x, face_coord_y, mb.left)
        for c in self.table.flat:
            # deprecated
            # c.status = 'closed'
            c.type = asset.closed
        time.sleep(config.screen_refresh_lag * 10)
