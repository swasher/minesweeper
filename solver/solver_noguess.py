from asset import Asset


def solver_noguess(matrix):
    """
    Первый ход для no-guess игр.
    Нажимает отмеченную крестиком клетку.
    Этот солвер `должен` вернуть X клетку, если нет, значит что-то пошло не так
    :param matrix:
    :return:
    """
    x_cell = matrix.get_noguess_cell()
    if not len(x_cell):
        raise Exception('Error in solver_noguess function! Не найден крест в режиме NG!!!')
    return x_cell, Asset.open





