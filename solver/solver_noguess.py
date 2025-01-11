from classes import Action
from classes import Cell


def solver_noguess(matrix) -> ([Cell], Action):
    """
    Первый ход для no-guess игр. Это когда игра помечает крестиком хороший первый ход.
    Нажимает отмеченную крестиком клетку.
    Этот солвер `должен` вернуть X клетку, если не вернул, значит возникла ошибка.
    :param matrix:
    :return:
    """
    x_cell = matrix.get_noguess_cell()
    if not len(x_cell):
        raise Exception('Error in solver_noguess function! Не найден крест в режиме NG!!!')
    return x_cell, Action.open_cell
