from enum import IntEnum
import mss
import numpy as np
import cv2 as cv
import win32gui
import win32api
import win32con

from config import config
from util import search_pattern_in_image_for_red_bombs
from util import search_pattern_in_image_universal
from asset import smile


def search_smile():
    """
    Функция, аналогичная find_board, но предназначенная для поиска уже начатых игр,
    в которых ячейки уже открыты.
    :return:
    """
    print('Try finding started board...')
    with mss.mss() as sct:
        region = mss.mss().monitors[0]
        screenshot = sct.grab(region)
        raw = np.array(screenshot)
    image = cv.cvtColor(raw, cv.COLOR_BGRA2BGR)
    precision = 0.8

    smile_ndarray = cv.cvtColor(smile.raster, cv.COLOR_BGRA2BGR)
    w, h = smile.raster.shape[0], smile.raster.shape[1]

    # smile = config.assets[game_asset].smile
    methods = ['TM_CCOEFF', 'TM_CCOEFF_NORMED', 'TM_CCORR',
               'TM_CCORR_NORMED', 'TM_SQDIFF', 'TM_SQDIFF_NORMED']
    # тестирование поиска смайлика
    # TM_CCOEFF - ок
    # TM_CCOEFF_NORMED - ок
    # TM_CCORR - не находит
    # TM_CCORR_NORMED - ок
    # TM_SQDIFF - ок
    # TM_SQDIFF_NORMED - ок
    # внимание! значение similarity - отличается для разных методов.
    # Для normed оно между 0 и 1, для - может составлять миллионы.
    # Для TM_SQDIFF_NORMED - около 0, для TM_CCOEFF_NORMED TM_CCORR_NORMED - около 1.
    found_location, similarity = search_pattern_in_image_universal(smile_ndarray, image, precision, method=cv.TM_SQDIFF_NORMED)
    print(found_location, similarity)

    dc = win32gui.GetDC(0)
    red = win32api.RGB(255, 0, 0)
    pen = win32gui.CreatePen(win32con.PS_SOLID, 4, red)  # Красный цвет
    win32gui.SelectObject(dc, pen)
    win32gui.SetBkMode(dc, win32con.TRANSPARENT)
    x, y = found_location
    rect = (x, y, x + w, y + h)
    win32gui.FrameRect(dc, rect, pen)

    return found_location


class MinesweeperMode(IntEnum):
    beginner = 1
    intermediate = 2
    expert = 3
    custom = 4

class MinesweeperBoardSize:
    size: MinesweeperMode = MinesweeperMode.beginner
    width: int
    height: int

if __name__ == '__main__':
    smile_coord = search_smile()
    print(smile_coord)






