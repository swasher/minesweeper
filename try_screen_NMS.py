import win32gui
import win32api
import cv2 as cv
from assets import *
from screen_controller import search_pattern_in_image_NMS

def draw_rect(x1, y1, x2, y2):
    dc = win32gui.GetDC(0)
    red = win32api.RGB(255, 0, 0)
    win32gui.SetPixel(dc, 0, 0, red)  # draw red at 0,0
    win32gui.Rectangle(dc, x1, y1, x2, y2)

def try_found_1_image():
    # method = cv.TM_CCOEFF
    method = cv.TM_CCOEFF_NORMED  # ++
    # method = cv.TM_CCORR
    # method = cv.TM_CCORR_NORMED  # ++
    # method = cv.TM_SQDIFF
    # method = cv.TM_SQDIFF_NORMED


    image_file = 'led_of_msonline.png'
    patterns = [led0, led1, led2, led3, led4, led5, led6, led7, led8, led9]
    present_pattern_in_image = [led0, led1, led2, led3, led8, led9]

    for led in patterns:
        location, similarity = search_pattern_in_image_NMS(pattern=led.raster, image=image_file, method=method)
        # print('Location:', location)
        is_pattern_in_image = '+' if led in present_pattern_in_image else '-'
        print(f'{led.name} {is_pattern_in_image} Sim:', similarity)


if __name__ == "__main__":
    try_found_1_image()
