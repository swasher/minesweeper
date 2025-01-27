from pynput import mouse
import threading
import time
import win32gui
import win32api
import win32con

from core.screen import ScreenMatrix
from core.screen import find_board
from solver import multi_solver

hwnd = win32gui.GetDesktopWindow()
dc = win32gui.GetDC(0)

red = win32api.RGB(255, 0, 0)
green = win32api.RGB(0, 255, 0)
blue = win32api.RGB(0, 0, 255)

global x1, y1, x2, y2, width, height
old_turns = []


def do_something():
    global old_turns

    # CLEAR PREVIOUS DRAWING
    background_color = win32api.RGB(198, 198, 198)
    background_brush = win32gui.CreateSolidBrush(background_color)
    background_pen = win32gui.CreatePen(win32con.PS_SOLID, 0, background_color)

    old_brush = win32gui.SelectObject(dc, background_brush)
    old_pen = win32gui.SelectObject(dc, background_pen)

    # Перерисовываем те же области фоновым цветом
    for turn in old_turns:
        x, y = turn.cell.abscoordx + 12, turn.cell.abscoordy + 12
        rad = 3
        win32gui.Ellipse(dc, x - rad, y - rad, x + rad, y + rad)

    win32gui.SelectObject(dc, old_brush)
    win32gui.SelectObject(dc, old_pen)
    win32gui.DeleteObject(background_brush)
    win32gui.DeleteObject(background_pen)

    matrix.update_from_screen()
    turns = multi_solver(matrix)

    # matrix.display()
    old_turns = turns

    for turn in turns:
        if turn.probability == 0:  # 100% нет мин
            brush = win32gui.CreateSolidBrush(green)
            pen = win32gui.CreatePen(win32con.PS_SOLID, 0, green)
        elif turn.probability == 1:  # 100% есть мина
            brush = win32gui.CreateSolidBrush(red)
            pen = win32gui.CreatePen(win32con.PS_SOLID, 0, red)
        else:
            # в будующем у нас будут еще промежуточные вероятности
            pass

        # Select the brush and pen into the device context (hdc)
        old_brush = win32gui.SelectObject(dc, brush)
        old_pen = win32gui.SelectObject(dc, pen)

        x, y = turn.cell.abscoordx + 12, turn.cell.abscoordy + 12
        rad = 3
        win32gui.Ellipse(dc, x - rad, y - rad, x + rad, y + rad)

        win32gui.SelectObject(dc, old_brush)
        win32gui.SelectObject(dc, old_pen)
        win32gui.DeleteObject(brush)
        win32gui.DeleteObject(pen)


class MouseListener:
    def __init__(self):
        self.listener = None
        self.worker_thread = None
        self.is_running = True

    def on_click(self, x, y, button, pressed):
        """Обработчик события клика мыши"""
        print(button)
        if pressed:  # Реагируем только на нажатие, не на отпускание
            # Запускаем обработку в отдельном потоке
            if self.worker_thread is None or not self.worker_thread.is_alive():
                # if button == "Button.LEFT":
                self.worker_thread = threading.Thread(target=do_something)
                # elif button == "Button.RIGHT":
                #     self.worker_thread = threading.Thread(target=clear_drawing)
                self.worker_thread.start()

    def start_listening(self):
        """Запуск прослушивания событий мыши"""
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()
        print("Отслеживание кликов мыши запущено...")

    def stop_listening(self):
        """Остановка прослушивания"""
        self.is_running = False
        if self.listener:
            self.listener.stop()
            self.listener.join()

        # Очищаем последнее рисование перед выходом
        win32gui.InvalidateRect(hwnd, None, True)
        win32gui.ReleaseDC(hwnd, dc)

        print("Отслеживание остановлено.")

if __name__ == "__main__":

    col_values, row_values, region = find_board()
    x1, y1, x2, y2 = region
    width = x2 - x1
    height = y2 - y1


    hdc_screen = win32gui.GetDC(0)
    # width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    # height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    hdc_memory = win32gui.CreateCompatibleDC(hdc_screen)
    hbitmap = win32gui.CreateCompatibleBitmap(hdc_screen, width, height)
    win32gui.SelectObject(hdc_memory, hbitmap)


    matrix = ScreenMatrix(row_values, col_values, region)
    print('Matrix creted:')
    matrix.display()

    try:
        # Создаем и запускаем прослушиватель
        mouse_listener = MouseListener()
        mouse_listener.start_listening()

        # Держим программу запущенной
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Корректное завершение при нажатии Ctrl+C
        mouse_listener.stop_listening()
