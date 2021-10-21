import random
import cv2 as cv
import util

from matrix import Matrix
from patterns import patterns


class Cell(Matrix):  # TODO Разобраться, нужно ли тут наследование

    def __init__(self, row, col, coordx, coordy, w, h):
        """
        :param col: номер ячейки в строке, начиная с 0. Т.е. это СТОЛБЕЦ. Левая ячейка - номер 0 - cell[строка][столбец]
        :param row: номер ячейки в столбце, начиная с 0. Т.е. это СТРОКА. Верхняя ячейка - номер 0
        :param coordx: коор. на экране X от левого верхнего угла ДОСКИ в пикселях
        :param coordy: коор. на экране Y от левого верхнего угла ДОСКИ в пикселях
        :param w: ширина ячейки в пикселях
        :param h: высота ячейки в пикселях
        :param status: (str) 'closed' закрыто / 'opened' открыто / 'flag' флаг / number(str)

        POSSIBLE STATUS:
        str - closed (default)
        str - flag
        str - bomb (for reflect endgame)
        str - number, represent number of around bomb

        """
        self.col = col
        self.row = row
        self.coordx = coordx
        self.coordy = coordy
        self.w = w
        self.h = h
        self.status = 'closed'

    def __repr__(self):
        # TODO Сделать еще одно поле - TYPE с типом Pattern, и здесь
        # TODO возвращать просто self.type.represent
        if self.status == 'closed':
            slot = '·'  # ·ᐧ    # more bad ․⋅
        elif self.status == 'flag':
            slot = '⚑'
        elif self.status == 'bomb':
            slot = '⚹'
        elif self.status.isnumeric():
            if self.status == '0':
                slot = '⨯'  # ⨯·
            else:
                slot = self.status
        else:
            return 'e'  # error
        # return slot
        return slot+f'{self.row}:{self.col}'

    @property
    def is_closed(self):
        if self.status == 'closed':
            return True
        else:
            return False

    @property
    def is_flag(self):
        return True if self.status == 'flag' else False

    @property
    def is_not_flag(self):
        return not self.is_flag

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
        x += Cell.ident_right
        y += Cell.ident_top
        util.click(x, y, button)

    def setflag(self):
        self.click('right')

    def setclear(self):
        self.click('left')

    @property
    def number(self):
        """
        Возвращает цифру ячейки в виде int. Иначе возвращает -1
        :return: int
        """
        if self.status.isnumeric():
            return int(self.status.isnumeric())
        else:
            return -1

    def update_cell(self, image):
        """
        Обновляет содержимое ячейки в соответствии с полем Minesweeper
        :param image: текущее изображение поля игры, после нажатия на клетку
        :return:
        """

        # TODO нет смысла проверять уже открытые ячейки - можно скипать

        # ТУТ НАМ НУЖНО СРАВНИВАТЬ НЕ ТОЛЬКО С ЦИФРАМИ, НО И С "ЗАКРЫТЫМ" ПОЛЕМ
        # ПРОБЛЕМА ЕЩЕ В ТОМ, ЧТО ОТКРЫТОЕ И ЗАКРЫТОЕ ПОЛЯ ОЧЕНЬ ПОХОЖИ,
        # ОТЛИЧАЮТСЯ КРАЯМИ, А МЫ КРАЯ ОБРЕЗАЕМ

        # image_cell содержит пиксельную матрицы соотв. ячейки
        image_cell = image[self.coordy:self.coordy+self.h, self.coordx:self.coordx+self.w]

        precision = 0.8

        # конвертируем объект SimpleNamespace, который по сути обертка для dict, в список.
        # Потому что dict не итерируемый, а здесь нам нужен перебор, и в цикле и при сортировке чуть дальше
        list_patterns = []
        for name, obj in patterns.__dict__.items():
            list_patterns.append(obj)

        for patt in list_patterns:  # patterns imported from cell_pattern
            template = cv.imread(patt.filename, cv.IMREAD_COLOR)
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
