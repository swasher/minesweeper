import cv2 as cv
import numpy as np
import numpy.typing as npt
from assets import Asset
from util import compress_array


def compare_images(image1, image2, method=cv.TM_CCOEFF_NORMED) -> float:
    """Сравнивает два изображения и возвращает степень их схожести"""
    res = cv.matchTemplate(image1, image2, method)
    _, max_val, _, _ = cv.minMaxLoc(res)
    return max_val


def cell_coordinates(cells: list[tuple[int, int, float]]) -> tuple[list[int], list[int]]:
    """
    Превращает список координат ВСЕХ ячеек поля в список отдельно X и Y координат (верхнего левого угла ячейки).
    Применяется только для связи search_cells_in_image() с find_board()

    Args:
        cells: list of tuples (x, y, cv2_max_val)

    Returns:
        cells_coord_x: list of int, список координат по оси X для каждого столбца (в пикселях относительно верха лева экрана)
        cells_coord_y: list of int, то же, по оси Y для каждой строки
    """

    cells_coord_y = []
    cells_coord_x = []
    for cell in cells:
        cells_coord_x.append(cell[0])
        cells_coord_y.append(cell[1])

    # Эти два списка - искомые координаты ячеек. Убираем из них дубликаты при помощи set()
    cells_coord_x = compress_array(cells_coord_x)  # кол-во соотв. кол-ву столбцов; координаты столбцов слева направо по X
    cells_coord_y = compress_array(cells_coord_y)  # кол-во соотв. кол-ву строк; координаты строк сверху вниз по Y

    return cells_coord_x, cells_coord_y


