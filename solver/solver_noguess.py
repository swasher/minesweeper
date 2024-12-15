from asset import Asset
import maus


def solver_noguess(matrix):
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
    return x_cell, maus.OPEN
