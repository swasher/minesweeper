"""
-- Agreement: --
No import high level objects in UTIL! (like classes)
"""

import cv2 as cv
import ctypes


def get_screen_size():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    size = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
    return size



# --- DEPRECATED
def find_templates(pattern, image, precision):

    """
    Эта функция не используется, но пусть будет тут, как альтернатива scan_region

    Ищет несколько вхождений темплейта в имадж.
    Координаты вхождений.

    Код отсюда
    https://stackoverflow.com/questions/61687427/python-opencv-append-matches-center-x-y-coordinates-in-tuples
    """

    h, w = pattern.shape[:2]
    # print('h', h, 'w', w)
    method = cv.TM_CCORR_NORMED

    res = cv.matchTemplate(image, pattern, method)
    res_h, res_w = res.shape[:2]

    # fake out max_val for first run through loop
    max_val = 1
    coords = []
    while max_val > precision:
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        if max_val > precision:
            coords.append((max_loc[0], max_loc[1], max_val))

            x1 = max(max_loc[0] - w//2, 0)
            y1 = max(max_loc[1] - h//2, 0)

            x2 = min(max_loc[0] + w//2, res_w)
            y2 = min(max_loc[1] + h//2, res_h)

            res[y1:y2, x1:x2] = 0

            # эта строка портит image для дальнейших сравнений в цикле
            # image = cv.rectangle(image, (max_loc[0], max_loc[1]), (max_loc[0]+w+1, max_loc[1]+h+1), (0,255,0) )

    """
    DEBUG
    возвращает координаты
    print(centers)
    cv.imshow("Test", image)
    cv.waitKey(0)
    """
    return coords








