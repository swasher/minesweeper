import time
import msvcrt
import threading
from pynput import mouse
from threading import Timer
from datetime import datetime

from classes import Action


def exists(var):
    return var in globals()


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


def solver_human(matrix):
    """
    Передает управление человеку, если нет ходов
    :param matrix:
    :return:
    """
    cell = None

    def on_click(x, y, button, pressed):
        nonlocal t
        nonlocal cell
        nonlocal start_time
        # pressed = True при нажатии кнопики мыщи и
        # pressed = False при отпускании
        if not pressed:
            # Когда мы возвращаем False, когда хотим остановить listener thread:
            # конструкция with listener: завершается
            global xx, yy, bb
            xx = x
            yy = y
            bb = button

            point = (xx, yy)
            cell = matrix.cell_by_abs_coords(point)
            print('\nUser click mouse', f'{xx}, {yy}, {bb}, cell is: {cell}')
            if cell:
                return False
            else:
                print('Clicked out of field')
                start_time = datetime.now()
                t.cancel()
                t = Timer(5, mouse_thread.stop)
                t.start()

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
            mouse_thread.suppress_event()

    # x = threading.Thread(target=wait_func(), args=(), daemon=True)
    # x.start()

    print('\nStart mouse listen: wait your move 5 sec')


    mouse_thread = mouse.Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll,
        win32_event_filter=win32_event_filter
    )

    t = Timer(5, mouse_thread.stop)


    start_time = datetime.now()
    t.start()
    mouse_thread.start()


    while True:
        time.sleep(0.1)
        now_time = datetime.now()
        delta = (now_time - start_time).total_seconds()
        out_str = f'{delta:.2f}'
        print('\b'*len(out_str) + out_str, end='')
        if cell or not t.is_alive():
            break

    t.cancel()
    mouse_thread.stop()


    if exists('xx'):

        print('User click mouse', f'{xx}, {yy}, {bb}')

        point = (xx, yy)
        cell = matrix.cell_by_abs_coords(point)
        if cell:
            if bb == mouse.Button.left:
                action = Action.open_cell
            elif bb == mouse.Button.right:
                action = Action.set_flag
            else:
                exit('Error: That mouse button is not assigned.')
            return [cell], action
        else:
            print('Нажато за пределами поля')

    else:

        print('\nNo action from human')
        from .solver_R1 import solver_R1
        return solver_R1(matrix)
