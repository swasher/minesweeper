from typing import TYPE_CHECKING
import numpy as np
from numpy import ndarray
from .matrix import Matrix
from .cell import Cell
from asset import asset
import mss
import mss.tools
import cv2 as cv





class SolveMatrix(Matrix):

    #initialize_from_screen
    def initialize(self, row_values: list[int], col_values: list[int], region: list[int]):
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
                c = Cell(self, row, col, coordx, coordy, abscoordx, abscoordy, w, h)
                image_cell = self.image_cell(c)
                c.image = image_cell
                c.update_cell(image_cell)  # нужно делать апдейт, потому что при простом старте у нас все ячейки закрыты, а если мы загружаем матрицу из Pickle, нужно ячейки распознавать.
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