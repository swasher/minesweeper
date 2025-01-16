"""
Абстрагирует логику записи/чтения в файл от логики преобразования матрицы в текст и обратно


Режимы:
- PREDEFINED - матрица знает о расположении мин (для Tk)
- UNDEFINED - матрица не знает о расположении мин (для Tk и экранной версии)

× - закрытая клетка
⚑ - флаг
· - открытая клетка (0)
1-8 - открытая клетка с цифрой

Формат:

[properties]
width = 8
height = 8
mine_mode = PREDEFINED | UNDEFINED

[matrix]
· · · · · ⚑ × × ×
· · · · · ⚑ × × ×
· 1 1 1 · ⚑ × × ×
· 1 ⚑ ⚑ ⚑ × × × ×
· 1 1 2 × × × × ×
· · · 1 × × × × ×
· · · 1 × × × × ×
× · · · × × × × ×
× × × × × × × × ×

[mines]
MINE 0 7
MINE 6 5
MINE 5 4
MINE 6 8
MINE 5 6
MINE 3 2

[solutions]
MINE 4 5
EMPTY 0 0
"""

import os
import numpy as np
from datetime import datetime

from .utility import MineMode
from .cell import Cell
from config import config
from assets import *





# def save_coordinates(filename, coordinates):
#     """
#     Сохраняет координаты в текстовый файл.
#     :param filename: Имя файла для сохранения.
#     :param coordinates: Словарь координат, где ключ — кортеж (x, y), значение — тип ('EMPTY' или 'MINE').
#     """
#     with open(filename, 'w') as file:
#         # Записываем заголовки разделов
#         file.write("[properties]\n")
#         file.write("<some data>\n\n")  # Пример данных для раздела properties
#
#         file.write("[matrix]\n")
#         file.write("<some data>\n\n")  # Пример данных для раздела matrix
#
#         # Записываем координаты в раздел solution
#         file.write("[solution]\n")
#         for (x, y), type in coordinates.items():
#             file.write(f"{type} {x} {y}\n")  # Тип на первом месте, затем координаты

# def load_coordinates(filename):
#     """
#     Загружает координаты из текстового файла.
#     :param filename: Имя файла для загрузки.
#     :return: Два списка координат: empty_coords и mine_coords.
#     """
#     empty_coords = []
#     mine_coords = []
#     with open(filename, 'r') as file:
#         lines = file.readlines()
#
#         # Ищем начало раздела [solution]
#         solution_started = False
#         for line in lines:
#             line = line.strip()  # Убираем лишние пробелы и переносы строк
#             if line == "[solution]":
#                 solution_started = True
#                 continue  # Пропускаем строку с заголовком раздела
#
#             if solution_started and line:  # Если раздел начался и строка не пустая
#                 type, x, y = line.split()  # Разделяем строку по пробелам
#                 if type == "EMPTY":
#                     empty_coords.append((int(x), int(y)))
#                 elif type == "MINE":
#                     mine_coords.append((int(x), int(y)))
#
#     return empty_coords, mine_coords

# Пример использования
# coordinates = {
#     (3, 5): 'EMPTY',
#     (0, 0): 'MINE',
#     (4, 0): 'MINE'
# }

# Сохраняем координаты в файл
# save_coordinates('game_coords.txt', coordinates)

# Загружаем координаты из файла
# empty_coords, mine_coords = load_coordinates('game_coords.txt')
# print("EMPTY:", empty_coords)
# print("MINE:", mine_coords)





class MatrixIO:
    def __init__(self, matrix):
        self.matrix = matrix
        pass

    def save(self, matrix_text: list[str]):
        """
        Сохраняет Матрицу в текстовый файл.
        """
        save_dir = config.save_dir
        file_name = 'save_' + datetime.now().strftime("%d-%b-%Y--%H.%M.%S.%f") + '.txt'
        file_path = os.path.join(save_dir, file_name)

        mine_mode = self.matrix.mine_mode
        width = self.matrix.width
        height = self.matrix.height

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        with open(file_path, 'w', encoding='utf-8') as outp:

            # Записываем секцию матрицы
            outp.write("[properties]\n")
            outp.write(f"width = {width}\n")
            outp.write(f"height = {height}\n")
            outp.write(f"mode = {mine_mode.name}\n")

            outp.write("\n[matrix]\n")
            outp.write('\n'.join(matrix_text) + '\n')

            outp.write("\n[mines]\n")
            if mine_mode == MineMode.PREDEFINED:
                for mine in self.matrix.mines:
                    outp.write(f"MINE {mine[0]} {mine[1]}\n")

            outp.write("\n[solution]")
        print('Matrix saved to', file_path)

    def load(self, file_path: str):
        """
        Загружает Матрицу из текстового файла.

        Args:
            file_path (str): Путь к файлу сохранения

        Returns:
            None

        Raises:
            FileNotFoundError: Если файл не найден
            ValueError: Если формат файла некорректен
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Save file not found: {file_path}")

        # Словарь для обратного преобразования: буква -> asset
        symbol_to_asset = {
            closed.symbol: closed,
            flag.symbol: flag,
            there_is_bomb.symbol: there_is_bomb,
            bomb_wrong.symbol: bomb_wrong,
        }

        # Добавляем цифры от 0 до 8
        for i, digit_asset in enumerate(open_cells):
            symbol_to_asset[digit_asset.symbol] = digit_asset

        current_section = None
        matrix_data = []
        solution_empty_coords = []
        solution_mine_coords = []
        mines = set()

        with open(file_path, 'r', encoding='utf-8') as inp:
            for line in inp:
                line = line.strip()

                # Пропускаем пустые строки
                if not line:
                    continue

                # Обработка заголовков секций
                if line.startswith('[') and line.endswith(']'):
                    current_section = line[1:-1]
                    continue

                if current_section == 'properties':
                    key, value = line.split(' = ')
                    if key == 'width':
                        self.width = int(value)
                    elif key == 'height':
                        self.height = int(value)
                    elif key == 'mode':
                        if value in ['PREDEFINED', 'UNDEFINED']:
                            loaded_mine_mode = MineMode[value]
                        else:
                            raise ValueError(f"Invalid mode: {value}")

                elif current_section == 'matrix':
                    # Убираем пробелы между символами, если они есть
                    line = ''.join(line.split())
                    matrix_data.append(line)

                elif current_section == 'mines':
                    line = line.strip()  # Убираем лишние пробелы и переносы строк
                    type, x, y = line.split()  # Разделяем строку по пробелам
                    mines.add((int(x), int(y)))

                elif current_section == 'solution':
                    # reserved for future use
                    ...

                    # empty_coords = []
                    # mine_coords = []
                    # with open(filename, 'r') as file:
                    #     lines = file.readlines()
                    #
                    #     # Ищем начало раздела [solution]
                    #     solution_started = False
                    #     for line in lines:
                    line = line.strip()  # Убираем лишние пробелы и переносы строк

                    type, x, y = line.split()  # Разделяем строку по пробелам
                    if type == "EMPTY":
                        solution_empty_coords.append((int(x), int(y)))
                    elif type == "MINE":
                        solution_mine_coords.append((int(x), int(y)))


        # Инициализируем матрицу
        self.matrix.width = self.width
        self.matrix.height = self.height
        self.matrix.table = np.full((self.height, self.width), Cell)
        self.matrix.mines = mines.copy()
        self.matrix.mine_mode = loaded_mine_mode

        # Заполняем матрицу данными
        for row in range(self.height):
            for col in range(self.width):
                symbol = matrix_data[row][col]
                cell = Cell(self.matrix, row=row, col=col)

                # Конвертируем символ в asset
                if symbol not in symbol_to_asset:
                    raise ValueError(f"Unknown symbol in save file: {symbol}")
                cell.content = symbol_to_asset[symbol]
                self.matrix.table[row, col] = cell

        print(f'Matrix loaded from {file_path}')
        self.matrix.display()

    def write_save(self, text_matrix: list[str]) -> bool:
        ok = True
        return ok

    def read_save(self) -> str:
        matrix_text = None
        matrix_width = None
        matrix_height = None
        solutions_mines = None
        solutions_empty = None
