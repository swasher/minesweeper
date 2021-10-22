import numpy
import mss
import numpy as np
import cv2 as cv
import util
from icecream import ic
import cell

from patterns import patterns


class Matrix(object):

    def __init__(self, row_values, col_values, region, patterns):
        """
        Заполняет Matrix пустыми объектами Cell
        :param num_rows:
        :param num_cols:
        """
        self.matrix_height = len(row_values)
        self.matrix_width = len(col_values)

        self.table = numpy.full((self.matrix_height, self.matrix_width), cell.Cell)

        # TODO это нужно брать из класса Cell_pattern
        template = cv.imread(patterns.closed.filename, cv.IMREAD_COLOR)
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
        for row in range(self.matrix_height):
            row_view = ''
            for col in range(self.matrix_width):
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
            # from file (for test)
            # image = cv.imread('pic/test_big.png', cv.IMREAD_COLOR)

            # from screen
            screenshot = sct.grab(self.region)
            raw = np.array(screenshot)
            image = cv.cvtColor(raw, cv.COLOR_RGB2BGR)
            # cv.imshow("Display window", raw)
            # k = cv.waitKey(0)
        return image

    def get_closed_cells(self):
        """
        Возвращает все закрытые ячейки
        :return:
        """
        cells = []
        for row in range(self.matrix_height):
            for col in range(self.matrix_width):
                cell = self.table[row, col]
                if cell.is_closed:
                    cells.append(cell)
        return cells

    def number_cells(self):
        cells = []
        for row in range(self.matrix_height):
            for col in range(self.matrix_width):
                cell = self.table[row, col]
                if cell.is_open and cell.is_not_zero:
                    cells.append(cell)
        return cells


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
        ic('update matrix...')
        image = self.get_image()
        image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
        for row in range(self.matrix_height):
            for col in range(self.matrix_width):
                self.table[row, col].update_cell(image)

        if self.face_is_fail:
            exit()


    @property
    def face_is_fail(self):
        """
        :return: True если рожица грустая, иначе False
        """
        precision = 0.53
        image = self.get_image()
        template = cv.imread(patterns.fail.filename, cv.IMREAD_COLOR)
        res = cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        # fail.png - совпадение со smile - 0.48, с fail - 0.57
        if max_val < precision:
            return False
        else:
            print('Game Over!')
            return True

    def reset(self):
        """
        Нажимает на рожицу, чтобы перезапустить поле
        TODO BUG Рожицы нет на маленьких полях
        :return:
        """
        face_coord_x = (self.region_x2 - self.region_x1)//2 + self.region_x1
        face_coord_y = self.region_y1 + 40
        util.click(face_coord_x, face_coord_y, 'left')


    """
    Работает, дает "правильный" срез матрицы с учетом границ.
    ПРоблема в том, что возвращает так же центральную ячейку, 
    а в готовом срезе уже не понять, где была первоначальная ячейка.  
    def get_proper_area(self, v, len_axis):
        if v not in range(len_axis):
            raise Exception('`get_proper_area` function - out of matrix range')
        if v == 0:
            return 0, v + 2
        elif v == len_axis:
            return v - 1, v + 1
        else: return v - 1, v + 2

    def get_around_cells(self, x, y):
        x1, x2 = self.get_proper_area(x, self.count_x)
        y1, y2 = self.get_proper_area(x, self.count_y)

        square = self.table[y1:y2, x1:x2]
        return square


        # for row in [x - 1, x, x + 1]:
        #     for col in [y - 1, y, y + 1]:
        #         if (row not in range(matrix.count_x)) \
        #                 or (col not in range(matrix.count_y)) \
        #                 or (row == x and col == y):
        #             continue
        # return cells
    """

    def get_slice(self, v, len_axis):
        if v not in range(len_axis):
            raise Exception('`get_proper_area` function - out of matrix range')
        if v == 0:
            return 0, v + 2
        elif v == len_axis - 1:
            return v - 1, v + 1
        else:
            return v - 1, v + 2

    def get_around_cells(self, cell):
        """
        see test/around_cell.py for explain
        :param col:
        :param row:
        :return: array of cells around (x,y)
        """
        # arr = self.table
        cells = []
        rows, cols = self.table.shape

        # TODO переделать, чтобы не передавать номера строк/стобов, а ячейку
        # TODO сделать типа def get_X_neighbours(cell)

        c1, c2 = self.get_slice(cell.col, cols)
        r1, r2 = self.get_slice(cell.row, rows)

        for row in range(r1, r2):
            for col in range(c1, c2):
                if col == cell.col and row == cell.row:
                    continue
                else:
                    cells.append(self.table[row, col])
        return cells

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
            if cell.is_closed:
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
