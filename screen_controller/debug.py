import win32gui
import win32api


def draw_rect(x1, y1, x2, y2):
    dc = win32gui.GetDC(0)
    red = win32api.RGB(255, 0, 0)
    win32gui.SetPixel(dc, 0, 0, red)  # draw red at 0,0
    win32gui.Rectangle(dc, x1, y1, x2, y2)