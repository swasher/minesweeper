from __future__ import annotations
from typing import TYPE_CHECKING

import cv2 as cv
import win32api
import win32gui
import win32con
import xxhash
from enum import IntEnum


from asset import *
from asset import bombs, digits, open_cells, all_cell_types
import mouse_controller
from config import config
from util import point_in_rect
from util import random_point_in_square
from .utility import Color

if TYPE_CHECKING:
    from asset import Asset
    from classes import SolveMatrix, PlayMatrix
    from numpy import ndarray


class Cell:

    def __init__(self, matrix: SolveMatrix | PlayMatrix,
                 row: int, col: int,
                 coordx: int = 0, coordy: int = 0,
                 abscoordx: int = 0, abscoordy: int = 0,
                 w: int = 0, h: int = 0):
        """
        Определить, является ли ячейка миной, можно обратившиться к матрице и вызвать метод is_mine(self).

        :param col: номер ячейки в строке, начиная с 0. Т.е. это СТОЛБЕЦ. Левая ячейка - номер 0 - cell[строка][столбец]
        :param row: номер ячейки в столбце, начиная с 0. Т.е. это СТРОКА. Верхняя ячейка - номер 0
        :param coordx: коор. на экране X от левого верхнего угла ДОСКИ в пикселях
        :param coordy: коор. на экране Y от левого верхнего угла ДОСКИ в пикселях
        :param abscoordx: коор. на экране X от левого верхнего угла ЭКРАНА в пикселях
        :param abscoordy: коор. на экране Y от левого верхнего угла ЭКРАНА в пикселях
        :param w: ширина ячейки в пикселях
        :param h: высота ячейки в пикселях
        :param asset: instance of Asset - что содержится в ячейке
        :param image: ndarray - текущее изображение ячейки
        :param hash: int - хэш изображения ячейки
        """
        self.matrix = matrix
        # column and row of matrix
        self.col = col
        self.row = row
        # coordinates from game board; need it because we take screenshot only game board
        self.coordx = coordx
        self.coordy = coordy
        # coordinates from screen; for example used for draw on screen
        self.abscoordx = abscoordx
        self.abscoordy = abscoordy
        self.w = w
        self.h = h
        # self.status = 'closed'
        self.content: Asset | None = None  # Asset instance
        self.image: ndarray | None = None  # Current image of cell; ndarray
        self.hash = 0  # hash of image

    def __repr__(self):
        return f'{self.content.name} ({self.row}:{self.col})'

    def symbol(self):
        return self.content.symbol

    @property
    def is_closed(self):
        """
        True - если ячейка закрыта. Ячейка с флагом, хоть фактически и закрыта,
        возращаем False для более ясной логики solver-ов
        :return:
        """
        return True if self.content == closed else False

    @property
    def is_flag(self):
        return True if self.content == flag else False

    @property
    def is_bomb(self):
        # Бомбы, которые видны после проигрыша
        return True if self.content in bombs else False

    @property
    def is_mine(self):
        # Является ли миной. Мина определенны в матрце. Используется в сапере Tk.
        return self.matrix.is_mine(self)

    @property
    def is_digit(self):
        return True if self.content in digits else False

    @property
    def is_empty(self):
        return True if self.content == n0 else False

    @property
    def is_open(self):
        return True if self.content in open_cells else False

    @property
    def is_noguess(self):
        return True if self.content == noguess else False

    def set_flag(self):
        self.content = flag

    def remove_flag(self):
        self.content = closed

    def set_mine(self):
        """
        Только для Tk
        Sets a mine in this cell by adding its coordinates to the matrix's mines set.
        """
        self.matrix.mines.add((self.row, self.col))

    def remove_mine(self):
        """
        Только для Tk
        Removes a mine from this cell by removing its coordinates from the matrix's mines set.
        """
        self.matrix.mines.discard((self.row, self.col))

    def click(self, button):
        """
        Нажимает на ячейку.
        Если mouse_randomize_xy = true, то каждый раз немного рандомные координаты
        :return:
        """
        if config.mouse_randomize_xy:
            x, y = random_point_in_square(self.abscoordx, self.abscoordy, self.w, self.h)
        else:
            x, y = self.abscoordx + self.w//2, self.abscoordy + self.h//2
        mouse_controller.click(x, y, button)

    @property
    def digit(self) -> int | None:
        """
        Возвращает цифру ячейки в виде int. Если ячейка - не цифра, возвращает None.
        :return: int
        """
        if self.content in digits:
            return int(self.content.value)

    def hashing(self):
        """
        Возвращает хэш изображения ячейки.
        Используется при сканировании поля, чтобы понять, изменилась ли ячейка.
        :return:
        """
        c = self.image.copy(order='C')
        h = xxhash.xxh64()
        h.update(c)
        intdigits = h.intdigest()
        return intdigits

    def update_cell(self, crop):
        """
        Обновляет содержимое ячейки в соответствии с полем Minesweeper
        :param crop: актуальное изображение ячейки
        :return: None
        """
        self.image = crop
        new_hash = self.hashing()
        if self.hash != new_hash:
            self.hash = new_hash

            precision = 0.8

            for pattern in all_cell_types:  # list_patterns imported from cell_pattern
                template = pattern.raster
                res = cv.matchTemplate(crop, template, cv.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
                # print(f'Cell {self.row}:{self.col} compared with <{pattern.name}> with result {max_val}')
                pattern.similarity = max_val
                if max_val > precision:
                    self.content = pattern
                    # deprecated
                    # self.status = pattern.name
                    break

            # deprecated
            # был вариант находить для каждого паттерна индекс "похожести" и выбирать наибольший
            # но по сути все совпадения имеют индекс более 0,9999 или 1,0, так что нет смысла заморачиваться
            # best_match = sorted(list_patterns, key=lambda x: x.similarity, reverse=True)[0]
            # print(best_match.similarity)
            # if best_match.similarity > precision:
            #     self.status = best_match.name

            else:  # если перебор for не дал результатов
                print(f'Update board: Cell {self.row}x{self.col} do not match anything. Exit')
                exit()

    def point_in_cell(self, point):
        """
        Проверяет, входит ли точка с координатами на экране (point) в данную ячейку
        :param point: tuple (x, y)
        :return: bool
        """
        if point_in_rect(point, self.abscoordx, self.abscoordy, self.w, self.h):
            return True
        else:
            return False

    def mark_cell_debug(self, color: Color, dist=6, size=8):
        """
        Used for debug.
        Draw small square on current cell right on Minesweeper board,
        with edge `size` px and distance from top left corner `dist`.
        :return:
        """
        # select = {
        #     'red': win32api.RGB(255, 0, 0),
        #     'green': win32api.RGB(0, 255, 0),
        #     'blue': win32api.RGB(0, 0, 255),
        #     'yellow': win32api.RGB(255, 255, 0),
        #     'cyan': win32api.RGB(0, 255, 255),
        #     'magenta': win32api.RGB(255, 0, 255),
        # }

        dc = win32gui.GetDC(0)
        rect = (self.abscoordx+dist, self.abscoordy+dist, self.abscoordx+dist+size, self.abscoordy+dist+size)

        # win32gui.SetBkColor(dc, red)
        # win32gui.Rectangle(dc, self.abscoordx+6, self.abscoordy+6, self.abscoordx+18, self.abscoordy+18)

        brush = win32gui.CreateSolidBrush(color)
        win32gui.FillRect(dc, rect, brush)

        # win32gui.MoveToEx(dc, self.abscoordx+9, self.abscoordy+9)
        # win32gui.LineTo(dc, self.abscoordx+9, self.abscoordy+9)
