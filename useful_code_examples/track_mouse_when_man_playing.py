"""
Util for analyze human mouse use - time and distance.

Results:

Minesweeper Online, size 28 (big cells). 30 clicks per run. 3 runs every test.
============================

Рядом стоящие клетки
-------------------
Distance 30.72, Time: 0.43, Time per 100 px: 1.47
Distance 31.89, Time: 0.41, Time per 100 px: 1.35
Distance 31.03, Time: 0.40, Time per 100 px: 1.36

Средне расположенные клетки (треть - две трети высоты поля)
--------------------
Distance 299.88, Time: 0.96, Time per 100 px: 0.37
Distance 286.46, Time: 0.89, Time per 100 px: 0.42
Distance 254.39, Time: 0.88, Time per 100 px: 0.39

Отдаленно стоящие клетки
------------------------
Distance 663.85, Time: 1.08, Time per 100 px: 0.18
Distance 691.21, Time: 0.97, Time per 100 px: 0.15
Distance 690.31, Time: 1.03, Time per 100 px: 0.16


Vienna (home)
=================================

Рядом стоящие клетки
-------------------
Distance 16.59, Time: 0.46, Time per 100 px: 2.88
Distance 15.44, Time: 0.44, Time per 100 px: 2.90
Distance 15.62, Time: 0.46, Time per 100 px: 3.02

Средне расположенные клетки (треть - две трети высоты поля)
--------------------
Distance 154.83, Time: 1.05, Time per 100 px: 0.72
Distance 144.12, Time: 1.03, Time per 100 px: 0.74
Distance 152.89, Time: 1.08, Time per 100 px: 0.78

Отдаленно стоящие клетки
------------------------
Distance 320.75, Time: 1.06, Time per 100 px: 0.36
Distance 316.51, Time: 1.05, Time per 100 px: 0.35
Distance 308.79, Time: 1.09, Time per 100 px: 0.39
"""
import time
import math
import numpy as np
from dataclasses import dataclass, field
from pynput import mouse
from datetime import datetime

oldx = 0
oldy = 0
oldtime = datetime.now()


@dataclass(order=True)
class Moving:
    # for analyze
    dist: float
    tdelta: time
    # for append next item
    t: time
    x: int
    y: int

    @classmethod
    def add(self, x, y):
        oldx = mousemove[-1].x
        oldy = mousemove[-1].y
        oldt = mousemove[-1].t
        dist = math.hypot(oldx - x, oldy - y)
        t = datetime.now()
        tdelta = t - oldt
        x = x
        y = y
        mousemove.append(Moving(dist, tdelta, t, x, y))


mousemove = []


def on_move(x, y):
    # print('Pointer moved to {0}'.format((x, y)))
    pass


def on_click(x, y, button, pressed):
    # print('{0} at {1}'.format('Pressed' if pressed else 'Released', (x, y)))
    if not pressed:  # считаем клик при отпускании кнопки
        # print(f'Click {button} at {x},{y}')
        Moving.add(x, y)
        # print(mousemove[-1].tdelta.total_seconds())
    # if not pressed:
    #     # Stop listener
    #     return False


def on_scroll(x, y, dx, dy):
    print('Scrolled {0} at {1}'.format('down' if dy < 0 else 'up', (x, y)))


# # Collect events until released
# while True:
#     with mouse.Listener(
#             on_move=on_move,
#             on_click=on_click,
#             on_scroll=on_scroll) as listener:
#         listener.join()

# ...or, in a non-blocking fashion:
listener = mouse.Listener(
    on_move=on_move,
    on_click=on_click,
    on_scroll=on_scroll)


def main():
    print('Start mouse listener')
    m = Moving(dist=0, tdelta=0, x=0, y=0, t=datetime.now())
    mousemove.append(m)

    listener.start()
    # while True:
    while len(mousemove) < 30:
        time.sleep(0.001)

    mousemove.pop(0)  # remove first two elements
    mousemove.pop(0)
    mm_sorted = sorted(mousemove, key=lambda mousemove: mousemove.dist)
    per100 = []
    for x in mm_sorted:
        per100_ = x.tdelta.total_seconds() * 100 / x.dist
        per100.append(per100_)
        print(f'dist: {x.dist:.2f}, time: {x.tdelta.total_seconds():.3f}, per 100 px: {per100_:.3f}')
    arr = np.array([o.dist for o in mm_sorted])
    dist_mean = np.mean(arr)
    delta_mean = np.mean(np.array([o.tdelta.total_seconds() for o in mm_sorted]))
    per100_mean = np.mean(np.array(per100))
    print('----Meaning values:')
    print(f'Distance {dist_mean:.2f}, Time: {delta_mean:.2f}, Time per 100 px: {per100_mean:.2f}')


if __name__ == '__main__':
    main()
