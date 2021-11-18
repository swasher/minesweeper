from asset import Asset
from pynput import mouse


def on_click(x, y, button, pressed):
    # pressed = True при нажатии кнопики и False при отпускании
    # print('{0} at {1}'.format('Pressed' if pressed else 'Released', (x, y)))

    if not pressed:  # Когда мы возвращаем False, конструкция with listener: завершается
        # Stop listener
        global xx, yy, bb
        xx = x
        yy = y
        bb = button
        return False


def on_move(x, y):
    # print('Pointer moved to {0}'.format((x, y)))
    pass


def on_scroll(x, y, dx, dy):
    # print('Scrolled {0} at {1}'.format('down' if dy < 0 else 'up', (x, y)))
    pass


def win32_event_filter(msg, data):
    # msg = 512 move
    # msg = 513 left click
    # msg = 516 right click
    # data.pt.x and y  - coordinates
    # data has unknown but probably useful flag attribute
    if msg in [513, 516]:
        # Тут мы смотрим на все события мыши.
        # Если событие - это нажатие кнопки, то мы его не передаем дальше в систему (suppress)
        listener.suppress_event()


listener = mouse.Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll,
        win32_event_filter=win32_event_filter
)

import time
import msvcrt
def wait_func(t=5):
    print(f'Wait {t:.1f} sec')
    for i in range(round(t*10), 0, -1):
        if msvcrt.kbhit():
            # key = msvcrt.getch()
            pressed = True
            break
        print(f'\b\b\b{i/10:.1f}', end='')
        time.sleep(0.1)
    print('\b\b\b', end='')

    # if pressed:
    #     print('Wait for key press')
    #     k = False
    #     while not k:
    #         k = msvcrt.kbhit()

import threading
def solver_human(matrix):
    """
    Передает управление человеку, если нет ходов
    :param matrix:
    :return:
    """

    x = threading.Thread(target=wait_func(), args=(), daemon=True)
    x.start()

    print('Start mouse listen')

    with listener:
        listener.join()

    print('Stop mouse listen')
    print(f'{xx}, {yy}, {bb}')

    exit()
    point = (xx, yy)
    cell = matrix.cell_by_abs_coords(point)
    button = Asset.open
    button = Asset.flag
    return [cell], Asset.open
