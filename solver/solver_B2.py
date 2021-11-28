import itertools

import maus
from solver.classes import create_roots


def solver_B2(matrix):
    """
    - Для каждой цифры делаем список закрытых ячеек
    - Если один набор полностью входит во второй
    - Из ЦИФРЫ списка (вокруг которой root) вычитаем кол-во уже открытых флагов
    - Сравниваем два корня (каждый с каждым).
    - Находим совпадения:
        `Цифра` первого корня + `Цифра` второго корня + разница в длине между корнями = длина большего корня
        Вот эту разницу - отмечаем бомбами.
    См. иллюстрацию в pic

    r1 = roots[0]
    r2 = roots[1]
    set(r1.closed).issubset(set(r2.closed))  => True если r1 входид в множество r2

    set(r1) ^ set(r2) => set содержащий элементы, которые входят только в одно из множеств (XOR)

    r1.union(r2) => set содержащий все элементы обоих множеств (без дублирования) (OR)
    """
    roots = create_roots(matrix)
    for r1, r2 in itertools.combinations(roots, 2):

        set1 = set(r1.closed)
        set2 = set(r2.closed)
        if set1.issubset(set2) or set2.issubset(set1):
            # сначала я думал убирать возможный знак минус, но именно так получается правильно - даже если будет минус,
            # то в обоих случаях. А если его убрать, возможны коллизии
            diff_len = r1.len_closed - r2.len_closed

            diff_number = r1.rest_bombs - r2.rest_bombs
            if diff_len and (diff_len == diff_number):
                # XOR - возвращает то, что не входит в оба сета.
                # Возвращает тип set. Если нужен список - обернуть в tuple.
                bombs = tuple(set(r1.closed) ^ set(r2.closed))
                # r1.ancestor.mark_cell_debug()
                # r2.ancestor.mark_cell_debug()
                # print('COMPARE', r1.ancestor, r2.ancestor)
                # print(bombs)
                return bombs, maus.FLAG
    return [], maus.FLAG
