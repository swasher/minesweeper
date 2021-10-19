import numpy
import random
import pyautogui
import mss
import numpy as np
import cv2 as cv
import util
from pprint import pprint


class Matrix(object):
    table = None
    region_x1 = 0
    region_y1 = 0
    region_x2 = 0
    region_y2 = 0
    len_x = 0
    len_y = 0

    def __init__(self, num_rows, num_cols):
        """
        Заполняет Matrix пустыми объектами Cell
        :param num_rows:
        :param num_cols:
        """
        self.table = numpy.full((num_rows, num_cols), Cell)
        self.len_x = num_cols
        self.len_y = num_rows

    def display(self):
        """
        Выводит в консоль текущее изображение поля (матрицу)
        :return: Возвращает матрицу типа array of strings
        """
        print('---DISPLAY---')
        m = []
        for y in range(self.len_y):
            row = ''
            for x in range(self.len_x):
                row += str(self.table[x][y])
            m.append(row)
        print('\n'.join(row for row in m))
        return m

    def get_image(self):
        """
        Возвращает текущее изображение поля игры
        :return: opencv image
        """
        with mss.mss() as sct:
            # from file (for test)
            # image = cv.imread('pic/test_big.png', cv.IMREAD_COLOR)

            # from screen
            screenshot = sct.grab(self.region())
            raw = np.array(screenshot)
            image = cv.cvtColor(raw, cv.COLOR_RGB2BGR)
            # cv.imshow("Display window", raw)
            # k = cv.waitKey(0)
        return image

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
        ic('Start update matrix...')
        image = self.get_image()
        image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
        for y in range(self.len_y):
            for x in range(self.len_x):
                self.table[x][y].update_cell(image)
        ic('  finish')

    def face_is_fail(self):
        """
        :return: True если рожица грустая, иначе False
        """
        precision = 0.53
        image = self.get_image()
        template = cv.imread('pic/smile_fail.png', cv.IMREAD_COLOR)
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
    а в результате вычислений уже не понять, где была первоначальная ячейка.  
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

    def get_around_cells(self, col, row):
        """
        see test/around_cell.py for explain
        :param col:
        :param row:
        :return: array of cells around (x,y)
        """
        arr = self.table
        cells = []
        x1, x2 = self.get_slice(col, arr.shape[1])
        y1, y2 = self.get_slice(row, arr.shape[0])

        for y in range(y1, y2):
            for x in range(x1, x2):
                if x == col and y == row:
                    continue
                else:
                    cells.append(arr[y, x])
        return cells

    def count_closed(self, col, row):
        cells = self.get_around_cells(col, row)
        count = 0
        for cell in cells:
            if cell.is_closed:
                count += 1
        return count


class Cell(Matrix):
    x = 0
    y = 0
    coordx = 0
    coordy = 0
    h = 0
    w = 0
    status = ''       # False - закрытая ячейка, True - открытая ячейка
    number = 0        # для открытой ячейки показывает число на ней
    # deprecated flag = False    # если True, то ячейка помечена как потенциально с бомбой

    def __init__(self, x, y, coordx, coordy, w, h):
        """
        :param x: номер ячейки в строке, начиная с 0. Т.е. это СТОЛБЕЦ. Левая ячейка - номер 0    cell[столбец][строка]
        :param y: номер ячейки в столбце, начиная с 0. Т.е. это СТРОКА. Верхняя ячейка - номер 0
        :param coordx: коор. X от левого верхнего угла
        :param coordy: коор. Y от левого верхнего угла
        :param w: ширина ячейки
        :param h: высота ячейки
        :param status: (str) 'closed' закрыто / 'opened' открыто / 'flag' флаг / number(str)

        POSSIBLE STATUS:
        str - closed (default)
        str - flag
        str - bomb (for reflect endgame)
        str - number, represent number of around bomb

        """
        self.x = x
        self.y = y
        self.coordx = coordx
        self.coordy = coordy
        self.w = w
        self.h = h
        self.status = 'closed'

    def __repr__(self):
        if self.status == 'closed':
            return '·'  # ·ᐧ    # more bad ․⋅
        elif self.status == 'flag':
            return '⚑'
        elif self.status == 'bomb':
            return '⚹'
        elif self.status.isnumeric():
            if self.status == '0':
                return '⨯'  # ⨯·
            else:
                return self.status

    @property
    def is_closed(self):
        if self.status == 'closed':
            return True
        else:
            return False

    @property
    def is_not_flag(self):
        if self.status == 'flag':
            return False
        else:
            return True

    @property
    def is_open(self):
        return not self.is_closed

    @property
    def is_not_zero(self):
        if self.status != 'closed':
            if self.status.isnumeric() and self.status == '0':
                return False
        return True

    def cell_random_coordinates(self):
        """
        :return: Координаты для клика с учетом рандомизации внутри ячейки
        """
        xstart = self.coordx
        xend = xstart + self.w
        edge_x = int(self.w*0.2)
        coord_x = random.randint(xstart + edge_x, xend - edge_x)

        ystart = self.coordy
        yend = ystart + self.h
        edge_y = int(self.h*0.2)
        coord_y = random.randint(ystart + edge_y, yend - edge_y)
        return coord_x, coord_y

    def click(self, button):
        """
        нажимает на ячейку, каждый раз немного рандомно
        :return:
        """
        x, y = self.cell_random_coordinates()
        x += Matrix.region_x1
        y += Matrix.region_y1
        util.click(x, y, button)

    def update_cell(self, image):
        """
        Обновляет содержимое ячейки в соответствии с полем Minesweeper
        :param image:
        :return:
        """
        values = range(0, 7) ## + ЗАКРЫТОЕ ПОЛЕ

        # TODO нет смысла проверять уже открытые ячейки - можно скипать

        # ТУТ НАМ НУЖНО СРАВНИВАТЬ НЕ ТОЛЬКО С ЦИФРАМИ, НО И С "ЗАКРЫТЫМ" ПОЛЕМ
        # ПРОБЛЕМА ЕЩЕ В ТОМ, ЧТО ОТКРЫТОЕ И ЗАКРЫТОЕ ПОЛЯ ОЧЕНЬ ПОХОЖИ,
        # ОТЛИЧАЮТСЯ КРАЯМИ, А МЫ КРАЯ ОБРЕЗАЕМ

        image_cell = image[self.coordy:self.coordy+self.h, self.coordx:self.coordx+self.w]
        templates = []
        for v in range(0, 7):
            templates.append(f'pic/{v}.png')
        templates.append('pic/closed.png')    # 7
        templates.append('pic/bomb.png')      # 8
        templates.append('pic/red_bomb.png')  # 9
        templates.append('pic/flag.png')      # 10

        precision = 0.8
        result = []
        for f in templates:
            template = cv.imread(f, cv.IMREAD_COLOR)
            # template = cv.imread(f, cv.IMREAD_GRAYSCALE)
            res = cv.matchTemplate(image_cell, template, cv.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
            # fail.png - совпадение со smile - 0.48, с fail - 0.57
            # print(f'Cell {self.x}:{self.y} compared with {v} with result {max_val}')
            result.append(max_val)

        if max(result) > precision:
            answer = result.index(max(result))
            if answer == 7:                   # cell is closed
                pass
            elif answer == 8 or answer == 9:  # cell is bomb (game over)
                self.status = 'bomb'
            elif answer == 10:
                self.status = 'flag'          # mark cell as flag
            else:
                self.status = str(answer)
        else:
            print(f'Cell {self.x}x{self.y} do not match anything. Exit')
            exit()
