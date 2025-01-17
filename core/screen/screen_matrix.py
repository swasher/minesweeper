import time
import numpy as np
from numpy import ndarray
import mss
import mss.tools
import cv2 as cv
import win32gui
import win32ui
import win32con

from config import config

from ..matrix import Matrix
from ..cell import Cell
from ..utility import MineMode
from assets import *  # Ассеты уже инициализированы в __init__.py
from screen_controller import search_pattern_in_image_for_red_bombs


class ScreenMatrix(Matrix):

    def __init__(self, row_values: list[int], col_values: list[int], region: tuple[int, int, int, int]):
        """
        Заполняет Matrix пустыми объектами Cell с экрана,
        настраивая взаимосвязь между экраном и Matrix.
        Каждый объект Cell при этом становится привязан к конкретному месту на экране.
        :param row_values: list[int] - список координат верхнего левого угла строк
        :param col_values: list[int] - список координат верхнего левого угла столбцов
        :param region: list[int, int, int, int] - четыре координаты окна
        """
        super().__init__()
        self.region_x1, self.region_y1, self.region_x2, self.region_y2 = region

        self.image = self.get_image()
        self.height = len(row_values)
        self.width = len(col_values)

        self.table = np.full((self.height, self.width), Cell)
        self.mine_mode = MineMode.UNDEFINED

        template = closed.raster
        h, w = template.shape[:2]

        for row, coordy in enumerate(row_values):  # cell[строка][столбец]
            for col, coordx in enumerate(col_values):
                abscoordx = coordx + self.region_x1
                abscoordy = coordy + self.region_y1
                c = Cell(self, row, col, coordx, coordy, abscoordx, abscoordy, w, h)
                image_cell = self.image_cell(c)
                c.image = image_cell

                # POSSIBLE DEPRECATED
                c.read_cell_from_screen(image_cell)  # нужно делать апдейт, потому что при простом старте у нас все ячейки закрыты, а если мы загружаем матрицу из Pickle, нужно ячейки распознавать.

                """
                TODO BUG 
                
                вот в этом месте ячейка с вместо closed получает content there_is_bomb
                """


                c.hash = c.hashing()
                self.table[row, col] = c

        self.lastclicked = self.table[0, 0]

    def get_image(self) -> ndarray:
        """
        Возвращает текущее изображение поля игры
        :return: opencv image (ndarray)
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
            cell.read_cell_from_screen(crop)

    @property
    def you_win(self):
        """
        Если смайлик = веселый, то WIN
        :return: boolean
        """
        # TODO Это факен шайзе, какие прецижена в методе Матрицы?
        precision = 0.9
        image = self.get_image()
        template = win.raster

        res = cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

        # TODO Remove it from here!
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
        for pattern in red_digits:  # list_patterns imported from cell_pattern
            template = pattern.raster

            # result = util.find_templates(template, crop_img, precision)
            # result = util.search_pattern_in_image_for_red_bombs(template, crop_img, precision)
            result = search_pattern_in_image_for_red_bombs_on_work(template, crop_img, precision)

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


__all__ = ['ScreenMatrix']
