"""
ЭТО МОЯ ЛИЧНАЯ РАЗРАБОТКА, ПОТОМ ПЕРЕШЕЛ НА NUMPY-СРЕЗЫ, НАПИСАННОЕ AI

Функция дает "правильный" срез матрицы с учетом границ.
ПРоблема в том, что возвращает так же центральную ячейку,
а в результате вычислений уже не понять, где была первоначальная ячейка.
"""

import numpy as np
from pprint import pprint

arr = np.array([[1,  2,  3,  4,   5],
                [6,  7,  8,  9,  10],
                [11, 12, 13, 14, 15],
                [16, 17, 18, 19, 20]])


def get_slice(v, len_axis):
    if v not in range(len_axis):
        raise Exception('`get_proper_area` function - out of matrix range')
    if v == 0:
        return 0, v + 2
    elif v == len_axis-1:
        return v - 1, v + 1
    else:
        return v - 1, v + 2


def get_around_cells(arr, col, row):
    # arr.shape = (4, 5)   -> 4 строки, 5 итемов в строке (стобцов)
    # print('arr.shape', arr.shape)
    x1, x2 = get_slice(col, arr.shape[1])
    # print('x1x2=', x1, x2)
    y1, y2 = get_slice(row, arr.shape[0])
    # print('y1y2=', y1, y2)

    for y in range(y1, y2):
        for x in range(x1, x2):
            if x==col and y==row:
                print('-', ' ', end='')
            else:
                print(arr[y, x], ' ', end='')
        print('')
    exit()
    return square

x = 4
y = 3
print(arr)
print(f'\nSliced at {x}:{y}:\n')
print(get_around_cells(arr, x, y))

