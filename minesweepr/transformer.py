"""
ПРОСЛОЙКА МЕЖДУ МОИМИ КЛАССАМИ И MINESWEEPR
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from rich import print
from .minesweeper_util import Board
from .minesweeper_util import generate_rules
from .minesweeper import solve

if TYPE_CHECKING:
    from core import Matrix


def transformer_ascii(matrix_ascii: list[str]) -> str:
    # my codes
    # · = blank; ⚑ = mine; × = unknown; N = count
    # minesweepr codes
    # . = blank; * = mine; x = unknown; N = count

    replace_dict = {
        '·': '.',  # blank
        '⚑': '*',  # mine
        '×': 'x',  # unknown
        ' ': '',  # пробел заменяется на пустую строку
    }

    # Лямбда-функция для замены символов в строке
    transform_line = lambda line: ''.join(
        replace_dict.get(char, char) for char in line
    )

    # Применяем transform_line к каждой строке матрицы
    return '\n'.join(map(transform_line, matrix_ascii))


def solver(matrix: Matrix):
    matrix_ascii = matrix.to_text()
    converted_ascii = transformer_ascii(matrix_ascii)

    total_mines = matrix.get_num_mined() + matrix.get_num_flags
    print("Total mines: ", total_mines)

    b = Board(converted_ascii)
    r = generate_rules(b, total_mines=total_mines)
    rules = r[0]
    mine_prevalence = r[1]
    solution = solve(rules=rules, mine_prevalence=mine_prevalence)
    # print(solution)

    for i in matrix.get_all_cells():
        i.probability = None

    # {'2-2': 0.5, '2-4': 0.5, '2-1': 0.5, '2-5': 0.5, '2-3': 0.0, None: 0.0}
    for k, v in solution.items():
        if k is None:
            pass  # Значит v это вероятность для всех клеток, возле которых нет цифр
            continue

        row, col = tuple([int(x) for x in k.split('-')])
        row, col = row - 1, col - 1
        matrix.table[row, col].probability = v

    # Все ячейки, которые не получили свою вероятность, заполняются дефолтной вероятностью.
    # Это ячейки, возле которых нет цифр
    for cell in matrix.get_closed_cells():
        if cell.probability is None:
            cell.probability = float(solution[None])
