import time
import numpy as np
from asset import Asset
from random import randrange
from pynput import mouse


def on_click(x, y, button, pressed):
    print('{0} at {1}'.format('Pressed' if pressed else 'Released', (x, y)))
    # if not pressed:  # считаем клик при отпускании кнопки
    #     print(f'Click {button} at {x},{y}')
    #     # print(mousemove[-1].tdelta.total_seconds())
    if not pressed:
        # Stop listener
        return False


def on_move(x, y):
    # print('Pointer moved to {0}'.format((x, y)))
    pass


def on_scroll(x, y, dx, dy):
    # print('Scrolled {0} at {1}'.format('down' if dy < 0 else 'up', (x, y)))
    pass



def solver_human(matrix):
    """
    Передает управление человеку, если нет ходов
    :param matrix:
    :return:
    """
    print('Start listen')

    # with mouse.Listener(
    #             on_move=on_move,
    #             on_click=on_click,
    #             on_scroll=on_scroll) as listener:
    #         listener.join()

    with mouse.Events() as events:
        # for event in events:
        #     if event.button == mouse.Button.right:
        #         break
        #     else:
        #         print('Received event {}'.format(event))
        for event in events:
            if isinstance(event, mouse.Events.Click):
                if not event.pressed:
                    button = event.button
                    x, y = event.x, event.y
                    break



    print('Stop listen')
    print(f'{x}, {y}, {button}')

    Только тут проблема, что сам клик передается игре, а я хотел бы его
    обработать сам

    exit()
    cell = 'cell'
    button = Asset.open
    button = Asset.flag
    return [cell], Asset.open
