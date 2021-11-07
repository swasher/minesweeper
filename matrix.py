import numpy
import mss
import numpy as np
import cv2 as cv
import util
import time
from icecream import ic

import cell
from config import config
from asset import Asset
from asset import patterns
from asset import red_digits



"""
Соглашения:
get_closed - возвращает только закрытые и НЕ отмеченные флагами
"""


class Matrix(object):

    table = None  # matrix itself; numpy 2D array of Cell object
    height = 0  # height of matrix (number of rows)
    width = 0  # width of matrix (number of cols)

    def __init__(self, row_values, col_values, region, patterns):
        """
        Заполняет Matrix пустыми объектами Cell
        :param num_rows:
        :param num_cols:
        """
        self.height = len(row_values)
        self.width = len(col_values)

        self.table = numpy.full((self.height, self.width), cell.Cell)

        template = patterns.closed.raster
        h, w = template.shape[:2]

        self.region_x1, self.region_y1, self.region_x2, self.region_y2 = region
        cell.Cell.ident_right = self.region_x1
        cell.Cell.ident_top = self.region_y1

        for row, coordy in enumerate(row_values):  # cell[строка][столбец]
            for col, coordx in enumerate(col_values):
                c = cell.Cell(row, col, coordx, coordy, w, h)
                self.table[row, col] = c

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
            Чтобы уже раз и на всегда решить вопрос:
            sct.grab отдает в формате BGRA.
            Мы его конвертим просто в BGR. Никаких RGB не нужно!
            Планин pycharm'а показывает цвет правильно, только и когда он в BGR !!!
            А RGB показывает инвертно!
            Можно убедиться наведя пипетку на красный цвет и посмотрев, где R - 255
            """

            # from screen
            screenshot = sct.grab(self.region)
            raw = np.array(screenshot)
            image = cv.cvtColor(raw, cv.COLOR_BGRA2BGR)
        return image

    def get_around_cells(self, cell):
        """
        Возвращает список ячеек, расположенных вокруг (вкл. диагонали) заданой. Проблема в том, что нельзя просто
        вернуть "минус одна ячейка вправо, плюс одна влево", потому что у крайних ячеек возникнет IndexError.
        Поэтому есть вспомогательная функция get_slice, которая возвращаем "правильный" отрезок по оси.
        :param col:
        :param row:
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

    def get_closed_cells(self):
        """
        Возвращает все закрытые ячейки (которые закрыты и НЕ отмечены флагом)
        :return: array of Cell objects
        """
        cells = []
        for cell in self.table.flat:
            if cell.is_closed:
                cells.append(cell)
        return cells

    def get_flag_cells(self):
        """
        Возвращает список закрытых ячеек, уже помеченных флагами
        :return: array of Cell objects
        """
        cells = []
        for cell in self.table.flat:
            if cell.is_flag:
                cells.append(cell)
        # TODO функции get_какая_то_ячейка похожи, их надо объеденить в одну
        # TODO c передаваемам параметром типа get_cells(bomb)
        return cells

    def get_digit_cells(self):
        """
        Возвращает список открытых ячеек (отличных от 0)
        :return: array of Cell objects
        """
        cells = []
        for cell in self.table.flat:
            if cell.is_digit:
                cells.append(cell)
        return cells

    def get_bomb_cells(self):
        """
        Возвращает список бомб. Используется в game_over
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_bomb])
        return cells

    def get_open_cells(self):
        """
        Возвращает список открытых ячеек (включая нули).
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_open])
        return cells

    def get_noguess_cell(self):
        """
        Первый ход для no-guess игр. Возвращает отмеченную крестиком клетку.
        :return: list of Cell objects
        """
        cell = list([x for x in self.table.flat if x.is_noguess])
        return cell

    def around_closed_cells(self, cell):
        """
        Возвращает число закрытых ячеек вокруг ячейки cell.
        Флаги не считаются закрытыми ячейками.
        :param cell: instance of Cell class
        :return: closed_cells - array of Cell instances
        """
        cells = self.get_around_cells(cell)
        closed_cells = []
        for cell in cells:
            if cell.is_closed and cell.is_not_flag:
                closed_cells.append(cell)
        return closed_cells

    def around_flagged_cells(self, cell):
        """
        Возвращает число флагов вокруг ячейки cell
        :param cell: instance of Cell class
        :return: flagged_cells - array of Cell instances
        """
        cells = self.get_around_cells(cell)
        flagged_cells = []
        for cell in cells:
            if cell.is_flag:
                flagged_cells.append(cell)

        return flagged_cells

    @property
    def region(self):
        """
        Возвращает объект типа PIL bbox всего поля игры, включая рамки.
        :return: array of int
        """
        return self.region_x1, self.region_y1, self.region_x2, self.region_y2

    def update(self):
        """
        Запускает обновление всех ячеек в соответствии с полем Minesweeper
        :return:
        """
        # This is very important setting! After click, website has a lag for refresh game board.
        # If we do not waiting at this point, we do not see any changes after mouse click.
        if Asset.LAG:
            time.sleep(Asset.LAG)

        image = self.get_image()
        for cell in self.get_closed_cells():
            cell.update_cell(image)

    @property
    def you_fail(self):
        """
        Если в матрице есть бомбы - то FAIL
        :return:
        """
        bombs = self.get_bomb_cells()
        if bool(len(bombs)):
            print('You lose!')
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
        template = patterns.win.raster

        res = cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

        if max_val > precision:
            print('You WIN!\n')
            return True

        return False

    @property
    def bomb_counter(self):
        """
        3 - плохо
        4 - плохо
        5 - 0.99
        6 - 1.0
        7 - 1.0
        9 - 0.89 (((
        :return:
        """
        precision = 0.9
        image = self.get_image()
        # TODO нарушена логика - это должно быть в абстракции конкретеной реализаии минера
        crop_img = image[0:Asset.border['top'], 0:(self.region_x2 - self.region_x1) // 2]

        # cv.imshow("cropped", crop_img)
        # cv.waitKey(0)

        # for patt in red_digits:
        #     cells_coord_x, cells_coord_y = util.scan_image(crop_img, patt.raster)
        #     if len(cells_coord_x)+len(cells_coord_y):
        #         print('---', patt.name)
        #         print('x:', cells_coord_x)
        #         print('y:', cells_coord_y)

        for patt in red_digits:  # list_patterns imported from cell_pattern
            template = patt.raster
            res = cv.matchTemplate(crop_img, template, cv.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
            # print(f'Cell {self.row}:{self.col} compared with {pattern} with result {max_val}')
            patt.similarity = max_val
            print(patt.name, patt.similarity)

        # best_match = sorted(list_patterns, key=lambda x: x.similarity, reverse=True)[0]


        bombs = 0
        print('REST BOMBS:', bombs)
        exit()
        return bombs

    def bomb_counter2(self):
        image = self.get_image()
        # TODO нарушена логика - это должно быть в абстракции конкретеной реализаии минера
        crop_img = image[0:Asset.border['top'], 0:(self.region_x2 - self.region_x1) // 2]
        precision = 0.99
        # for patt in red_digits[::-1]:  # list_patterns imported from cell_pattern
        for patt in red_digits:  # list_patterns imported from cell_pattern
            template = patt.raster
            crop_img = image[0:Asset.border['top'], 0:(self.region_x2 - self.region_x1) // 2]

            # result = util.find_templates(template, crop_img, precision)
            # print(patt.name, result)

            result = util.search_pattern_in_image(template, crop_img, precision)
            print(patt.name, result)

        return result


    def reset(self):
        """
        Нажимает на рожицу, чтобы перезапустить поле
        TODO BUG Рожицы нет в играх на маленьких полях
        :return:


        ТУТ ВСЕ ПРИВЯЗАНО К КОНКРЕТНОЙ РЕАЛИЗАЦИИ
        В VIENNA ВСЕ ПО ДРУГОМУ

        Сделать, чтобы эти настройки брались из asset.
        Пока что мне кажется можно координату X брать как половину поля,
        а Y из ассета
        """

        face_coord_x = (self.region_x2 - self.region_x1)//2 + self.region_x1
        face_coord_y = self.region_y1 + Asset.smile_y_coord
        util.click(face_coord_x, face_coord_y, 'left')
        for c in self.table.flat:
            c.status = 'closed'
            c.type = patterns.closed
        # todo тут прибито гвоздями.
        #      онлайну подходит 0,1*3
        #      vienne
        time.sleep(0.5)
        self.update()
