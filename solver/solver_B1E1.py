import util
from config import config
from classes import Action
from classes import Cell


def solver_B1E1(matrix) -> ([Cell], Action):
    """
    Объедененный алгоритм E1+B1.
    Нужен для более "человеческой" игры - чтобы нажатия на клетки совершались кучно, а не вразброс по всему полю

    B1 - значит Bomb - ищем Бомбы алгоритомом "один"

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
    action_b1 = Action.set_flag

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

        distance_b1 = matrix.cell_distance(cells_b1[0], matrix.lastclicked)
    else:
        distance_b1 = 0

    #
    # E1 part
    #

    cells_e1 = []
    action_e1 = Action.open_digit

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

        distance_e1 = matrix.cell_distance(solution_e1[0], matrix.lastclicked)

        if config.noflag:
            # todo тут говно код... Завязана логика поиска решений на тип игры (noflag)
            solution_e1 = matrix.around_closed_cells(solution_e1[0])
            distance_e1 = matrix.cell_distance(solution_e1[0], matrix.lastclicked)
            action_e1 = Action.open_cell

        # if config.turn_by_turn:
        #     ic('------ E1')
        #     ic(solution)
        #     solution.mark_cell_debug()
    else:
        # если ни у одной клетки нет решения, возвращаем пустой список
        solution_e1 = []
        distance_e1 = 0

    #
    # Выбираем, что возвращать
    #

    # - debug
    # matrix.lastclicked.mark_cell_debug('magenta')
    # for cc in cells_b1:
    #     cc.mark_cell_debug('red')
    # for cc in cells_e1:
    #     cc.mark_cell_debug('yellow')
    # print(f'cells B1: <{dist_b1}> {cells_b1}')
    # print(f'cells E1: <{dist_e1}> {cells_e1}')
    # - end debug

    # todo говно код, но лучше ничего не придумал.
    if distance_b1 == 0 and distance_e1 == 0:
        c, b = [], None
    elif distance_b1 > 0 and distance_e1 == 0:
        c, b = cells_b1[0:1], action_b1
    elif distance_b1 == 0 and distance_e1 > 0:
        c, b = solution_e1, action_e1
    elif distance_b1 > distance_e1:
        c, b = solution_e1, action_e1
    else:
        c, b = cells_b1[0:1], action_b1

    # if c:
    #     c[0].mark_cell_debug('green', dist=12, size=12)
    # print(f'Result: {b} on {c}\n')
    return c, b







