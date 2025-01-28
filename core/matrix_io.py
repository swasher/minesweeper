"""
Абстрагирует логику записи/чтения в файл от логики преобразования матрицы в текст и обратно

Комментарии:
; строка

Режимы:
- PREDEFINED - матрица знает о расположении мин (для Tk)
- UNDEFINED - матрица не знает о расположении мин (для Tk и экранной версии)

Символы ячеек:
× - закрытая клетка
⚑ - флаг
· - открытая клетка (0)
1-8 - открытая клетка с цифрой

Мины:
Каждая мина начинается со слова MINE, и далее строка и столбец.

Решения:
Строки вида: CELL 2 2 MINE 0.5
Первые два числа - это ячейка, а после слова PROB - вероятность мины, float (0-мины точно нет, 1-мина точно есть)

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
CELL 4 5 PROB 1
"""

import os
import numpy as np
from datetime import datetime

from .utility import MineMode
from .cell import Cell
from config import config
from assets import *


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
        remaining_mines = self.remaining_mines

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        with open(file_path, 'w', encoding='utf-8') as outp:

            # Записываем секцию матрицы
            outp.write("[properties]\n")
            outp.write(f"width = {width}\n")
            outp.write(f"height = {height}\n")
            outp.write(f"remaining_mines = {remaining_mines}\n")
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
        solutions = []
        mines = set()

        with open(file_path, 'r', encoding='utf-8') as inp:
            for line in inp:
                line = line.strip()

                # Пропускаем пустые строки
                if not line:
                    continue

                # Обработка комментариев
                if line.startswith(';'):
                    print(f'- {line[1:].strip()} -')
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
                    elif key == 'remaining_mines':
                        # TODO У объекта Matrix я не делал такого свойства, remaining_mines - нужно подумать, где хранить эту цифру
                        #  можно добавить к нему кол-во флагов и записать в self.total_mines, как вариант.
                        self.remaining_mines_variable = int(value)
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
                    keyword, x, y = line.split()  # Разделяем строку по пробелам
                    assert keyword == 'MINE', 'Wrong MINE keyword in txt'
                    mines.add((int(x), int(y)))

                elif current_section == 'solution':
                    line = line.strip()  # Убираем лишние пробелы и переносы строк

                    line_values = line.split()  # Разделяем строку по пробелам
                    # проверяем корректность синтаксиса
                    if len(line_values) != 5 or line_values[0] != "CELL" or line_values[3] != "PROB":
                        raise Exception(f"Неверный формат файла {file_path}")
                    _, x, y, _, probability = line_values
                    try:
                        solutions.append((int(x), int(y), float(probability)))
                    except ValueError:
                        print(f"Ощибка чтения решения: {file_path}")

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
        return solutions  # todo Это факен шайзе, возвращать тут solution.
