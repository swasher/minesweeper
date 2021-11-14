def noguess_finish(matrix):
    """
    Если не осталось ходов, то нужно закончить игру, чтобы не зацикливалось.
    Применяется в игре без угадываения.
    :return:
    """
    print('No_guess: No more turn')
    return [], ''
