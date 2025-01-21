from pynput import mouse
import threading
import time
import win32gui
import win32api
import win32con

from core.screen import ScreenMatrix
from core.screen import find_board
from core import Action

from solver import multi_solver

hwnd = win32gui.GetDesktopWindow()
dc = win32gui.GetDC(0)

red = win32api.RGB(255, 0, 0)
green = win32api.RGB(0, 255, 0)
blue = win32api.RGB(0, 0, 255)

def do_something():


    matrix.update()

    turns = multi_solver(matrix)

    # matrix.display()

    # Get the desktop window handle (hwnd)



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

        x, y = turn.cell.abscoordx+12, turn.cell.abscoordy+12
        # win32gui.SetPixel(dc, x, y, color)  # draw red at 0,0
        # win32gui.Rectangle(dc, region_x1, region_y1, region_x2, region_y2)
        rad = 3
        win32gui.Ellipse(dc, x - rad, y - rad, x + rad, y + rad)

    # Restore the previous brush and pen (important for cleanup)
    # win32gui.SelectObject(dc, old_brush)
    # win32gui.SelectObject(dc, old_pen)
    # Clean up: Delete the brush and pen objects to free resources
    try:
        win32gui.DeleteObject(brush)
        win32gui.DeleteObject(pen)
    except:
        pass
    # Release the device context


def clear_drawing(self):
    # Очищаем нарисованное, вызывая перерисовку окна
    win32gui.InvalidateRect(self.hwnd, None, True)
    pass




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
                if button == "Button.LEFT":
                    self.worker_thread = threading.Thread(target=do_something)
                elif button == "Button.RIGHT":
                    self.worker_thread = threading.Thread(target=clear_drawing)
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

        win32gui.ReleaseDC(hwnd, dc)

        print("Отслеживание остановлено.")

if __name__ == "__main__":
    col_values, row_values, region = find_board()

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
