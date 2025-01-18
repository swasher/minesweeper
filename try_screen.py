import win32gui
import win32api
import cv2 as cv
from assets import *
from screen_controller import search_pattern_in_image_universal

def draw_rect(x1, y1, x2, y2):
    dc = win32gui.GetDC(0)
    red = win32api.RGB(255, 0, 0)
    win32gui.SetPixel(dc, 0, 0, red)  # draw red at 0,0
    win32gui.Rectangle(dc, x1, y1, x2, y2)

def try_found_1_image():
    method = cv.TM_CCOEFF
    # method = cv.TM_CCOEFF_NORMED  # ++
    # method = cv.TM_CCORR
    # method = cv.TM_CCORR_NORMED  # ++
    # method = cv.TM_SQDIFF
    # method = cv.TM_SQDIFF_NORMED

    image_led = led4.raster
    location, similarity = search_pattern_in_image_universal(pattern=image_led, method=method)
    print('Location:', location)
    print('Similarity:', similarity)


if __name__ == "__main__":
    try_found_1_image()
