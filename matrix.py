import functools
import math
import operator
import time
import win32gui
import win32con
import cv2 as cv
import mss
import mss.tools
import numpy
import numpy as np

import asset
import cell
import maus
import util
from board import board
from config import config

"""
Соглашения:
get_closed - возвращает только закрытые и НЕ отмеченные флагами
"""


class Matrix(object):

    table = None  # matrix itself; numpy 2D array of Cell object
    height = 0  # height of matrix (number of rows)
    width = 0  # width of matrix (number of cols)

    def __init__(self, row_values, col_values, region):
        """
        Заполняет Matrix пустыми объектами Cell
        :param num_rows:
        :param num_cols:
        """
        self.region_x1, self.region_y1, self.region_x2, self.region_y2 = region

        self.image = self.get_image()
        self.height = len(row_values)
        self.width = len(col_values)

        self.table = numpy.full((self.height, self.width), cell.Cell)

        template = asset.closed.raster
        h, w = template.shape[:2]

        for row, coordy in enumerate(row_values):  # cell[строка][столбец]
            for col, coordx in enumerate(col_values):
                abscoordx = coordx + self.region_x1
                abscoordy = coordy + self.region_y1
                c = cell.Cell(row, col, coordx, coordy, abscoordx, abscoordy, w, h)
                image_cell = self.image_cell(c)
                c.image = image_cell
                c.update_cell(image_cell)  # нужно делать апдейт, потому что при простом старте у нас все ячейки закрыты, а если мы загружаем матрицу их Pickle, нужно ячейки распознавать.
                c.hash = c.hashing()
                self.table[row, col] = c

        self.lastclicked = self.table[0, 0]

    def cell_distance(self, cell1, cell2) -> float:
        d = math.hypot(cell1.row - cell2.row, cell1.col - cell2.col)
        return d

    def display(self):
        """
        Выводит в консоль текущее изображение поля (матрицу)
        :return: Возвращает матрицу типа array of strings
        """
        print('---DISPLAY---')
        matrix_view = []
        for row in range(self.height):
            row_view = ''
            for col in range(self.width):
                row_view += self.table[row, col].cell_pict() + ' '
            matrix_view.append(row_view)
        print('\n'.join(row for row in matrix_view))
        return matrix_view

    def get_image(self):
        """
        Возвращает текущее изображение поля игры
        :return: opencv image
        """
        with mss.mss() as sct:
            """
            Чтобы уже раз и на всегда закрыть вопрос:
            sct.grab отдает в формате BGRA.
            Мы его конвертим просто в BGR. Никаких RGB не нужно!
            Плагин pycharm'а показывает цвет правильно, только и когда он в BGR !!!
            А RGB показывает инвертно!
            Можно убедиться наведя пипетку на красный цвет и посмотрев, где R - 255
            """
            screenshot = sct.grab(self.region)
            raw = np.array(screenshot)
            image = cv.cvtColor(raw, cv.COLOR_BGRA2BGR)
        return image

    def around_cells(self, cell):
        """
        Возвращает список ячеек, расположенных вокруг (вкл. диагонали) заданой. Проблема в том, что нельзя просто
        вернуть "минус одна ячейка вправо, плюс одна влево", потому что у крайних ячеек возникнет IndexError.
        Поэтому есть вспомогательная функция get_slice, которая возвращаем "правильный" отрезок по оси.
        :param cell: instance of Cell class
        :return: array of Cell objects
        """

        def get_slice(v, len_axis):
            """
            Вычисляет правильный "отрезок" соседних клеток. Например для оси длиной 5 [0, 1, 2, 3, 4] для
            координаты 2 вернет [1, 2, 3], а для координаты 4 вернет [3, 4]
            :param v: координата
            :param len_axis: длина оси
            :return:
            """
            if v not in range(len_axis):
                raise Exception('`get_proper_area` function - out of matrix range')
            if v == 0:
                return 0, v + 2
            elif v == len_axis - 1:
                return v - 1, v + 1
            else:
                return v - 1, v + 2

        cells = []
        rows, cols = self.table.shape

        c1, c2 = get_slice(cell.col, cols)
        r1, r2 = get_slice(cell.row, rows)

        for row in range(r1, r2):
            for col in range(c1, c2):
                if col == cell.col and row == cell.row:
                    continue
                else:
                    cells.append(self.table[row, col])
        return cells

    def around_closed_cells(self, cell):
        """
        Возвращает список закрытых ячеек вокруг ячейки cell.
        Флаги не считаются закрытыми ячейками.
        :param cell: instance of Cell class
        :return: array of Cell instances
        """
        closed_cells = list([x for x in self.around_cells(cell) if x.is_closed])
        return closed_cells

    def around_flagged_cells(self, cell):
        """
        Возвращает список ячеек-флагов вокруг ячейки cell
        :param cell: instance of Cell class
        :return: array of Cell instances
        """
        flagged_cells = list([x for x in self.around_cells(cell) if x.is_flag])
        return flagged_cells

    def around_digit_cells(self, cell):
        """
        Возвращает список ячеек-цифр вокруг ячейки cell
        :param cell: instance of Cell class
        :return: array of Cell instances
        """
        flagged_cells = list([x for x in self.around_cells(cell) if x.is_digit])
        return flagged_cells

    def get_closed_cells(self):
        """
        Возвращает все закрытые ячейки (которые закрыты и НЕ отмечены флагом)
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_closed])
        return cells

    def get_flag_cells(self):
        """
        Возвращает список закрытых ячеек, уже помеченных флагами
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_flag])
        return cells

    def get_digit_cells(self):
        """
        Возвращает список открытых ячеек (без нулевых ячеек)
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_digit])
        return cells

    def get_open_cells(self):
        """
        Возвращает список открытых ячеек (включая нули).
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_open])
        return cells

    def get_bomb_cells(self):
        """
        Возвращает список бомб. Используется в game_over
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_bomb])
        return cells

    def get_noguess_cell(self):
        """
        Первый ход для no-guess игр. Возвращает отмеченную крестиком клетку.
        :return: list of Cell objects
        """
        cell = list([x for x in self.table.flat if x.is_noguess])
        return cell

    @property
    def region(self):
        """
        Возвращает объект типа PIL bbox всего поля игры, включая рамки.
        :return: array of int
        """
        return self.region_x1, self.region_y1, self.region_x2, self.region_y2

    def image_cell(self, cell):
        """
        вырезает из image сооветствующую ячейку.
        :return: ndarray (image)
        """
        return self.image[cell.coordy:cell.coordy+cell.h, cell.coordx:cell.coordx+cell.w]

    def update(self):
        """
        Запускает обновление всех ячеек, считывая их с экрана (поле Minesweeper'а)
        :return:
        """
        # This is very important string! After click, website (and browser, or even Vienna program) has a lag
        # beetween click and refreshing screen.  If we do not waiting at this point, our code do not see any changes
        # after mouse click.
        time.sleep(config.LAG)

        self.image = self.get_image()
        for cell in self.get_closed_cells():
            crop = self.image_cell(cell)
            cell.update_cell(crop)

    @property
    def you_fail(self):
        """
        Если в матрице есть бомбы - то FAIL
        :return:
        """
        bombs = self.get_bomb_cells()
        if bool(len(bombs)):
            # print('You lose!')
            return True
        return False

    @property
    def you_win(self):
        """
        Если смайлик = веселый, то WIN
        :return: boolean
        """
        precision = 0.9
        image = self.get_image()
        template = asset.win.raster

        res = cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

        if max_val > precision:
            # print('You WIN!\n')
            return True

        return False

    @property
    def bomb_qty(self) -> int:
        """
        Возвращает число, которое на игровом поле на счетчике бомб (сколько еще спрятанных бомб на поле)
        :return:
        """
        image = self.get_image()
        # TODO нарушена логика - это должно быть в абстракции конкретной реализаии сапера.
        #      перенести это в board
        crop_img = image[0:board.border['top'], 0:(self.region_x2 - self.region_x1) // 2]

        # precision = 0.94
        # precision = 0.837

        # для Minesweeper online я подбирал значения;
        # дома, на 1920х1080 (zoom 24) работает 0,837 (до сотых).
        # Если больше (0,84) - он не "узнает" паттерны. Если меньше (0,8) - возникают ложные срабатывания,
        # например, 7 может распознать как 1.
        # НА САМОМ ДЕЛЕ, PRECISION ПОДОБРАН В search_pattern_in_image_for_red_bombs

        found_digits = []
        for pattern in asset.red_digits:  # list_patterns imported from cell_pattern
            template = pattern.raster

            # result = util.find_templates(template, crop_img, precision)
            result = util.search_pattern_in_image_for_red_bombs(template, crop_img)

            # `result` - это list of tuple
            # каждый кортеж содержит список из трех числ:
            # координаты найденной цифры - x и y, и с какой точностью определилась цифра. Напр.
            # [(19, 66, 1.0), (32, 66, 0.998)]
            for r in result:
                found_digits.append((r[0], pattern.value))

        # сортируем найденные цифры по координате X
        digits = sorted(found_digits, key=lambda a: a[0])

        if not digits:
            # raise Exception('Не удалось прочитать кол-во бомб на поле.')
            return None

        _, numbers = zip(*digits)
        bomb_qty: int = int(''.join(map(str, numbers)))
        return bomb_qty

    def cell_by_abs_coords(self, point):
        """
        Возвращает ячейку, которая содержит данную точку (по абсолютным координатам на экране)
        :param point: (x, y)
        :return: Cell object
        """
        for cell in self.table.flat:
            if cell.point_in_cell(point):
                return cell
        else:
            return None

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
        maus.click(face_coord_x, face_coord_y, maus.OPEN)
        for c in self.table.flat:
            # deprecated
            # c.status = 'closed'
            c.type = asset.closed
        # todo тут прибито гвоздями. Нужно ждать некоторое время, пока поле обновится.
        #      онлайну подходит 0,1*3
        #      vienne
        time.sleep(config.reset_pause)

    def show_debug_text(self):
        """
        Показывает текст на ячейках, который содержится в каждой ячейке в debug_text.
        Убирает текст после нажатия любой клавиши.
        :return:
        """
        dc = win32gui.GetDC(0)
        for row in self.table:
            for cell in row:
                if cell.debug_text is not None:
                    rect = (cell.abscoordx, cell.abscoordy, cell.abscoordx+cell.w, cell.abscoordy+cell.h)
                    win32gui.DrawText(dc, cell.debug_text, -1, rect, win32con.DT_LEFT)
                cell.debug_text = None

        im = self.get_image()
        cv.imwrite('screenshot2.png', im)

        input("Press Enter to continue")

        win32gui.ReleaseDC(0, dc)