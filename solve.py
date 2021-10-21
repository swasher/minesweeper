import icecream
from random import randrange
from util import remove_dup


def solver_R1(matrix):
    """
    Нажимает рандомную клетку из закрытых.
    TODO Нужно научить считать ВЕРОЯТНОСТИ ДЛЯ КЛЕТОК!!!!!
    :param matrix:
    :return:
    """
    cells = matrix.get_closed_cells()
    qty = len(cells)
    random_cell = cells[randrange(qty)]
    return [], [random_cell]


def solver_B1(matrix):
    """
    B1 - значит ищем Bомбы алгоритомом "один"
    :param matrix:
    :return: list of cells (bomb) and empty list (for clear cells)

    Алгоритм:
    Проверяем все ячейки с цифрами.
    Если цифра в ячейке равно кол-ву соседних закрытых клеток,
    ТО все эти клетки - бомбы
    """

    """
    оно не считает уже отмеченные бомбы,
    и получается, что если вокруг "1" две закрытые клетки, и одна из
    них уже бомба, то оставшуюся единственной клеткой вокруг "1", 
    и соотв. тоже помечает ее бомбой.
    """

    bomb_cells = []
    for cell in matrix.number_cells():
        cells = matrix.around_closed_cells(cell)
        if cell.number == len(cells):
            # значит во всех клетках cells есть бомбы
            bomb_cells += cells
    bomb_cells = remove_dup(bomb_cells)
    return bomb_cells, []


def solver_E1(matrix):
    """
    E1 значит Empty - ищем потенчиально пустые ячейки алгоритмом "один"
    :return: empty list of cells (bombs) and list for empty cells

    Алгоритм:
    Проверяем все ячейки с цифрами.
    Если вокруг ячейки с цифрой такое же кол-во флагов, и вокруг есть закрытые
    ячейки, ТО все закрытые ячейки являются пустыми
    """
    empty_cells = []
    for cell in matrix.number_cells():
        flags = matrix.around_flagged_cells(cell)
        if cell.number == len(flags):
            empties = matrix.around_closed_cells(cell)
            empty_cells += empties
    empty_cells = remove_dup(empty_cells)
    return [], empty_cells
