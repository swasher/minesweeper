import itertools
from solver.classes import create_roots

from classes import Action
from cell import Cell


def solver_E2(matrix, debug=False) -> ([Cell], Action):
    """
    - Для каждой цифры делаем список закрытых ячеек вокруг (Root.closed)
    - При этом нужно из цифры вычесть кол-во имеющихся вокруг флагов  (Root.rest_bomb)
    - Сравниваем каждый список с каждым. Ищем вхождение одного списка в другой.
    - Если при этом цифры одинаковые (с учетом вычета флагов), то все "лишние" ячейки - пустые (их может быть более 1-й)

    На "цифры" влияют флаги - т.е. цифру нужно считать как 'цифра минус флаги вокруг', см. пример solver_e2_2 (п.2)
    :param matrix:
    :return:
    """
    action = Action.open_cell
    roots = create_roots(matrix)
    solution = []

    for r1, r2 in itertools.combinations(roots, 2):

        set1 = set(r1.closed)
        set2 = set(r2.closed)
        if set1.issubset(set2) or set2.issubset(set1):
            if r1.rest_bombs == r2.rest_bombs:
                empties = tuple(set(r1.closed) ^ set(r2.closed))

                # -- debug
                if debug:
                    r1.ancestor.mark_cell_debug('yellow')
                    r2.ancestor.mark_cell_debug('green')
                    print('-----')
                    print('COMPARE:', r1.ancestor, 'and', r2.ancestor)
                    print('EMPTIES:', empties)
                # -- debug

                return empties, action
                # VAR1 - return all found solution
                #solution += empties

    # VAR1 - return all found solution
    # return solution, Asset.open
    return [], action
