import random
import cv2 as cv
import util
import win32gui
import win32api

from patterns import patterns
from config import config


class Cell(object):

    ident_right = 0  # class property
    ident_top = 0    # class property
    col = 0
    row = 0
    coordx = 0
    coordy = 0
    w = 0
    h = 0
    status = ''
    type = None  # Pattern instance

    def __init__(self, row, col, coordx, coordy, w, h):
        """
        :param col: номер ячейки в строке, начиная с 0. Т.е. это СТОЛБЕЦ. Левая ячейка - номер 0 - cell[строка][столбец]
        :param row: номер ячейки в столбце, начиная с 0. Т.е. это СТРОКА. Верхняя ячейка - номер 0
        :param coordx: коор. на экране X от левого верхнего угла ДОСКИ в пикселях
        :param coordy: коор. на экране Y от левого верхнего угла ДОСКИ в пикселях
        :param w: ширина ячейки в пикселях
        :param h: высота ячейки в пикселях
        :param status: (str) 'closed' закрыто / 'opened' открыто / 'flag' флаг / digit(str)

        POSSIBLE STATUS:
        str - closed (default)
        str - flag
        str - bomb (for reflect endgame)
        str - digit, represent digit of around bomb

        """
        self.col = col
        self.row = row
        self.coordx = coordx
        self.coordy = coordy
        self.w = w
        self.h = h
        self.status = 'closed'
        self.type = patterns.closed


    def cell_pict(self):
        # TODO Сделать еще одно поле - TYPE с типом Pattern, и здесь
        # TODO возвращать просто self.type.represent
        # TODO в общем, нужно ВСЕ проверки self.status как строки заменить на проверки
        # TODO self.type как объекта
        if self.status == 'closed':
            slot = '·'  # ·ᐧ    # more bad ․⋅
        elif self.status == 'flag':
            slot = '⚑'
        elif self.status == 'bomb':
            slot = '⚹'
        elif self.status.isnumeric():
            if self.status == '0':
                slot = ' '  # ⨯·
            else:
                slot = self.status
        else:
            return 'e'  # error
        return slot
        # return slot+f'{self.row}:{self.col}'

    def __repr__(self):
        return f'{self.row}:{self.col} {self.status}'

    @property
    def abscoordx(self):
        return self.coordx + self.ident_right

    @property
    def abscoordy(self):
        return self.coordy + self.ident_top

    @property
    def is_closed(self):
        """
        True - если ячейка закрыта. Ячейка с флагом, хоть фактически и закрыта,
        возращаем False для более ясной логики solver-ов
        :return:
        """
        # if self.status == 'closed' or self.status == 'flag':
        #     return True
        # else:
        #     return False
        return True if self.status == 'closed' else False

    @property
    def is_flag(self):
        return True if self.status == 'flag' else False

    @property
    def is_not_flag(self):
        return not self.is_flag


    @property
    def is_bomb(self):
        return True if self.status == 'bomb' else False

    @property
    def is_digit(self):
        if self.status in ['1', '2', '3', '4', '5', '6', '7', '8']:
            return True
        return False

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
        Нажимает на ячейку.
        Если randomize_mouse, то каждый раз немного рандомно
        :return:
        """
        # TODO уродский код - и тут и в cell_random_coordinates, надо переделать!
        if config.randomize_mouse:
            x, y = self.cell_random_coordinates()
        else:
            x, y = self.coordx + self.w//2, self.coordy + self.h//2
        x += Cell.ident_right
        y += Cell.ident_top
        util.click(x, y, button)

    """
    possible depricated
    def setflag(self):
        self.click('right')

    def setclear(self):
        self.click('left')
    """

    @property
    def digit(self):
        """
        Возвращает цифру ячейки в виде int. Иначе возвращает -1
        :return: int
        """
        if self.status.isnumeric():
            return int(self.status)
        else:
            return -1

    def update_cell(self, image):
        """
        Обновляет содержимое ячейки в соответствии с полем Minesweeper
        :param image: текущее изображение поля игры, после нажатия на клетку
        :return:
        """

        # image_cell содержит пиксельную матрицы соотв. ячейки
        image_cell = image[self.coordy:self.coordy+self.h, self.coordx:self.coordx+self.w]

        precision = 0.8

        # конвертируем объект SimpleNamespace, который по сути обертка для dict, в список.
        # Потому что dict не итерируемый, а здесь нам нужен перебор, и в цикле и при сортировке чуть дальше
        list_patterns = []
        for name, obj in patterns.__dict__.items():
            list_patterns.append(obj)

        # TODO какая есть мысля ускорить процесс
        # TODO нужно уменьшить кол-во выполнения этого цикла, путем прерываения при нахождении
        # TODO какого-то процента совпадения. Сначала нужно сравнивать с открытой и закрытой ячейками, потом с остальными.

        for patt in list_patterns:  # patterns imported from cell_pattern
            template = patt.raster
            res = cv.matchTemplate(image_cell, template, cv.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
            # print(f'Cell {self.row}:{self.col} compared with {pattern} with result {max_val}')
            patt.similarity = max_val

        best_match = sorted(list_patterns, key=lambda x: x.similarity, reverse=True)[0]

        if best_match.similarity > precision:
            self.status = best_match.name
        else:
            print(f'Cell {self.row}x{self.col} do not match anything. Exit')
            exit()

    def mark_cell_debug(self):
        dc = win32gui.GetDC(0)
        red = win32api.RGB(255, 0, 0)
        # win32gui.SetPixel(dc, 0, 0, red)  # draw red at 0,0
        win32gui.Rectangle(dc, self.abscoordx+6, self.abscoordy+6,
                           self.abscoordx+18, self.abscoordy+18)

        win32gui.MoveToEx(dc, self.abscoordx+9, self.abscoordy+9)
        win32gui.LineTo(dc, self.abscoordx+9, self.abscoordy+9)
        # win32gui.ReleaseDC(dc)
        # dc.Clear()
        # dc.Refresh()
