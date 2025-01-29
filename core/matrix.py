import math
import numpy as np
from abc import abstractmethod

from assets import *

from .cell import Cell
from .utility import GameState, MineMode
from .matrix_io import MatrixIO

from minesweepr import solver

"""
Соглашения:
get_closed - возвращает только закрытые и НЕ отмеченные флагами
"""


class Matrix:
    """
    Описывает набор ячеек игрового поля и реализует логику.
    Экземпляр этого класса можно использовать для тестирования алгоритмов.
    От Matrix наследуются: Tk-версия (TkMatrix) и экранная версия (ScreenMatrix)
    """
    def __init__(self, width: int = 0, height: int = 0, total_mines: int = 0):
        self.io = MatrixIO(self)
        self.width = width   # height of matrix (number of rows)
        self.height = height  # width of matrix (number of cols)
        self.total_mines: int = total_mines  # общее кол-во мин. Берется либо из LED-индикатора при старте игры (screen), либо из данных об игре (Tk), либо из файла загрузки.

        self.table = np.full((height, width), Cell)  # matrix itself; numpy 2D array of Cell object
        self._game_state: GameState = GameState.waiting
        self._mine_mode = MineMode.UNDEFINED

        # TODO Переместить эти две строчки в PlayMatrix? с одной стороны, известные мины
        #  только в Playmatrix могут быть, с другой, у нас есть методы, которые используют мины и находятся в Matrix


    def save(self):
        text = self.to_text()
        self.io.save(text)

    def load(self, file_path: str):
        """
        Возвращаем solution, это используется в тестах солверов на паттернах.
        """
        solutions = self.io.load(file_path)
        return solutions

    @property
    def game_state(self) -> GameState:
        """
        GETTER. Возвращает текущее состояние игры.
        :return: GameState enum
        """
        return self._game_state

    @game_state.setter
    def game_state(self, state: GameState):
        """
        SETTER. Устанавливает состояние игры.
        :param state: GameState enum
        """
        self._game_state = state

    @property
    def mine_mode(self) -> MineMode:
        """ GETTER. Возвращает режим расположения мин """
        return self._mine_mode

    @mine_mode.setter
    def mine_mode(self, mode: MineMode):
        """SETTER. Устанавливает режим расположения мин"""
        self._mine_mode = mode

    @staticmethod
    def cell_distance(cell1: Cell, cell2: Cell) -> float:
        d = math.hypot(cell1.row - cell2.row, cell1.col - cell2.col)
        return d

    def to_text(self) -> list[str]:
        """
        Используется в методе сохранении матрицы в файл. В display() не используем, потому что немного другая логика.
        """
        matrix = []
        for row in range(self.height):
            line = ''
            for col in range(self.width):
                cell = self.table[row, col]
                line += cell.content.symbol
            line = ' '.join(line)
            matrix.append(line)
        return matrix

    def display(self):
        """
        Выводит в консоль текущее изображение поля (матрицу)
        Мы не можем тут использовать matrix_to_text, потому что та функция не показывает мины в матрице.
        :return: Возвращает матрицу типа array of strings
        """
        print('---DISPLAY---')

        if self.mine_mode == MineMode.PREDEFINED:
            matrix_view = [
                ' '.join(
                    there_is_bomb.symbol
                    if ((row, col) in self.mines and not self.table[row, col].is_flag)  # -> показываем мину, если по коорд. row, col находится мина И в ячейке нет флага
                    else self.table[row, col].content.symbol
                    for col in range(self.width))
                for row in range(self.height)
            ]
        else:
            matrix_view = [
                ' '.join(
                    self.table[row, col].content.symbol
                    for col in range(self.width))
                for row in range(self.height)
            ]
        print('\n'.join(matrix_view))
        return matrix_view

    def around_cells(self, cell: Cell) -> list[Cell]:
        """
        Returns a list of cells surrounding the given cell (including diagonals).
        Uses NumPy's capabilities to handle edge cases efficiently.

        Для ячейки в центре это будет 8 "соседей", для угловой - 3, для ячейки возле стенки - 5.

        Args:
            cell: Cell object with row and col attributes

        Returns:
            list[Cell]: List of neighboring cells
        """
        rows, cols = self.table.shape

        # Calculate valid row and column ranges
        row_start = max(0, cell.row - 1)
        row_end = min(rows, cell.row + 2)
        col_start = max(0, cell.col - 1)
        col_end = min(cols, cell.col + 2)

        # Get the subarray of neighboring cells
        neighbors = self.table[row_start:row_end, col_start:col_end]

        # Convert to flat list and remove the center cell
        cells = neighbors.flatten().tolist()
        center_idx = (cell.row - row_start) * (col_end - col_start) + (cell.col - col_start)
        cells.pop(center_idx)

        return cells

    def around_closed_cells(self, cell) -> list[Cell]:
        """
        Возвращает список закрытых ячеек вокруг ячейки cell.
        Флаги не считаются закрытыми ячейками.
        :param cell: instance of Cell class
        :return: array of Cell instances
        """
        closed_cells = list([x for x in self.around_cells(cell) if x.is_closed])
        return closed_cells

    def around_flagged_cells(self, cell) -> list[Cell]:
        """
        Возвращает список ячеек-флагов вокруг ячейки cell
        :param cell: instance of Cell class
        :return: array of Cell instances
        """
        flagged_cells = list([x for x in self.around_cells(cell) if x.is_flag])
        return flagged_cells

    def around_flagged_num(self, cell) -> int:
        """
        Возвращает количество ячеек-флагов вокруг ячейки cell
        :param cell: instance of Cell class
        :return: array of Cell instances
        """
        return len(self.around_flagged_cells(cell))

    def around_digit_cells(self, cell) -> list[Cell]:
        """
        Возвращает список ячеек-цифр вокруг ячейки cell
        :param cell: instance of Cell class
        :return: array of Cell instances
        """
        flagged_cells = list([x for x in self.around_cells(cell) if x.is_digit])
        return flagged_cells

    def around_opened_cells(self, cell) -> list[Cell]:
        """
        Возвращает список открытых ячеек вокруг ячейки cell.
        :param cell: instance of Cell class
        :return: array of Cell instances
        """
        flagged_cells = list([x for x in self.around_cells(cell) if x.is_open])
        return flagged_cells

    def around_mined_cells(self, cell) -> list[Cell]:
        """
        Возвращает список ячеек-мин вокруг ячейки cell.
        Используется для tk-версии с известно расположенными минами.
        :param cell: instance of Cell class
        :return: array of Cell instances
        """
        mines = list([x for x in self.around_cells(cell) if x.is_mined])
        return mines

    def around_mined_count(self, cell) -> int:
        """
        Возвращает количество ячеек-мин вокруг ячейки cell.
        Используется для tk-версии с известно расположенными минами.
        :param cell: instance of Cell class
        :return: int
        """
        return len(self.around_mined_cells(cell))

    def get_all_cells(self) -> list[Cell]:
        """
        Все ячейки в матрице
        """
        return self.table.flat

    def get_closed_cells(self) -> list[Cell]:
        """
        Возвращает все закрытые ячейки (которые закрыты и НЕ отмечены флагом)
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_closed])
        return cells

    @property
    def get_closed_cells_count(self) -> int:
        return len(self.get_closed_cells())

    def get_opened_cells(self) -> list[Cell]:
        """
        Возвращает все открытые ячейки (это цифры плюс пустая ячейка)
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_open])
        return cells

    @property
    def get_opened_cells_count(self) -> int:
        return len(self.get_opened_cells())

    def get_flagged_cells(self) -> list[Cell]:
        """
        Возвращает список закрытых ячеек, уже помеченных флагами
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_flag])
        return cells

    @property
    def get_flagged_cells_count(self) -> int:
        return len(self.get_flagged_cells())

    def get_digit_cells(self) -> list[Cell]:
        """
        Возвращает список открытых ячеек (без нулевых ячеек)
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_digit])
        return cells

    def get_open_cells(self) -> list[Cell]:
        """
        Возвращает список открытых ячеек (включая нули).
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_open])
        return cells

    ####################
    #   START BLOCK    #
    ####################

    # Все методы, связанные с минами, потому что с ними есть путаница.
    # Есть еще два метода (только для tk используются) - around_mined_cells и around_mined_num, сюда не переносил.

    def get_bombs_cells(self) -> list[Cell]:
        """
        Возвращает список бомб (которые видны, если игра окончена). Используется в game_over
        :return: array of Cell objects
        """
        cells = list([x for x in self.table.flat if x.is_bomb])
        return cells

    @abstractmethod
    def get_mined_cells(self) -> list[Cell]:
        """
        (TK only)
        Список всех мин.
        :return:
        """
        raise NotImplementedError("Метод get_mined_cells должен быть переопределен.")

    @property
    def get_total_mines(self) -> int:
        """
        Общее кол-во мин всех мин. Оно не меняется в процессе игры.
        А на LED индикаторе отображается "общее кол-во мин минус кол-во флагов" - это get_remaining_mines_count.
        """
        return self.total_mines

    @abstractmethod
    def get_remaining_mines(self) -> list[Cell]:
        """
        (TK only)
        Не уверен в необходимсти этого метода. Возвращает список нераскрытых мин (на которых нет флага).
        Returns:
        """
        raise NotImplementedError("Метод get_remaining_mines должен быть переопределен.")

    @property
    @abstractmethod
    def get_remaining_mines_count(self) -> int:
        """
        Кол-во мин минус кол-во флагов. Это число отображается на LED индикаторе.
        Реализация и смысл этого метода в screen и tk версиях совершенно различна.
        - В tk мы используем сами данные матрицы, чтобы получить значение led_mines и отобразить его на индикаторе,
        - В screen версии мы считываем индикатор, чтобы получить информацию о кол-ве мин,
        - в родительской Matrix мы можем знать кол-во оставшихся мин, если Матрица загружена из файла

        Но итог один - метод возвращает число мин на индикаторе.
        """
        return self.total_mines - self.get_num_flags

    ####################
    #    END BLOCK     #
    ####################

    def get_noguess_cell(self) -> list[Cell]:
        """
        Первый ход для no-guess игр. Возвращает отмеченную крестиком клетку.
        Для совместимости в виде списка.
        :return: list of Cell objects
        """
        cell = list([x for x in self.table.flat if x.is_noguess])
        return cell

    @property
    def get_num_closed(self) -> int:
        """
        Кол-во закрытых ячеек (флаг не считается закрытой ячейкой!)
        """
        return len(self.get_closed_cells())

    @property
    def get_num_flags(self) -> int:
        """
        Кол-во установленных флагов
        """
        return len(self.get_flagged_cells())

    @property
    def you_fail(self) -> bool:
        """
        Если в матрице есть бомбы - то FAIL (бомбы - это открытое изображение бомбы после проигрыша)
        :return:
        """
        revealed_bombs = self.get_bombs_cells()
        if len(revealed_bombs):
            self.game_state = GameState.fail
            return True

    @property
    @abstractmethod
    def you_win(self) -> bool:
        """
        Имплементируется по-разному в Tk и в экранной версии.
        """
        raise NotImplementedError("Метод you_win должен быть переопределен в дочернем классе.")

    def fill_with_closed(self):
        for c in self.table.flat:
            c.content = closed

    def solve(self):
        """
        Рассчитывает матрицу с помощью алгоритмов minesweepr.
        У каждой ячейки заполняется свойство probability соответствующей вероятностью появления
        мины (float 0..1, 1 = мина, 0 = нет мины)

        Returns: None
        """
        solver(self)
