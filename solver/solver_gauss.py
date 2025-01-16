#
#
# dir = 'game_SAVE_24-Nov-2021--19.30.04.683185'
# matrix = manual_interract.load(dir)
# matrix.update()
# s = matrix.find_cells_sets()
# print(s)
#
# for cellset in s:
#     color = random.choice(['red', 'green', 'blue', 'yellow', 'cyan', 'magenta'])
#     for c in cellset:
#         c.mark_cell_debug(color)
#
"""
Матрица должа быть вида (каждое значение - инстанс Cell)

Closed1  Closed2         | Digit1
         Closed2 Closed3 | Digit2

и решаться
m = np.array[[Closed1, Closed2], [Closed2, Closed3]]
v = np.array[Digit1, Digit2]
np.linalg.solve(m, v)
"""
from collections import namedtuple

import numpy as np

import mouse_controller
import random
from core import Action

"""
См. pics/clusters.png
:return:
"""


def glue_cell_array_into_groups(arr):
    """
    Рекурсивная функция. Принимает `array of arrays of Cells`.
    Сравнивает списки попарно. Если в паре есть общие ячейки, то пара объеденяется, добавляется в `arr`,
    а исходные списки удаляются.
    На выходе получаем такой же `array of arrays of Cells`
    :param arr:
    :return:
    """
    lenght = len(arr)
    for i in range(lenght):
        for j in range(lenght):
            item_i, item_j = arr[i], arr[j]
            if bool(item_i.intersection(item_j)) and i != j:
                new_entry = item_j.union(item_i)
                arr.remove(item_i)
                arr.remove(item_j)
                arr.insert(0, new_entry)

                # colors = ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta']
                # for cellset in arr:
                #     color = random.choice(colors)
                #     for c in cellset:
                #         c.mark_cell_debug(color)

                return glue_cell_array_into_groups(arr)
    return arr


def make_registered_groups(matrix):
    digits_around_cells = []

    for cell in matrix.get_digit_cells():
        closed_around = matrix.around_closed_cells(cell)
        digits_around_cells.append(set(closed_around))

    registered_groups = glue_cell_array_into_groups(digits_around_cells)
    return registered_groups


def make_clusters(matrix, registered_groups):
    """
    Создаем "кластеры" - каждый кластер содержит набор связанных закрытых ячеек и список прилегающих
    к этому набору цифр. Эти два набора в дальнейшем используются для создания матрицы - набор ячеек для
    самой матрицы, а цифры - для вектора матрицы.
    """
    clusters = []
    Cluster = namedtuple('Cluster', ['body', 'vector'])
    for group in registered_groups:
        vector = set()
        for cell in group:
            around_digits = matrix.around_digit_cells(cell)
            vector = vector.union(set(around_digits))
        vector = list(vector)
        cluster = Cluster(body=group, vector=vector)
        clusters.append(cluster)
    return clusters


def solver_gauss(matrix):
    registered_groups = make_registered_groups(matrix)
    clusters = make_clusters(matrix, registered_groups)

    if clusters:
        for cluster in clusters:
            color = random.choice(['red', 'green', 'blue', 'yellow', 'cyan', 'magenta'])
            for c in cluster.body:
                # В реальной игре мы не можем маркировать ячейки цветом, потому что при следующем сканировании
                # они не будут совпадать с "образцами"
                # c.mark_cell_debug(color)
                pass


# Тут нужно как то добавть в numpy.array массив типа:
# x1*0, x2*1, x3*0, x4*1
# где x - это все ячейки в кластере, а 0 или 1 - входид ячейка в текущий вектор или нет
# таким образом получим матрицу.
#
# Идея:
# у каждой Cell сделать property - взаимодействует она с цифрой Cell_digig (1) или нет (0).
# Тогда создать матрицу так:
# cell1(digit1), cell2(digit1), cell3(digit1) | digit1
# cell1(digit2), cell2(digit2), cell3(digit2) | digit2
#
#
# Ссылки матрица объектов
# # https://stackoverflow.com/a/55872235/1334825
# # https://stackoverflow.com/questions/4877624/numpy-array-of-objects


        for cluster in clusters:
            """
            На этом месте мы работаем с кластером cluster,
            у которого есть cluster.vector - это цифры и cluster.body - это закрытые ячейки.
            Нам нужно построить матрицу - по строке на каждую цифру. Для каждой ячейки написать 
            0 если ячейка не взаимодействует с цифрой, иначе 1.
            """
            matrice = []
            matrice_vector = []

            for digit in cluster.vector:

                matrice_row = []

                for cell in list(cluster.body):
                    if cell in matrix.around_closed_cells(digit):
                        matrice_row.append(1)
                    else:
                        matrice_row.append(0)

                matrice.append(matrice_row)
                matrice_vector.append(digit.type.value)


            """
            На этом этапе мы уже должны смочь решить матрицу
            """
            m = np.array(matrice)
            v = np.array(matrice_vector)
            try:
                np.linalg.solve(m, v)
            except np.linalg.LinAlgError:
                pass  # no solution


    return [], Action.open_cell
