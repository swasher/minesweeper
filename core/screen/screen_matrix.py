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
from screen_controller import recognize_led_digits
from ..board import board
from utils import random_point_in_circle
import mouse_controller
from mouse_controller import MouseButton


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
                c.content = closed

                # POSSIBLE DEPRECATED
                # c.read_cell_from_screen(image_cell)  # нужно делать апдейт, потому что при простом старте у нас все ячейки закрыты, а если мы загружаем матрицу из Pickle, нужно ячейки распознавать.


                # TODO BUG
                #  вот в этом месте ячейка 'с' вместо closed получает content there_is_bomb



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

    def update_from_screen(self):
        """
        Запускает обновление всех ячеек, считывая их с экрана (поле Minesweeper'а)
        """
        # This is very important string! After click, website (and browser, or even Vienna program) has a lag
        # beetween click and refreshing screen.  If we do not waiting at this point, our code do not see any changes
        # after mouse click.
        time.sleep(config.screen_refresh_lag)

        self.image = self.get_image()

        # Робот не может снять флаг, а вот когда человек играет - может. Поэтому нужно обновлять и ячейки с флагами тоже.
        cells_for_updating = self.get_closed_cells() + self.get_flagged_cells()
        for cell in cells_for_updating:
            crop = self.image_cell(cell)
            cell.read_cell_from_screen(crop)

    def click_smile(self):
        """
        Нажимает на рожицу, чтобы перезапустить поле
        TODO BUG Рожицы нет в играх на маленьких полях - на кастомных полях MinSweeper.Online шириной 7 и меньше
        :return:

        Сделать, чтобы эти настройки брались из asset.
        Пока что мне кажется можно координату X брать как половину поля,
        а Y из ассета
        """

        # face_coord_x = (self.region_x2 - self.region_x1)//2 + self.region_x1
        # face_coord_y = self.region_y1 + board.smile_y_coord

        x1, x2, y1, y2 = self.region_x1, self.region_x2, self.region_y1, self.region_y2
        smile_x = int(x1 + (x2 - x1) / 2)
        smile_y = int(y1 + config.top / 2)
        click_point = random_point_in_circle(smile_x, smile_y, r=10)

        mouse_controller.click(click_point, MouseButton.left)

        # todo но более феншуйно обновить с экрана и проверить - все ячейки должны стать закрытыми
        self.fill_with_closed()

        time.sleep(config.screen_refresh_lag * 10)

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

        if max_val > precision:
            # print('You WIN!\n')
            return True

        return False

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
            # input("Нажмите Enter для продолжения...")

            # Восстанавливаем область экрана из сохраненного битмапа
            mem_dc.BitBlt((x1, y1), (width, height), save_dc, (0, 0), win32con.SRCCOPY)

        finally:
            # Очистка ресурсов
            win32gui.DeleteObject(save_bitmap.GetHandle())
            save_dc.DeleteDC()
            mem_dc.DeleteDC()
            win32gui.ReleaseDC(hdesktop, desktop_dc)

    @property
    def get_remaining_mines_count(self) -> int:
        """
        Число мин минус число флагов. Это число отображается на LED индикаторе.
        Реализация и смысл этого метода в screen и tk версиях совершенно различна. В tk мы используем сами данные матрицы,
        чтобы получить значение led_mines и отобразить его на индикаторе, в то время как в screen версии мы
        считываем индикатор, чтобы получить информацию о кол-ве мин.

        Но итог один - метод возвращает число мин на индикаторе.
        """
        image = self.get_image()
        crop_img = image[0:board.border['top'], 0:(self.region_x2 - self.region_x1) // 2]
        qty = int(recognize_led_digits(crop_img))
        return qty

    def get_mined_cells(self) -> list[Cell]:
        """
        Возвращает список установленных мин в закрытых ячейках (только для Tk сапера).
        :return:
        """
        raise NotImplementedError("Метод get_mined_cells не применим для MatrixScreen")


__all__ = ['ScreenMatrix']
