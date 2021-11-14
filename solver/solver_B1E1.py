import math
import util
from config import config
from asset import Asset


def solver_B1E1(matrix):
    """
    Объедененный алгоритм E1+B1.
    Нужен для более "человеческой" игры - чтобы нажатия на клетки совершались кучно, а не вразброс по всему полю

    B1 - значит ищем Bомбы алгоритомом "один"

    Алгоритм:
    Проверяем все ячейки с цифрами.
    Если цифра в ячейке равно кол-ву соседних закрытых клеток (включая клетки с флагами),
    ТО все оставшиеся неоткрытые клетки - бомбы


    E1 значит Empty - ищем потенчиально пустые ячейки алгоритмом "один"

    Алгоритм:
    Проверяем все ячейки с цифрами.
    Если вокруг ячейки с цифрой такое же кол-во флагов, и вокруг есть закрытые
    ячейки, ТО все закрытые ячейки вокруг являются пустыми.

    Алгоритм сканирует все поле по этому принципу, затем выбирает ту ячейку, у которой максимальное кол-во пустых клеток.

    HINT: Такие ячейки можно "вскрыть" левым или "both" кликом - откроются все вокруг.
    КРОМЕ режима noflag - тогда отдаем все нужные ячейки
    """

    #
    # B1 part
    #

    cells_b1 = []
    button_b1 = Asset.flag
    for cell in matrix.get_digit_cells():
        closed = matrix.around_closed_cells(cell)
        flags = matrix.around_flagged_cells(cell)

        if (cell.digit == len(closed) + len(flags)) and len(closed) > 0:
            # значит во всех closed клетках есть бомбы

            # вариант алгоритма с возвратом первой найденной ячейки
            # можно вернуть одну ячейку
            # return closed, 'right'

            for c in closed:
                cells_b1.append(c)

    if cells_b1:
        # В список cells одна и та же ячейка может попасть несколько раз (при анализе разных "цифр"). Убираем дубликаты.
        cells_b1 = util.remove_dup(cells_b1)

        # Алгоритм B1 выдает серию клеток; сортируем их в порядке "близости" к последней нажатой клетке
        cells_b1 = sorted(cells_b1, key=lambda c: matrix.cell_distance(c, matrix.lastclicked))

        dist_b1 = matrix.cell_distance(cells_b1[0], matrix.lastclicked)
    else:
        dist_b1 = 0

    #
    # E1 part
    #

    cells_e1 = []
    button_e1 = Asset.nearby

    for cell in matrix.get_digit_cells():
        closed = matrix.around_closed_cells(cell)
        flags = matrix.around_flagged_cells(cell)

        if cell.digit == len(flags) and len(closed):
            cell.nearby_closed = len(matrix.around_closed_cells(cell))
            cells_e1.append(cell)

    if cells_e1:
        # TODO тут надо подумать.
        #      С одной стороны, выгодно совершать both click, чтобы открыть максимальное кол-во закрытых клеток.
        #      С другой, мы хотим нажать максимально близко к последнему нажатию.
        solution_e1 = [max(cells_e1, key=lambda item: item.nearby_closed)]

        dist_e1 = matrix.cell_distance(solution_e1[0], matrix.lastclicked)

        if config.noflag:
            # todo тут говно код... Завязана логика поиска решений на тип игры (noflag)
            solution_e1 = matrix.around_closed_cells(solution_e1[0])
            dist_e1 = matrix.cell_distance(solution_e1[0], matrix.lastclicked)
            button_e1 = Asset.open

        # if config.turn_by_turn:
        #     ic('------ E1')
        #     ic(solution)
        #     solution.mark_cell_debug()
    else:
        # если ни у одной клетки нет решения, возвращаем пустой список
        solution_e1 = []
        dist_e1 = 0

    #
    # Выбираем, что возвращать
    #
    if dist_b1 or dist_e1:
        if dist_b1 >= dist_e1:
            return cells_b1[0:1], button_b1
        else:
            return solution_e1, button_e1
    else:
        return [], None







