import os
import functools
import math
import operator
import time
import win32gui
import win32ui
import win32con
import cv2 as cv
import mss
import random
import secrets
import pickle
import mss.tools
import numpy as np
from itertools import product

import asset
from cell import Cell
import mouse_controller
import util
from datetime import datetime
from board import board
from config import config
from classes import MouseButtons as mb

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
        self.height = height # width of matrix (number of cols)
        self.table = np.full((self.height, self.width), Cell) # matrix itself; numpy 2D array of Cell object
        self.mines = set()  # set of bombs for Tk playing


    def initialize_from_screen(self, row_values, col_values, region):
        """
        Заполняет Matrix пустыми объектами Cell с экрана,
        настраивая взаимосвязь между экраном и Matrix.
        Каждый объект Cell при этом становится привязан к конкретному месту на экране.
        :param row_values: list[int] - список координат верхнего левого угла строк
        :param col_values: list[int] - список координат верхнего левого угла столбцов
        :param region: list[int, int, int, int] - четыре координаты окна
        """
        self.region_x1, self.region_y1, self.region_x2, self.region_y2 = region

        self.image = self.get_image()
        self.height = len(row_values)
        self.width = len(col_values)

        self.table = np.full((self.height, self.width), Cell)

        template = asset.closed.raster
        h, w = template.shape[:2]

        for row, coordy in enumerate(row_values):  # cell[строка][столбец]
            for col, coordx in enumerate(col_values):
                abscoordx = coordx + self.region_x1
                abscoordy = coordy + self.region_y1
                c = Cell(row, col, coordx, coordy, abscoordx, abscoordy, w, h)
                image_cell = self.image_cell(c)
                c.image = image_cell
                c.update_cell(image_cell)  # нужно делать апдейт, потому что при простом старте у нас все ячейки закрыты, а если мы загружаем матрицу из Pickle, нужно ячейки распознавать.
                c.hash = c.hashing()
                self.table[row, col] = c

        self.lastclicked = self.table[0, 0]

    def initialize_without_screen(self, width, height):
        """
        Создаем матрицу со всеми закрытыми ячейками.
        Такая матрица не свящана с экраном.
        :return:
        """
        self.height = height
        self.width = width
        self.table = np.full((height, width), Cell)

        for row in range(height):  # cell[строка][столбец]
            for col in range(width):
                self.table[row, col] = Cell(row, col, matrix=self)

        self.lastclicked = self.table[0, 0]
        pass

    def create_new_game(self, n_bombs: int = 0):
        """
        Used to create a new game.
        Fills the field with bombs and closed cells.
        This matrix is not linked to the screen.
        :param n_bombs: Number of bombs to place
        :return:
        """
        self.mines = set()  # Initialize the set to store mine positions

        for row, col in product(range(self.height), range(self.width)):
            self.table[row, col].asset = asset.closed

        placed_mines = 0
        while placed_mines < n_bombs:
            row = random.randint(0, self.height - 1)
            col = random.randint(0, self.width - 1)

            if (row, col) not in self.mines:
                self.mines.add((row, col))
                placed_mines += 1

    # def create_new_game1(self, n_bombs: int = 0):
    #     """
    #     Используется для создания новой игры.
    #     Заполняет поле бомбами и закрытыми ячейками.
    #     Такая матрица не свящана с экраном.
    #     :param bombs:
    #     :return:
    #     """
    #     for row, col in product(range(self.height), range(self.width)):
    #         self.table[row, col].asset = asset.closed
    #         # print(f'Closed at {row}:{col}')
    #
    #     placed_mines = 0
    #     while placed_mines < n_bombs:
    #         row = random.randint(0, self.height - 1)
    #         col = random.randint(0, self.width - 1)
    #
    #         if self.table[row, col].asset != asset.there_is_bomb:
    #             self.table[row, col].asset = asset.there_is_bomb
    #             placed_mines += 1

    def cell_distance(self, cell1, cell2) -> float:
        d = math.hypot(cell1.row - cell2.row, cell1.col - cell2.col)
        return d

    # deprecated
    # def display(self):
    #     """
    #     Выводит в консоль текущее изображение поля (матрицу)
    #     :return: Возвращает матрицу типа array of strings
    #     """
    #     print('---DISPLAY---')
    #     matrix_view = []
    #     for row in range(self.height):
    #         row_view = ''
    #         for col in range(self.width):
    #             c = self.table[row, col]
    #             # было
    #             # row_view += self.table[row, col].cell_pict() + ' '
    #             # стало
    #             row_view += c.asset.symbol + ' '
    #         matrix_view.append(row_view)
    #     print('\n'.join(row for row in matrix_view))
    #     return matrix_view

    def display(self):
        """
        Выводит в консоль текущее изображение поля (матрицу)
        :return: Возвращает матрицу типа array of strings
        """
        print('---DISPLAY---')
        matrix_view = [
            ' '.join(self.table[row, col].asset.symbol for col in range(self.width))
            for row in range(self.height)
        ]
        print('\n'.join(matrix_view))
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
                raise Exception('`get_slice` function - out of matrix range')
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

    def around_opened_cells(self, cell):
        """
        Возвращает список открытых ячеек вокруг ячейки cell.
        :param cell: instance of Cell class
        :return: array of Cell instances
        """
        flagged_cells = list([x for x in self.around_cells(cell) if x.is_open])
        return flagged_cells

    def around_mines_cells(self, cell):
        """
        Возвращает список ячеек-мин вокруг ячейки cell.
        Используется для tk-версии с известно расположенными минами.
        :param cell: instance of Cell class
        :return: array of Cell instances
        """
        mines = list([x for x in self.around_cells(cell) if x.is_known_bomb])
        return mines

    def get_closed_cells(self):
        """
        Возвращает все закрытые ячейки (которые закрыты и НЕ отмечены флагом)
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_closed])
        return cells

    def get_opened_cells(self):
        """
        Возвращает все открытые ячейки (это цифры плюс пустая ячейка)
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_open])
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
        Возвращает список бомб (которые видны, если игра окончена). Используется в game_over
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_bomb])
        return cells

    def get_known_mines(self):
        """
        Возвращает список установленных мин в закрытых ячейках.
        :return:
        """
        return [self.table[row][col] for row, col in self.mines]

    def get_noguess_cell(self):
        """
        Первый ход для no-guess игр. Возвращает отмеченную крестиком клетку.
        :return: list of Cell objects
        """
        cell = list([x for x in self.table.flat if x.is_noguess])
        return cell

    def is_mine(self, cell):
        return (cell.row, cell.col) in self.mines

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
        time.sleep(config.screen_refresh_lag)

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

    def bomb_qty(self, precision=0) -> int:
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
            # result = util.search_pattern_in_image_for_red_bombs(template, crop_img, precision)
            result = util.search_pattern_in_image_for_red_bombs_on_work(template, crop_img, precision)

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

    def save(self):
        """
        Сохраняет текущую игру в папку, создавая два файла - картинку с изображением игры
        и файл pickle, который потом можно загрузить.
        """
        print('Saving...')
        random_string = secrets.token_hex(2)
        date_time_str = datetime.now().strftime("%d-%b-%Y--%H.%M.%S.%f")
        picklefile = 'obj.pickle'
        image_file = 'image.png'
        dir = 'game_R1_' + date_time_str + '_' + random_string
        if not os.path.exists(dir):
            os.makedirs(dir)

        with open(os.path.join(dir, picklefile), 'wb') as outp:
            pickle.dump(self, outp, pickle.HIGHEST_PROTOCOL)

        image = self.get_image()
        cv.imwrite(os.path.join(dir, image_file), image)

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

    def show_debug_text_orig(self):
        """
        Показывает текст на ячейках, который содержится в каждой ячейке в debug_text.
        Убирает текст после нажатия любой клавиши.
        :return:
        """
        dc = win32gui.GetDC(0)
        try:
            for row in self.table:
                for cell in row:
                    if cell.debug_text is not None:
                        rect = (cell.abscoordx, cell.abscoordy, cell.abscoordx+cell.w, cell.abscoordy+cell.h)
                        win32gui.DrawText(dc, cell.debug_text, -1, rect, win32con.DT_LEFT)
                    cell.debug_text = None

            im = self.get_image()
            cv.imwrite('screenshot2.png', im)

            # keyboard.wait('space')
        finally:
            win32gui.ReleaseDC(0, dc)



    def show_debug_text(self):
        """
        Показывает текст на ячейках, который содержится в каждой ячейке в debug_text, в пределах ограниченной области.
        Убирает текст после нажатия любой клавиши, восстанавливая исходное состояние области.
        """
        # Координаты области
        x1, y1, x2, y2 = self.region_x1, self.region_y1, self.region_x2, self.region_y2
        width = x2 - x1
        height = y2 - y1

        # Получаем контекст устройства для области экрана
        hdesktop = win32gui.GetDesktopWindow()
        desktop_dc = win32gui.GetWindowDC(hdesktop)

        # Создаем контекст устройства для сохранения области
        mem_dc = win32ui.CreateDCFromHandle(desktop_dc)
        save_dc = mem_dc.CreateCompatibleDC()

        # Создаем битмап для сохранения области
        save_bitmap = win32ui.CreateBitmap()
        save_bitmap.CreateCompatibleBitmap(mem_dc, width, height)
        save_dc.SelectObject(save_bitmap)

        # Сохраняем область экрана в битмап
        save_dc.BitBlt((0, 0), (width, height), mem_dc, (x1, y1), win32con.SRCCOPY)

        try:
            # Рисуем текст поверх экрана
            for row in self.table:
                for cell in row:
                    if cell.debug_text is not None:
                        rect = (
                            cell.abscoordx,
                            cell.abscoordy,
                            cell.abscoordx + cell.w,
                            cell.abscoordy + cell.h
                        )

                        # Рисуем текст только если ячейка попадает в область
                        if (
                                rect[0] >= x1 and rect[1] >= y1 and
                                rect[2] <= x2 and rect[3] <= y2
                        ):
                            win32gui.DrawText(desktop_dc, cell.debug_text, -1, rect, win32con.DT_LEFT)
                            cell.debug_text = None

            # Ждем нажатия клавиши
            # keyboard.wait('space')
            keyboard.read_event()

            # Восстанавливаем область экрана из сохраненного битмапа
            mem_dc.BitBlt((x1, y1), (width, height), save_dc, (0, 0), win32con.SRCCOPY)

        finally:
            # Очистка ресурсов
            win32gui.DeleteObject(save_bitmap.GetHandle())
            save_dc.DeleteDC()
            mem_dc.DeleteDC()
            win32gui.ReleaseDC(hdesktop, desktop_dc)

    def play_left_button(self, cell):
        """
        Метод для "игры" в сапера Tk.
        :param cell:
        :return:
        """
        is_game_over = False

        match cell.asset:
            case asset.closed:
                # открываем ячейку
                # Обращаю внимание, что закрытая ячейка не может быть бомбой!
                # Закрытые ячейки с бомбами обозначаются как asser.there_is_bomb
                # depr cell.asset = asset.open_cells

                mines = len(self.around_known_bombs_cells(cell))
                cell.asset = asset.open_cells[mines]

                # Если вокруг ячейки нет бомб (n0), открываем все соседние ячейки
                if cell.is_empty:
                    for neighbor in self.around_closed_cells(cell):
                        self.play_left_button(neighbor)
                # Если ячейка с цифрой, ничего не делаем
                elif cell.is_digit:
                    pass

            case cell.asset if cell.asset in asset.digits:
                # пока держит мышку, закрытые ячейки вокруг визуально меняем на открытые (как-бы подсвечиваем)
                # если кол-во бомб вокруг совпадаем с цифрой - открываем все закрытые ячейки вокруг мины.
                flagged_cells = self.around_flagged_cells(cell)
                print('Detect flagged cells:', flagged_cells)
                if len(flagged_cells) == cell.asset.value:
                    print('Flagged equal!')
                    for neighbor in self.around_closed_cells(cell):

                        print('Neighbors: ', self.around_closed_cells(cell))

                        self.play_left_button(neighbor)

            case asset.there_is_bomb:
                # Game over!
                print("Game Over!")
                self.reveal_all_bombs(cell)
                is_game_over = True
            case asset.n0:
                pass  # тут реально pass, ничего делать не надо.
            case asset.flag:
                pass  # тут тоже реально pass, если стоит флаг, ячейку не открываем.

        return is_game_over

    def play_right_button(self, cell):
        match cell.asset:
            case asset.closed:
                cell.asset = asset.flag
            case asset.there_is_bomb:
                cell.asset = asset.flag
            case asset.flag:
                cell.asset = asset.closed

    def reveal_all_bombs(self, cell):
        bombs = self.get_known_bomb_cells()
        for b in bombs:
            b.asset = asset.bomb
        cell.asset = asset.bomb_red




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
