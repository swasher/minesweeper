import sys
from config import config
from pathlib import Path
from solver import solver_E2
from classes import Matrix


def solve(algo, pattern):
    """
    Test solve engine on saved board
    :return:
    """
    file_exercise = Path(__file__).parent / config.patterns_dir / pattern

    matrix = Matrix(0, 0)
    matrix.load(file_path=file_exercise)

    cells, button = algo(matrix)
    print('Cells', cells)
    print('Button', button)


if __name__ == '__main__':
    algo = solver_E2
    pattern = "5x5_E1_1.txt"

    if len(sys.argv) < 3:
        print("Not enough arguments")
    else:
        action = sys.argv[1]
        if action == 'solve':
            pattern = sys.argv[2]
            solve(algo, pattern)
