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
    # mine code
    # · = blank; ⚑ = mine; × = unknown; N = count
    # minesweepr
    # . = blank; * = mine; x = unknown; N = count

    replace_dict = {
        '·': '.',  # blank
        '⚑': '*',  # mine
        '×': 'x',  # unknown
        ' ': '',  # пробел заменяется на пустую строку
    }

    # transformed_matrix = []
    # for line in matrix_ascii:
    #     line.replace(' ', '')
    #     for old_char, new_char in replace_dict.items():
    #         line = line.replace(old_char, new_char)
    #     transformed_matrix.append(line)
    # return transformed_matrix

    # Лямбда-функция для замены символов в строке
    transform_line = lambda line: ''.join(
        replace_dict.get(char, char) for char in line
    )

    # Применяем transform_line к каждой строке матрицы
    return '\n'.join(map(transform_line, matrix_ascii))

def solver(matrix: Matrix):
    matrix_ascii = matrix.to_text()
    converted_ascii = transformer_ascii(matrix_ascii)

    total_mines = matrix.get_num_mined()
    total_mines = 2

    b = Board(converted_ascii)
    r = generate_rules(b, total_mines=total_mines)
    rules = r[0]
    mine_prevalence = r[1]
    solution = solve(rules=rules, mine_prevalence=mine_prevalence)
    print(solution)
