"""
Анализ времени между кликами в реальной игре (без учета расстояния).
Для анализа времени "думания" человека.

Список mousemove содержит экземпляры класса Moving, создающиеся при каждом клике мышки.
По окончании работы мы может проанализировать среднюю скорость движения и другие параметры.
"""
import time
import win32api
import math
import numpy as np
from dataclasses import dataclass, field
from pynput import mouse
from datetime import datetime
import threading
import ctypes
from pynput.keyboard import Key, Listener
from pynput.mouse import Button

oldx = 0
oldy = 0
oldtime = time.perf_counter()
pressed_timestamp_L = 0
pressed_timestamp_R = 0
mousemove = []
both_click = False


@dataclass(order=True)
class Moving:
    x: int
    y: int

    click_timestamp: float = field(init=False)
    click_time_delta: float = field(init=False)
    dist: float = field(init=False)

    def __post_init__(self):
        if len(mousemove) > 0:
            time_now = time.perf_counter()
            oldx = mousemove[-1].x
            oldy = mousemove[-1].y
            old_timestamp = mousemove[-1].click_timestamp
            self.click_timestamp = time_now
            self.dist = math.hypot(oldx - self.x, oldy - self.y)
            self.click_time_delta = time_now - old_timestamp
        else:
            # если у нас пустой пул кликов, и нет предыдущего для сравнения
            self.click_timestamp = time.perf_counter()
            self.dist = 0
            self.click_time_delta = 0


def on_move(x, y):
    # print('Pointer moved to {0}'.format((x, y)))
    pass


def left_mouse_button_pressed():
    left_button_pressed = win32api.GetKeyState(0x01) < 0  # Левая кнопка (VK_LBUTTON)
    return left_button_pressed


def right_mouse_button_pressed():
    right_button_pressed = win32api.GetKeyState(0x02) < 0  # Правая кнопка (VK_RBUTTON)
    # middle_button_pressed = win32api.GetKeyState(0x04) < 0  # Средняя кнопка (VK_MBUTTON)
    return right_button_pressed


def on_click(x: int, y: int, button: Button, pressed: bool):
    global pressed_timestamp_L
    global pressed_timestamp_R
    global both_click

    if both_click:
        # мы пропускаем это событие, потому что оно учтено в предыдущем. НО НЕ ФАКТ! МЫ ЖЕ ДЕЛАЕМ АНАЛИЗ!
        # МОЖЕТ БЫТЬ К ДВОЙНЫМ КЛИКАМ НУЖНО ПОДОЙТИ ПО ДРУГОМУ И ТОЖЕ ИХ АНАЛИЗИРОВАТЬ!
        # С ТРЕТЬЕЙ СТОРОЫ, ДЛЯ MS ONLINE ДВОЙНЫЕ КЛИКИ НЕ НУЖНЫ, А ДЛЯ ВИЕННЫ НЕ НУЖНЫ ИСКУСТВЕННЫЕ ЗАДЕРЖКИ.
        both_click = False
        return None

    released = not pressed

    # Этот блок нужен только для подсчета времи удержания кнопки в нажатом состоянии
    if pressed:
        if button == Button.left:
            pressed_timestamp_L = time.perf_counter()
            print(f'Pressed L at {(x, y)}')
        if button == Button.right:
            pressed_timestamp_R = time.perf_counter()
            print(f'Pressed R at {(x, y)}')
    else:
        if button == Button.left:
            buttondown_duration_L = time.perf_counter() - pressed_timestamp_L
            print(f'Released L at {(x, y)}. Press duration: {buttondown_duration_L}')
        if button == Button.right:
            buttondown_duration_R = time.perf_counter() - pressed_timestamp_R
            print(f'Released R at {(x, y)}. Press duration: {buttondown_duration_R}')

    if released:  # сохраняем клик в списке mousemove при отпускании кнопки
        # both click - считается, когда зажаты обе кнопки, и потом срабатывает, когда отпускается любая первая из них.
        # поэтому следующее "отпускание" кнопки не считается за клик. Будем следить за этим с помощью глобального флага.

        # проверяем, обе ли кнопки нажаты
        if button == Button.left and right_mouse_button_pressed():
            print('BOTH!')
        if button == Button.right and left_mouse_button_pressed():
            print('BOTH!')
        both_click = True


        m = Moving(x, y)
        mousemove.append(m)
        print('Timedelta:', mousemove[-1].click_time_delta)


def on_scroll(x, y, dx, dy):
    print('Scrolled {0} at {1}'.format('down' if dy < 0 else 'up', (x, y)))


mouse_listener = mouse.Listener(
    on_move=on_move,
    on_click=on_click,
    on_scroll=on_scroll)


class thread_with_exception(threading.Thread):
    """
    В отдельном потоке запускаем прослушку клавиатуры - так мы можем остановить основной процесс по ESC,
    а так же есть возможность использовать горячие кнопки для каких-то действий, наример, вывода отчета.
    """
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        main_thread()

    def get_id(self):
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        print(Moving)
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')


def on_press(key):
    # print(f'pressed {key}')
    if key == Key.esc:
        print('End measuring.')
        after_esc_pressed()
        keyboard_listener.stop()
        t1.raise_exception()
    if key == Key.f4:
        for m in mousemove:
            print(m)


def main_thread():
    print('Start mouse listener. Press Esc for exit.')

    mouse_listener.start()
    while True:
        time.sleep(0.001)


def after_esc_pressed():
    clicks_sorted_by_dist = sorted(mousemove, key=lambda mousemove: mousemove.dist)

    per100 = []
    speed = []
    for x in clicks_sorted_by_dist:
        if x.dist == 0:
            continue
        per100_ = x.click_time_delta * 100 / x.dist
        per100.append(per100_)
        speed_ = x.dist / x.click_time_delta
        speed.append(speed_)
        print(f'Dist: {x.dist:.2f} | time: {x.click_time_delta:.3f} | sec per 100 px: {per100_:.3f}s | speed: {speed_:.3f}px/s')
    arr = np.array([o.dist for o in clicks_sorted_by_dist])
    dist_average = np.mean(arr)
    delta_average = np.mean(np.array([o.click_time_delta for o in clicks_sorted_by_dist]))
    per100_average = np.mean(np.array(per100))
    speed_average = np.mean(np.array(speed))
    print('----Average values:')
    print(f'Distance {dist_average:.2f} | Time: {delta_average:.2f} | Time per 100 px: {per100_average:.2f} | Speed: {speed_average:.2f}')



if __name__ == '__main__':
    keyboard_listener = Listener(on_press=on_press)
    keyboard_listener.start()  # Запускаем слушатель в отдельном потоке

    t1 = thread_with_exception('Thread 1')
    t1.start()
    # остановка потока по нажатию Esc выполняется в колбеке on_press(key):
    t1.join()

    keyboard_listener.stop()
