import os
import functools
import math
import operator
import time
import secrets
import pickle
import cv2 as cv

import numpy as np
from itertools import product

from asset import asset
from .cell import Cell
import mouse_controller
from mouse_controller import MouseButton as mb
from datetime import datetime
from .board import board
from config import config
from .utility import GameState

"""
Соглашения:
get_closed - возвращает только закрытые и НЕ отмеченные флагами
"""


class Matrix(object):
    """
    Описывает набор ячеек игрового поля и реализует логику.
    Часть функционала предназначена для решения сторонних полей (solver),
    часть - для реализации Tk игры.
    """

    def __init__(self, width: int = 0, height: int = 0):
        self.width = width   # height of matrix (number of rows)
        self.height = height  # width of matrix (number of cols)
        self.table = np.full((self.height, self.width), Cell)  # matrix itself; numpy 2D array of Cell object
        self.mines = set()  # set of bombs for Tk playing
        self._game_state: GameState | None = None

    def initialize(self):
        """
        Инициализация матрицы.
        Выполняется в дочерних классах либо экранной матрицей, либо для Tk пустыми ячейками.
        Дочерние классы имеют различные сигнатуры параметров!
        :return:
        """
        pass

    @property
    def get_state(self):
        """
        Возвращает текущее состояние игры.
        :return: GameState enum
        """
        return self._game_state

    def set_state(self, state: GameState):
        """
        Устанавливает состояние игры.
        :param state: GameState enum
        """
        self._game_state = state

    @staticmethod
    def cell_distance(cell1: Cell, cell2: Cell) -> float:
        d = math.hypot(cell1.row - cell2.row, cell1.col - cell2.col)
        return d

    def display(self):
        """
        Выводит в консоль текущее изображение поля (матрицу)
        :return: Возвращает матрицу типа array of strings
        """
        print('---DISPLAY---')

        if config.tk:
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
        mines = list([x for x in self.around_cells(cell) if x.is_mine])
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
        bombs = self.get_bombs_cells()
        if len(bombs):
            self.game_status = GameState.fail
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

    # def save(self):
    #     """
    #     Сохраняет текущую игру в папку, создавая два файла - картинку с изображением игры
    #     и файл pickle, который потом можно загрузить.
    #     """
    #     print('Saving...')
    #     random_string = secrets.token_hex(2)
    #     date_time_str = datetime.now().strftime("%d-%b-%Y--%H.%M.%S.%f")
    #     picklefile = 'obj.pickle'
    #     image_file = 'image.png'
    #     dir = 'game_R1_' + date_time_str + '_' + random_string
    #     if not os.path.exists(dir):
    #         os.makedirs(dir)
    #
    #     with open(os.path.join(dir, picklefile), 'wb') as outp:
    #         pickle.dump(self, outp, pickle.HIGHEST_PROTOCOL)
    #
    #     image = self.get_image()
    #     cv.imwrite(os.path.join(dir, image_file), image)

    def save(self, mode: str):
        """
        Сохраняет Матрицу в текстовый файл.
        Режимы:
        - 'tk' - матрица знает о расположении мин (для Tk)
        - 'screen' - матрица не знает о расположении мин (для экранной версии)
        """
        dir = 'saves'
        file_name = 'save_' + datetime.now().strftime("%d-%b-%Y--%H.%M.%S.%f")
        file_path = os.path.join(dir, file_name)

        if not os.path.exists(dir):
            os.makedirs(dir)

        with open(file_path, 'w', encoding='utf-8') as outp:
            for row in range(self.height):
                line = ''
                for col in range(self.width):
                    cell = self.table[row, col]
                    if mode == 'tk' and (row, col) in self.mines and cell.content == asset.closed:
                        line += 'ơ'
                    else:
                        line += cell.content.symbol
                outp.write(line + '\n')

    def load(self, file_name: str):
        """
        Загружает Матрицу из текстового файла.
        Режимы:
        - 'bomb' - матрица знает о расположении мин (для Tk)
        - 'no-bomb' - матрица не знает о расположении мин (для экранной версии)
        """
        pass

    def reset(self):
        """
        Нажимает на рожицу, чтобы перезапустить поле
        TODO BUG Рожицы нет в играх на маленьких полях
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












    # попытка уменьщить размер текста, но не завелось
    # def show_debug_text(self):
    #     """
    #     Показывает текст на ячейках, который содержится в каждой ячейке в debug_text, в пределах ограниченной области.
    #     Убирает текст после нажатия любой клавиши, восстанавливая исходное состояние области.
    #     """
    #     # Координаты области
    #     x1, y1, x2, y2 = self.region_x1, self.region_y1, self.region_x2, self.region_y2
    #     width = x2 - x1
    #     height = y2 - y1
    #
    #     # Получаем контекст устройства для области экрана
    #     hdesktop = win32gui.GetDesktopWindow()
    #     desktop_dc = win32gui.GetWindowDC(hdesktop)
    #
    #     # Создаем контекст устройства для сохранения области
    #     mem_dc = win32ui.CreateDCFromHandle(desktop_dc)
    #     save_dc = mem_dc.CreateCompatibleDC()
    #
    #     # Создаем битмап для сохранения области
    #     save_bitmap = win32ui.CreateBitmap()
    #     save_bitmap.CreateCompatibleBitmap(mem_dc, width, height)
    #     save_dc.SelectObject(save_bitmap)
    #
    #     # Сохраняем область экрана в битмап
    #     save_dc.BitBlt((0, 0), (width, height), mem_dc, (x1, y1), win32con.SRCCOPY)
    #
    #     font_params = {
    #         'height': 16,
    #         'width': 0,
    #         'escapement': 0,
    #         'orientation': 0,
    #         'weight': win32con.FW_NORMAL,
    #         'italic': False,
    #         'underline': False,
    #         # 'strikeout': False,
    #         'charset': win32con.ANSI_CHARSET,
    #         # 'out_precision': win32con.OUT_TT_PRECIS,
    #         # 'clip_precision': win32con.CLIP_DEFAULT_PRECIS,
    #         'quality': win32con.DEFAULT_QUALITY,
    #         # 'pitch_and_family': win32con.DEFAULT_PITCH | win32con.FF_DONTCARE,
    #         'name': "Arial"
    #     }
    #
    #     try:
    #         # Создаем шрифт с меньшим размером
    #         font_height = 12  # Высота шрифта (в пикселях)
    #         hfont = win32ui.CreateFont(font_params)
    #
    #         # Устанавливаем шрифт в контексте устройства
    #         old_font = save_dc.SelectObject(hfont)
    #
    #         # Рисуем текст поверх экрана
    #         for row in self.table:
    #             for cell in row:
    #                 if cell.debug_text is not None:
    #                     rect = (
    #                         cell.abscoordx,
    #                         cell.abscoordy,
    #                         cell.abscoordx + cell.w,
    #                         cell.abscoordy + cell.h
    #                     )
    #
    #                     # Рисуем текст только если ячейка попадает в область
    #                     if (
    #                             rect[0] >= x1 and rect[1] >= y1 and
    #                             rect[2] <= x2 and rect[3] <= y2
    #                     ):
    #                         win32gui.DrawText(desktop_dc, cell.debug_text, -1, rect, win32con.DT_LEFT)
    #                         cell.debug_text = None
    #
    #         # Ждем нажатия клавиши
    #         # keyboard.wait('space')
    #         keyboard.read_event()
    #
    #         # Восстанавливаем старый шрифт после рисования
    #         save_dc.SelectObject(old_font)
    #         # Восстанавливаем область экрана из сохраненного битмапа
    #         mem_dc.BitBlt((x1, y1), (width, height), save_dc, (0, 0), win32con.SRCCOPY)
    #
    #     finally:
    #         # Очистка ресурсов
    #         win32gui.DeleteObject(save_bitmap.GetHandle())
    #         save_dc.DeleteDC()
    #         mem_dc.DeleteDC()
    #         win32gui.ReleaseDC(hdesktop, desktop_dc)
