import time
import msvcrt
import threading
from asset import Asset
from pynput import mouse
from threading import Timer


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


    def on_click(x, y, button, pressed):
        nonlocal t
        # pressed = True при нажатии кнопики мыщи и
        # pressed = False при отпускании
        if not pressed:
            # Когда мы возвращаем False, когда хотим остановить listener thread:
            # конструкция with listener: завершается
            global xx, yy, bb
            xx = x
            yy = y
            bb = button

            print('User click mouse', f'{xx}, {yy}, {bb}')

            point = (xx, yy)
            cell = matrix.cell_by_abs_coords(point)
            if cell:
                return False
            else:
                print('Click out of field')
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

    print('Start mouse listen: wait your move 5 sec')

    mouse_thread = mouse.Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll,
        win32_event_filter=win32_event_filter
    )

    def showing():
        print('.')

    my_thread = threading.Thread(target=showing, args=())
    with mouse_thread:
        t = Timer(5, mouse_thread.stop)
        t.start()
        mouse_thread.join()
        my_thread.start()





    # t.cancel()

    if exists('xx'):

        print('User click mouse', f'{xx}, {yy}, {bb}')

        point = (xx, yy)
        cell = matrix.cell_by_abs_coords(point)
        if cell:
            if bb == mouse.Button.left:
                button = Asset.open
            elif bb == mouse.Button.right:
                button = Asset.flag
            else:
                exit('Error: That mouse button is not assigned.')
            return [cell], button
        else:
            print('Нажато за пределами поля')

    else:

        print('No action from human')
        from .solver_R1 import solver_R1
        return solver_R1(matrix)



        # exit()
        # return [], None




