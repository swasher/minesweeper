"""
ПРОСЛОЙКА МЕЖДУ МОИМИ КЛАССАМИ И MINESWEEPR
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from rich import print
from .minesweeper_util import Board
from .minesweeper_util import generate_rules
from .minesweeper import solve

from exceptions import InvalidCharacterError

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
        '░': 'x',  # unknown
        #'×': 'x',  # unknown
        ' ': '',  # пробел заменяется на пустую строку
    }
    # print("matrix_ascii:", matrix_ascii)

    for i, string in enumerate(matrix_ascii):
        for char in string:
            if char not in replace_dict and char not in '0123456789':
                raise InvalidCharacterError(f"Недопустимый символ: '{char}' в строке {i + 1}: '{string}'.")

    # Лямбда-функция для замены символов в строке
    transform_line = lambda line: ''.join(
        replace_dict.get(char, char) for char in line
    )

    # Применяем transform_line к каждой строке матрицы
    return '\n'.join(map(transform_line, matrix_ascii))


def solver(matrix: Matrix):
    # Очищаем вероятности
    for i in matrix.get_all_cells():
        i.probability = None

    matrix_ascii = matrix.to_text()
    try:
        converted_ascii = transformer_ascii(matrix_ascii)
    except InvalidCharacterError:
        # В некоторых случаях, например по окончанию игры, матрица может содержать символы, которых нет
        # в словаре, например, изображение бомбы, тогда просто выходим и оставляем значения вероятностей в Cell пустыми.
        print('FOUND INVALID CHARACTER!')
        return

    # В солвер нужно передевать общее кол-во мин на поле - то есть remaining + flags
    total_mines = matrix.get_remaining_mines_count + matrix.get_num_flags
    # print("Total mines -> solver:", total_mines)
    print('Remain:', matrix.get_remaining_mines_count)

    # print('converted_ascii:')
    # print(converted_ascii)
    # print('\n')

    b = Board(converted_ascii)
    r = generate_rules(b, total_mines=total_mines)
    rules = r[0]
    mine_prevalence = r[1]
    # mine_prevalence = 0.1  Если кол-во мин неизвестно, тогда можно назначить фиксированную вероятность для всех недоступных рассчету ячеект.

    solution = solve(rules=rules, mine_prevalence=mine_prevalence)

    if False:
        sorted_solution = dict(sorted((k, v) for k, v in solution.items() if k is not None))
        print("Solution:", sorted_solution)
        # like {'2-2': 0.5, '2-4': 0.5, '2-1': 0.5, '2-5': 0.5, '2-3': 0.0, None: 0.0}

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
