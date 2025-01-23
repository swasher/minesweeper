import sys
from config import config
from pathlib import Path
from solver import solver_E2_new
from core import Matrix


def solve(algo, pattern):
    """
    Testing solve engine on saved board
    :return:
    """
    pattern_file = Path(__file__).parent / config.patterns_dir / pattern

    matrix = Matrix(0, 0)
    solutions = matrix.load(file_path=pattern_file)

    print(f'Solutions: {solutions}')

    turns = algo(matrix)
    print(f'Len: {len(turns)}')
    for turn in turns:
        print(f'Cell {turn.cell}, mines: {turn.probability}')

    # Теперь нужно как-то заценить соответствие solution найденным turns.
    # Во первых, их кол-во может отличаться. То есть солвер может найти больше решений, чем задано в solution, это не обязательно ошибка.
    # И наоборот - некий солвер может найти меньше решений, если спикок решений предполагал более мощный солвер.
    #  НО! Если мы предлоложим, что у нас известный солвер, - ну то есть данная матрица и ее ответы рассчитаны на E2, то можно предполагать,
    # что ответы должны сойтись.


if __name__ == '__main__':
    algo = solver_E2_new
    pattern = "5x5_E1_1.txt"

    if len(sys.argv) < 3:
        print("Not enough arguments (for example, '5x5_E1_1.txt')")
    else:
        action = sys.argv[1]
        if action == 'solve':
            pattern = sys.argv[2]

            solve(algo, pattern)
