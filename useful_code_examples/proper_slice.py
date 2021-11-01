"""
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
    elif v == len_axis:
        return v - 1, v + 1
    else:
        return v - 1, v + 2


def get_around_cells(arr, x, y):
    # arr.shape = (4, 5)   -> 4 строки, 5 итемов в строке (стобцов)
    x1, x2 = get_slice(x, arr.shape[1])
    y1, y2 = get_slice(y, arr.shape[0])

    arr[y, x] = 0  # Это может быть выход из ситуации - помечать центральную ячейку в
                   # исходном массиве; но некрасиво, решил делать по другому
    square = arr[y1:y2, x1:x2]
    # в аргументах arr[ ]
    # сначала указываются строки, (номер "внешнего"  массива)
    # потом стобцы (номер элемента во внутреннем массиве
    # не включая последний!!! (как range)

    return square

x = 1
y = 1
print(arr)
print(f'\nSliced at {x}:{y}:\n')
c = get_around_cells(arr, x, y)
print(get_around_cells(arr, x, y))

print('----')
for j in c.flat:
    print(j)